"""Crash recovery test.

Verifies the core idempotency claim from design.md: after a crash, re-running
an agent with the same run_id resumes from the first incomplete sub-task and
does NOT re-execute completed sub-tasks.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pmos.agents.noop import NoOpAgent
from pmos.orchestrator import Orchestrator
from pmos.state import AgentRunState, SubTaskStatus, TaskState


def read_events(base_dir: Path) -> list[dict]:
    path = base_dir / "_system" / "telemetry" / "events.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


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


def test_telemetry_captures_crash_and_recovery_history(tmp_path: Path):
    """The events log is the execution history, not the final state. Completed
    sub-tasks should appear ONCE (idempotency); retried sub-tasks should appear
    TWICE (failed + succeeded). This is what makes telemetry useful for tuning."""
    orch = Orchestrator(tmp_path)

    crashing = NoOpAgent(tmp_path, crash_at="work")
    with pytest.raises(RuntimeError):
        orch.dispatch(crashing, run_id="rx", inputs={})

    healthy = NoOpAgent(tmp_path)
    orch.recover(healthy, run_id="rx")

    events = read_events(tmp_path)

    def count(event_name: str, sub_task: str | None = None) -> int:
        return sum(
            1
            for e in events
            if e["event"] == event_name
            and (sub_task is None or e["properties"].get("sub_task") == sub_task)
        )

    # Setup: completed once on first run, skipped silently on recovery (no events)
    assert count("sub_task.started", "setup") == 1
    assert count("sub_task.completed", "setup") == 1
    assert count("sub_task.failed", "setup") == 0

    # Work: started + failed on first run, started + completed on recovery
    assert count("sub_task.started", "work") == 2
    assert count("sub_task.failed", "work") == 1
    assert count("sub_task.completed", "work") == 1

    # Finalize: never reached on first run, completed on recovery
    assert count("sub_task.started", "finalize") == 1
    assert count("sub_task.completed", "finalize") == 1

    # Agent-level: 2 dispatches, 1 failed, 1 completed
    assert count("agent.dispatched") == 2
    assert count("agent.failed") == 1
    assert count("agent.completed") == 1
