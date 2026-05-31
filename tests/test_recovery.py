"""Crash recovery test.

Verifies the core idempotency claim from design.md: after a crash, re-running
an agent with the same run_id resumes from the first incomplete sub-task and
does NOT re-execute completed sub-tasks.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pmos.agents.noop import NoOpAgent
from pmos.orchestrator import Orchestrator
from pmos.state import AgentRunState, SubTaskStatus, TaskState


def test_crash_mid_loop_then_recover(tmp_path: Path):
    orch = Orchestrator(tmp_path)

    # First run — agent crashes at the second sub-task
    crashing_agent = NoOpAgent(tmp_path, crash_at="work")
    with pytest.raises(RuntimeError, match="simulated crash at work"):
        orch.dispatch(crashing_agent, run_id="r1", inputs={"trial": 1})

    state = AgentRunState.load(tmp_path, "noop", "r1")
    assert state.sub_tasks[0].status == SubTaskStatus.COMPLETE
    assert state.sub_tasks[1].status == SubTaskStatus.FAILED
    assert state.sub_tasks[1].error
    assert state.sub_tasks[2].status == SubTaskStatus.PENDING
    setup_output_before = state.sub_tasks[0].output

    # Recover with a healthy agent
    healthy_agent = NoOpAgent(tmp_path)
    result = orch.recover(healthy_agent, run_id="r1")

    assert result.task_state == TaskState.COMPLETE
    assert all(st.status == SubTaskStatus.COMPLETE for st in result.sub_tasks)

    # Idempotency: setup output must be byte-identical, not re-generated
    assert result.sub_tasks[0].output == setup_output_before

    # Work and finalize now have outputs
    assert result.sub_tasks[1].output["step"] == "work"
    assert result.sub_tasks[2].output["step"] == "finalize"
    # Inputs preserved from the original run
    assert result.inputs == {"trial": 1}


def test_recover_with_no_existing_state_raises(tmp_path: Path):
    orch = Orchestrator(tmp_path)
    agent = NoOpAgent(tmp_path)
    with pytest.raises(FileNotFoundError):
        orch.recover(agent, run_id="nonexistent")
