"""Telemetry failures never abort a run or hide its error (known bug c).

Before the fix, an OSError from the events-log write propagated out of
`telemetry.event`: a healthy dispatch aborted with agent and orchestrator state
stuck at RUNNING, and a failure inside an error-path emit (`sub_task.failed`,
`agent.failed`) replaced the agent's original exception.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pmos import telemetry
from pmos.agents.noop import NoOpAgent
from pmos.orchestrator import Orchestrator
from pmos.state import AgentRunState, OrchestratorState, SubTaskStatus, TaskState


def _break_events_log(tmp_path: Path, monkeypatch) -> None:
    """Point the log under a regular file, so every write raises OSError."""
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("")
    monkeypatch.setenv("PMOS_TELEMETRY_PATH", str(blocker / "events.jsonl"))


def _fail_on(monkeypatch, *event_names: str) -> list[str]:
    """Make the emitter raise OSError for the named events only."""
    real = telemetry._emit_jsonl
    attempted: list[str] = []

    def flaky(payload, *, base_dir=None):
        attempted.append(payload["event"])
        if payload["event"] in event_names:
            raise OSError("disk full (simulated)")
        real(payload, base_dir=base_dir)

    monkeypatch.setattr(telemetry, "_emit_jsonl", flaky)
    return attempted


def test_event_swallows_write_failure_and_warns(tmp_path: Path, monkeypatch, capsys):
    _break_events_log(tmp_path, monkeypatch)

    telemetry.event("test.thing", {"count": 1}, base_dir=tmp_path)  # must not raise

    err = capsys.readouterr().err
    assert "pmos telemetry" in err
    assert "test.thing" in err


def test_dispatch_completes_when_telemetry_is_broken(tmp_path: Path, monkeypatch, capsys):
    _break_events_log(tmp_path, monkeypatch)

    result = Orchestrator(tmp_path).dispatch(NoOpAgent(tmp_path), run_id="r1", inputs={})

    assert result.task_state == TaskState.COMPLETE
    assert all(st.status == SubTaskStatus.COMPLETE for st in result.sub_tasks)
    assert AgentRunState.load(tmp_path, "noop", "r1").task_state == TaskState.COMPLETE
    orch_state = OrchestratorState.load(tmp_path, "r1")
    assert orch_state.active_task_state == TaskState.COMPLETE
    assert "pmos telemetry" in capsys.readouterr().err


def test_original_error_survives_sub_task_failed_emit_failure(tmp_path: Path, monkeypatch):
    """Error path in Agent._execute_sub_task (sub_task.failed)."""
    attempted = _fail_on(monkeypatch, "sub_task.failed")

    with pytest.raises(RuntimeError, match="simulated crash at work"):
        NoOpAgent(tmp_path, crash_at="work").run("r1", {})

    assert "sub_task.failed" in attempted
    work = AgentRunState.load(tmp_path, "noop", "r1").sub_tasks[1]
    assert work.status == SubTaskStatus.FAILED
    assert work.error == "simulated crash at work"


def test_original_error_survives_agent_failed_emit_failure(tmp_path: Path, monkeypatch):
    """Error path in Orchestrator.dispatch (agent.failed), with both error-path
    emits failing."""
    attempted = _fail_on(monkeypatch, "sub_task.failed", "agent.failed")

    with pytest.raises(RuntimeError, match="simulated crash at work"):
        Orchestrator(tmp_path).dispatch(
            NoOpAgent(tmp_path, crash_at="work"), run_id="r1", inputs={}
        )

    assert "agent.failed" in attempted
