"""Orchestrator state is keyed per run (known bug a: stale run_id).

Before the fix, a single `current-state.json` was shared by every run, and
`_load_or_init_state` returned whatever was on disk without checking run_id, so
dispatching run-2 after run-1 kept run-1's run_id and run_started_at_commit.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pmos.agents.noop import NoOpAgent
from pmos.orchestrator import Orchestrator
from pmos.state import (
    OrchestratorState,
    TaskState,
    atomic_write_json,
    legacy_orchestrator_state_path,
    orchestrator_state_path,
    read_json,
)


def _orch_at(tmp_path: Path, monkeypatch, sha: str) -> Orchestrator:
    orch = Orchestrator(tmp_path)
    monkeypatch.setattr(orch, "_git_head_sha", lambda: sha)
    return orch


def test_new_run_does_not_inherit_previous_run_state(tmp_path: Path, monkeypatch):
    _orch_at(tmp_path, monkeypatch, "sha-1").dispatch(
        NoOpAgent(tmp_path), run_id="run-1", inputs={}
    )

    # A fresh orchestrator instance, as after a process restart.
    state = _orch_at(tmp_path, monkeypatch, "sha-2")._load_or_init_state("run-2")

    assert state.run_id == "run-2"
    assert state.run_started_at_commit == "sha-2"


def test_each_run_has_its_own_state_file(tmp_path: Path, monkeypatch):
    _orch_at(tmp_path, monkeypatch, "sha-1").dispatch(
        NoOpAgent(tmp_path), run_id="run-1", inputs={}
    )
    _orch_at(tmp_path, monkeypatch, "sha-2").dispatch(
        NoOpAgent(tmp_path), run_id="run-2", inputs={}
    )

    run1 = OrchestratorState.load(tmp_path, "run-1")
    run2 = OrchestratorState.load(tmp_path, "run-2")
    assert (run1.run_id, run1.run_started_at_commit) == ("run-1", "sha-1")
    assert (run2.run_id, run2.run_started_at_commit) == ("run-2", "sha-2")
    assert orchestrator_state_path(tmp_path, "run-1") != orchestrator_state_path(
        tmp_path, "run-2"
    )


def test_resuming_one_run_does_not_touch_another(tmp_path: Path, monkeypatch):
    with pytest.raises(RuntimeError):
        _orch_at(tmp_path, monkeypatch, "sha-1").dispatch(
            NoOpAgent(tmp_path, crash_at="work"), run_id="run-1", inputs={}
        )
    _orch_at(tmp_path, monkeypatch, "sha-2").dispatch(
        NoOpAgent(tmp_path), run_id="run-2", inputs={}
    )
    run2_before = read_json(orchestrator_state_path(tmp_path, "run-2"))

    # Resume run-1 at a later commit: it keeps its own run-start commit.
    _orch_at(tmp_path, monkeypatch, "sha-3").recover(NoOpAgent(tmp_path), run_id="run-1")

    run1 = OrchestratorState.load(tmp_path, "run-1")
    assert run1.run_started_at_commit == "sha-1"
    assert run1.active_task_state == TaskState.COMPLETE
    assert read_json(orchestrator_state_path(tmp_path, "run-2")) == run2_before


def test_legacy_single_file_state_is_migrated_for_its_own_run(tmp_path: Path, monkeypatch):
    legacy = legacy_orchestrator_state_path(tmp_path)
    atomic_write_json(
        legacy,
        OrchestratorState(
            run_id="run-1",
            run_started_at_commit="sha-legacy",
            active_agent="noop",
            active_task_state=TaskState.RUNNING,
        ).to_dict(),
    )

    state = _orch_at(tmp_path, monkeypatch, "sha-now")._load_or_init_state("run-1")

    assert state.run_id == "run-1"
    assert state.run_started_at_commit == "sha-legacy"
    assert OrchestratorState.load(tmp_path, "run-1").run_started_at_commit == "sha-legacy"
    assert not legacy.exists()


def test_legacy_single_file_state_for_another_run_is_left_alone(
    tmp_path: Path, monkeypatch
):
    legacy = legacy_orchestrator_state_path(tmp_path)
    original = OrchestratorState(run_id="run-1", run_started_at_commit="sha-legacy")
    atomic_write_json(legacy, original.to_dict())
    before = read_json(legacy)

    state = _orch_at(tmp_path, monkeypatch, "sha-now")._load_or_init_state("run-2")

    assert state.run_id == "run-2"
    assert state.run_started_at_commit == "sha-now"
    assert read_json(legacy) == before
