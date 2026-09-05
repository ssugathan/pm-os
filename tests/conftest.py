"""Shared test helpers."""

from __future__ import annotations

import json
from pathlib import Path


def read_events(base_dir: Path) -> list[dict]:
    """Read the telemetry events emitted under base_dir during a test."""
    path = base_dir / "_system" / "telemetry" / "events.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]
