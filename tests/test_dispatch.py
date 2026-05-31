"""End-to-end dispatch test using the NoOpAgent."""

from __future__ import annotations

from pathlib import Path

from pmos.agents.noop import NoOpAgent
from pmos.orchestrator import Orchestrator
from pmos.state import OrchestratorState, SubTaskStatus, TaskState


def test_noop_dispatch_end_to_end(tmp_path: Path):
    orch = Orchestrator(tmp_path)
    agent = NoOpAgent(tmp_path)

    result = orch.dispatch(agent, run_id="r1", inputs={"hello": "world"})

    assert result.task_state == TaskState.COMPLETE
    assert len(result.sub_tasks) == 3
    assert all(st.status == SubTaskStatus.COMPLETE for st in result.sub_tasks)
    assert result.sub_tasks[0].output["step"] == "setup"
    assert result.sub_tasks[1].output["step"] == "work"
    assert result.sub_tasks[2].output["step"] == "finalize"
    assert all("at" in st.output for st in result.sub_tasks)
    assert result.inputs == {"hello": "world"}


def test_orchestrator_state_written_on_dispatch(tmp_path: Path):
    orch = Orchestrator(tmp_path)
    agent = NoOpAgent(tmp_path)

    orch.dispatch(agent, run_id="r2", inputs={})

    state = OrchestratorState.load(tmp_path)
    assert state.run_id == "r2"
    assert state.active_agent == "noop"
    assert state.active_task_state == TaskState.COMPLETE
    # run_started_at_commit may be empty (tmp_path is not a git repo) — both ok
