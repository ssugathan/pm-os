"""Base Agent class. Subclasses define their sub-tasks.

An agent is a Python module that owns a responsibility and runs a sequence of
sub-tasks. Per design.md, an agent is NOT 1:1 with an LLM — different sub-tasks
may use different models or no model at all.

The run loop is idempotent on completed sub-tasks: re-running an agent with the
same run_id resumes from the first incomplete sub-task. This is how crash
recovery works.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from pmos import telemetry
from pmos.state import (
    AgentRunState,
    SubTaskRecord,
    SubTaskStatus,
    TaskState,
    now_iso,
)


class Agent:
    """Subclasses set `name` and implement `sub_tasks()`.

    `sub_tasks()` returns an ordered list of (name, callable) tuples.
    Each callable takes `(state: AgentRunState)` and returns the output to record.
    """

    name: str = "base"

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)

    def sub_tasks(self) -> list[tuple[str, Callable[[AgentRunState], Any]]]:
        raise NotImplementedError

    def run(self, run_id: str, inputs: dict[str, Any]) -> AgentRunState:
        """Run from scratch or resume an existing run. Idempotent on completed sub-tasks."""
        defs = self.sub_tasks()

        try:
            state = AgentRunState.load(self.base_dir, self.name, run_id)
        except FileNotFoundError:
            state = AgentRunState(
                agent_name=self.name,
                run_id=run_id,
                inputs=inputs,
                started_at=now_iso(),
                sub_tasks=[SubTaskRecord(name=name) for name, _ in defs],
            )

        state.task_state = TaskState.RUNNING
        state.save(self.base_dir)

        for record, (sub_task_name, func) in zip(state.sub_tasks, defs, strict=True):
            if record.status == SubTaskStatus.COMPLETE:
                continue  # idempotent skip
            record.status = SubTaskStatus.RUNNING
            state.save(self.base_dir)
            sub_start = time.monotonic()
            telemetry.event(
                "sub_task.started",
                {
                    "run_id": state.run_id,
                    "agent": self.name,
                    "sub_task": sub_task_name,
                    "prompt_sha": record.prompt_sha,
                    "prompt_dirty": record.prompt_dirty,
                },
                base_dir=self.base_dir,
            )
            try:
                output = func(state)
            except Exception as e:
                record.status = SubTaskStatus.FAILED
                record.error = str(e)
                state.save(self.base_dir)
                telemetry.event(
                    "sub_task.failed",
                    {
                        "run_id": state.run_id,
                        "agent": self.name,
                        "sub_task": sub_task_name,
                        "error_type": type(e).__name__,
                        "duration_ms": int((time.monotonic() - sub_start) * 1000),
                    },
                    base_dir=self.base_dir,
                )
                raise
            record.status = SubTaskStatus.COMPLETE
            record.output = output
            state.save(self.base_dir)
            telemetry.event(
                "sub_task.completed",
                {
                    "run_id": state.run_id,
                    "agent": self.name,
                    "sub_task": sub_task_name,
                    "duration_ms": int((time.monotonic() - sub_start) * 1000),
                },
                base_dir=self.base_dir,
            )

        state.task_state = TaskState.COMPLETE
        state.save(self.base_dir)
        return state
