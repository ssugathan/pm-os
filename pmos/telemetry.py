"""Telemetry — thin wrapper for event emission.

v1 backend: append-only jsonl at `_system/telemetry/events.jsonl`.
v2 backend: PostHog (swap _emit_jsonl for _emit_posthog; call sites unchanged).

Payload shape matches PostHog's `capture` format (event / distinct_id / properties)
so the swap is one file. Sid using PM OS himself is the first live "user" — these
events are the audit trail for tuning the system based on real usage.

Discipline: METADATA ONLY. Track names, counts, durations, models, prompt SHAs,
error types. Never track prompt contents, agent outputs, or any artifact body.
That stays in the agent state file (source of truth, local).

Environment overrides:
- PMOS_TELEMETRY_PATH — full path to the events log (default: <base_dir>/_system/telemetry/events.jsonl)
- PMOS_DISTINCT_ID — distinct_id for PostHog forward-compat (default: pm_os_user)
- PMOS_TELEMETRY_BACKEND — jsonl | posthog (default: jsonl; posthog not yet wired)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_DISTINCT_ID = "pm_os_user"


def event(
    name: str,
    properties: dict[str, Any] | None = None,
    *,
    base_dir: Path | None = None,
) -> None:
    """Record a telemetry event. Metadata only — never include content."""
    payload = {
        "event": name,
        "distinct_id": os.environ.get("PMOS_DISTINCT_ID", _DEFAULT_DISTINCT_ID),
        "properties": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(properties or {}),
        },
    }
    _emit(payload, base_dir=base_dir)


def _emit(payload: dict, *, base_dir: Path | None = None) -> None:
    backend = os.environ.get("PMOS_TELEMETRY_BACKEND", "jsonl")
    if backend == "jsonl":
        _emit_jsonl(payload, base_dir=base_dir)
    elif backend == "posthog":
        # v2: PostHog client goes here. Until then, fall through to jsonl rather
        # than silently dropping events.
        _emit_jsonl(payload, base_dir=base_dir)
    else:
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
