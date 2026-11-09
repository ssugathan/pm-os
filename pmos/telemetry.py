"""Telemetry — thin wrapper for event emission.

v1 backend: append-only jsonl at `_system/telemetry/events.jsonl`.
v2 backend: PostHog (swap _emit_jsonl for _emit_posthog; call sites unchanged).

Payload shape matches PostHog's `capture` format (event / distinct_id / properties)
so the swap is one file. The owner using PM OS is the first live "user" — these
events are the audit trail for tuning the system based on real usage.

Discipline: METADATA ONLY. Track names, counts, durations, models, prompt SHAs,
error types. Never track prompt contents, agent outputs, or any artifact body.
That stays in the agent state file (source of truth, local).

Failure handling: `event()` never raises. A failed write prints one warning
line to stderr and the event is dropped (not retried or buffered).

Environment overrides:
- PMOS_TELEMETRY_PATH — full path to the events log (default: <base_dir>/_system/telemetry/events.jsonl)
- PMOS_DISTINCT_ID — distinct_id for PostHog forward-compat (default: pm_os_user)
- PMOS_TELEMETRY_BACKEND — jsonl | posthog (default: jsonl; posthog not yet wired)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_DEFAULT_DISTINCT_ID = "pm_os_user"


def event(
    name: str,
    properties: dict[str, Any] | None = None,
    *,
    base_dir: Path | None = None,
) -> None:
    """Record a telemetry event. Metadata only — never include content.

    Best-effort: telemetry is an audit trail, not the source of truth (agent
    state files are). Any failure to build or write the event is reported on
    stderr and swallowed, so it can never abort a run or replace the exception
    of a failing sub-task or agent that is being recorded.
    """
    try:
        payload = {
            "event": name,
            "distinct_id": os.environ.get("PMOS_DISTINCT_ID", _DEFAULT_DISTINCT_ID),
            "properties": {
                "timestamp": datetime.now(UTC).isoformat(),
                **(properties or {}),
            },
        }
        _emit(payload, base_dir=base_dir)
    except Exception as e:  # deliberately broad, see docstring
        print(
            f"pmos telemetry: dropped event {name!r} ({type(e).__name__}: {e})",
            file=sys.stderr,
        )


def _emit(payload: dict, *, base_dir: Path | None = None) -> None:
    # jsonl is the only backend so far. When PMOS_TELEMETRY_BACKEND selects the
    # (not yet wired) posthog backend, or anything unknown, fall through to
    # jsonl rather than silently dropping events. v2: dispatch on the env var
    # once a PostHog client exists.
    _emit_jsonl(payload, base_dir=base_dir)


def _emit_jsonl(payload: dict, *, base_dir: Path | None = None) -> None:
    path = _log_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(payload) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _log_path(base_dir: Path | None = None) -> Path:
    if override := os.environ.get("PMOS_TELEMETRY_PATH"):
        return Path(override)
    base = Path(base_dir) if base_dir else Path.cwd()
    return base / "_system" / "telemetry" / "events.jsonl"
