"""Sub-task records are matched by name on resume (known bug b2).

Before the fix, `Agent.run` paired stored records with the agent's current
sub-task list by position (`zip(strict=True)`): a length change raised a bare
ValueError, and a reorder silently attached records to the wrong sub-tasks.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pmos.agents.base import SubTaskDriftError
from pmos.agents.noop import NoOpAgent
from pmos.state import AgentRunState, SubTaskStatus


class _ReshapedNoOp(NoOpAgent):
    """Same agent name as NoOpAgent, with a different sub-task list."""

    def __init__(self, base_dir: Path, names: list[str], **kwargs):
        super().__init__(base_dir, **kwargs)
        self.names = names
        self.calls: list[str] = []

    def sub_tasks(self):
        def make(n):
            def f(state):
                self.calls.append(n)
                return {"step": n}

            return f

        return [(n, make(n)) for n in self.names]


def _crash_first_run(tmp_path: Path) -> dict:
    with pytest.raises(RuntimeError):
        NoOpAgent(tmp_path, crash_at="work").run("r1", {})
    return AgentRunState.load(tmp_path, "noop", "r1").to_dict()


def test_reordered_sub_tasks_raise_and_leave_state_untouched(tmp_path: Path):
    before = _crash_first_run(tmp_path)
    agent = _ReshapedNoOp(tmp_path, ["work", "setup", "finalize"])

    with pytest.raises(SubTaskDriftError) as exc:
        agent.run("r1", {})

    assert exc.value.reordered == ["setup", "work"]
    assert exc.value.added == [] and exc.value.removed == []
    assert "reordered" in str(exc.value) and "noop" in str(exc.value)
    assert agent.calls == []
    after = AgentRunState.load(tmp_path, "noop", "r1").to_dict()
    assert after["sub_tasks"] == before["sub_tasks"]
    assert after["task_state"] == before["task_state"]


def test_added_and_removed_sub_tasks_are_named(tmp_path: Path):
    _crash_first_run(tmp_path)
    agent = _ReshapedNoOp(tmp_path, ["setup", "work", "review"])

    with pytest.raises(SubTaskDriftError) as exc:
        agent.run("r1", {})

    assert exc.value.added == ["review"]
    assert exc.value.removed == ["finalize"]
    assert "review" in str(exc.value) and "finalize" in str(exc.value)
    assert agent.calls == []


def test_extra_sub_task_is_drift_not_bare_value_error(tmp_path: Path):
    _crash_first_run(tmp_path)
    agent = _ReshapedNoOp(tmp_path, ["setup", "work", "finalize", "publish"])

    with pytest.raises(SubTaskDriftError) as exc:
        agent.run("r1", {})

    assert exc.value.added == ["publish"]


def test_duplicate_sub_task_names_are_rejected(tmp_path: Path):
    agent = _ReshapedNoOp(tmp_path, ["setup", "setup"])
    with pytest.raises(SubTaskDriftError, match="duplicate"):
        agent.run("r1", {})


def test_unchanged_sub_tasks_resume_by_name(tmp_path: Path):
    before = _crash_first_run(tmp_path)
    agent = _ReshapedNoOp(tmp_path, ["setup", "work", "finalize"])

    result = agent.run("r1", {})

    assert agent.calls == ["work", "finalize"]  # setup skipped as complete
    assert result.sub_tasks[0].output == before["sub_tasks"][0]["output"]
    assert [st.name for st in result.sub_tasks] == ["setup", "work", "finalize"]
    assert all(st.status == SubTaskStatus.COMPLETE for st in result.sub_tasks)
