"""State machine + state file management tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from pmos.state import (
    AgentRunState,
    OrchestratorState,
    SubTaskRecord,
    SubTaskStatus,
    TaskState,
    atomic_write_json,
    read_json,
)


def test_agent_run_state_roundtrip(tmp_path: Path):
    state = AgentRunState(
        agent_name="research",
        run_id="r1",
        task_state=TaskState.RUNNING,
        sub_tasks=[
            SubTaskRecord(
                name="scope",
                status=SubTaskStatus.COMPLETE,
                prompt_sha="abc123",
                prompt_dirty=False,
                output={"a": 1},
            ),
            SubTaskRecord(name="search", status=SubTaskStatus.PENDING),
        ],
        inputs={"problem": "foo"},
    )
    state.save(tmp_path)

    loaded = AgentRunState.load(tmp_path, "research", "r1")
    assert loaded.agent_name == "research"
    assert loaded.task_state == TaskState.RUNNING
    assert len(loaded.sub_tasks) == 2
    assert loaded.sub_tasks[0].status == SubTaskStatus.COMPLETE
    assert loaded.sub_tasks[0].prompt_sha == "abc123"
    assert loaded.sub_tasks[0].output == {"a": 1}
    assert loaded.sub_tasks[1].status == SubTaskStatus.PENDING
    assert loaded.inputs == {"problem": "foo"}
    assert loaded.updated_at  # set on save


def test_orchestrator_state_roundtrip(tmp_path: Path):
    state = OrchestratorState(
        run_id="r1",
        run_started_at_commit="def456",
        active_agent="research",
        active_task_state=TaskState.RUNNING,
    )
    state.save(tmp_path)

    loaded = OrchestratorState.load(tmp_path)
    assert loaded.run_id == "r1"
    assert loaded.run_started_at_commit == "def456"
    assert loaded.active_agent == "research"
    assert loaded.active_task_state == TaskState.RUNNING


def test_atomic_write_succeeds_and_leaves_no_temp_files(tmp_path: Path):
    target = tmp_path / "thing.json"
    atomic_write_json(target, {"key": "value"})
    assert target.exists()
    assert read_json(target) == {"key": "value"}
    temps = list(tmp_path.glob(".tmp_*"))
    assert temps == []


def test_atomic_write_preserves_existing_on_failure(tmp_path: Path, monkeypatch):
    target = tmp_path / "thing.json"
    atomic_write_json(target, {"original": True})

    def failing_replace(src, dst):
        raise OSError("simulated")

    monkeypatch.setattr(os, "replace", failing_replace)

    with pytest.raises(OSError, match="simulated"):
        atomic_write_json(target, {"new": True})

    assert read_json(target) == {"original": True}
    temps = list(tmp_path.glob(".tmp_*"))
    assert temps == []


def test_agent_state_file_lands_in_expected_location(tmp_path: Path):
    state = AgentRunState(agent_name="research", run_id="r1")
    state.save(tmp_path)
    expected = tmp_path / "_system" / "agent-state" / "research-r1.json"
    assert expected.exists()


def test_orchestrator_state_file_lands_in_expected_location(tmp_path: Path):
    state = OrchestratorState(run_id="r1")
    state.save(tmp_path)
    expected = tmp_path / "_system" / "orchestrator" / "current-state.json"
    assert expected.exists()
