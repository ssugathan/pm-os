"""Orchestrator — dispatches agents, tracks pipeline-level state.

This is the walking-skeleton version. Sequencing the full 7-agent pipeline,
gates, judgment points, and prompt assembly come in later commits.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from pmos import telemetry
from pmos.agents.base import Agent
from pmos.state import AgentRunState, OrchestratorState, TaskState


class Orchestrator:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)

    def dispatch(self, agent: Agent, run_id: str, inputs: dict[str, Any]) -> AgentRunState:
        """Dispatch an agent for a fresh run.

        If state already exists for (agent.name, run_id), the agent's run loop
        will resume idempotently from the first incomplete sub-task. Use
        `recover()` for explicit resume — the difference is that `recover()`
        loads inputs from the existing state file, while `dispatch()` takes
        them from the caller.
        """
        orch_state = self._load_or_init_state(run_id)
        orch_state.active_agent = agent.name
        orch_state.active_task_state = TaskState.RUNNING
        orch_state.save(self.base_dir)

        start = time.monotonic()
        telemetry.event(
            "agent.dispatched",
            {
                "run_id": run_id,
                "agent": agent.name,
                "run_started_at_commit": orch_state.run_started_at_commit,
            },
            base_dir=self.base_dir,
        )

        try:
            result = agent.run(run_id, inputs)
        except Exception as e:
            telemetry.event(
                "agent.failed",
                {
                    "run_id": run_id,
                    "agent": agent.name,
                    "error_type": type(e).__name__,
                    "duration_ms": int((time.monotonic() - start) * 1000),
                },
                base_dir=self.base_dir,
            )
            raise

        orch_state.active_task_state = TaskState.COMPLETE
        orch_state.save(self.base_dir)
        telemetry.event(
            "agent.completed",
            {
                "run_id": run_id,
                "agent": agent.name,
                "duration_ms": int((time.monotonic() - start) * 1000),
                "sub_task_count": len(result.sub_tasks),
            },
            base_dir=self.base_dir,
        )
        return result

    def recover(self, agent: Agent, run_id: str) -> AgentRunState:
        """Resume an interrupted agent run. Loads inputs from the existing state file."""
        existing = AgentRunState.load(self.base_dir, agent.name, run_id)
        return self.dispatch(agent, run_id, existing.inputs)

    def _load_or_init_state(self, run_id: str) -> OrchestratorState:
        try:
            return OrchestratorState.load(self.base_dir)
        except FileNotFoundError:
            return OrchestratorState(
                run_id=run_id,
                run_started_at_commit=self._git_head_sha(),
            )

    def _git_head_sha(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
