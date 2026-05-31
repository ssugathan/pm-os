"""Telemetry module tests — payload shape, env overrides, append semantics."""

from __future__ import annotations

import json
from pathlib import Path

from pmos import telemetry


def read_events(base_dir: Path) -> list[dict]:
    path = base_dir / "_system" / "telemetry" / "events.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def test_event_writes_jsonl_line(tmp_path: Path):
    telemetry.event("test.thing", {"count": 1}, base_dir=tmp_path)
    events = read_events(tmp_path)
    assert len(events) == 1
    assert events[0]["event"] == "test.thing"
    assert events[0]["properties"]["count"] == 1


def test_event_payload_matches_posthog_shape(tmp_path: Path):
    telemetry.event("test.shape", {"foo": "bar"}, base_dir=tmp_path)
    e = read_events(tmp_path)[0]
    assert set(e.keys()) == {"event", "distinct_id", "properties"}
    assert "timestamp" in e["properties"]
    assert e["distinct_id"] == "pm_os_user"  # default


def test_distinct_id_env_override(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PMOS_DISTINCT_ID", "sid")
    telemetry.event("test.id", {}, base_dir=tmp_path)
    assert read_events(tmp_path)[0]["distinct_id"] == "sid"


def test_telemetry_path_env_override(tmp_path: Path, monkeypatch):
    custom = tmp_path / "elsewhere" / "events.jsonl"
    monkeypatch.setenv("PMOS_TELEMETRY_PATH", str(custom))
    telemetry.event("test.path", {}, base_dir=tmp_path)
    assert custom.exists()
    # Default path should NOT have been written
    assert not (tmp_path / "_system" / "telemetry" / "events.jsonl").exists()


def test_multiple_events_append(tmp_path: Path):
    for i in range(5):
        telemetry.event("test.append", {"i": i}, base_dir=tmp_path)
    events = read_events(tmp_path)
    assert len(events) == 5
    assert [e["properties"]["i"] for e in events] == [0, 1, 2, 3, 4]


def test_event_without_properties(tmp_path: Path):
    telemetry.event("test.empty", base_dir=tmp_path)
    e = read_events(tmp_path)[0]
    assert e["event"] == "test.empty"
    assert "timestamp" in e["properties"]
