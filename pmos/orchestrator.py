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
from pmos.gate import (
    GateHandler,
    GateModifyRequested,
    GateOutcome,
    GateRejected,
)
from pmos.state import AgentRunState, OrchestratorState, TaskState


def _run_props(run_id: str, agent_name: str, **extra: Any) -> dict[str, Any]:
    """Shared payload for run-scoped telemetry events.

    Key order is part of the emitted payload (events are asserted as exact
    sequences in tests), so the shared keys always come first and extras keep
    their call-site order.
    """
    return {"run_id": run_id, "agent": agent_name, **extra}


class Orchestrator:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)

    def dispatch(
        self,
        agent: Agent,
        run_id: str,
        inputs: dict[str, Any],
        *,
        gate_handler: GateHandler | None = None,
    ) -> AgentRunState:
        """Dispatch an agent for a fresh run.

        If state already exists for (agent.name, run_id), the agent's run loop
        will resume idempotently from the first incomplete sub-task. Use
        `recover()` for explicit resume — the difference is that `recover()`
        loads inputs from the existing state file, while `dispatch()` takes
        them from the caller.

        When `gate_handler` is provided, it's invoked after a successful agent
        run. Raises `GateRejected` on reject or `GateModifyRequested` on modify
        so the caller decides how to act (re-dispatch with feedback, abort, etc.).
        """
        orch_state = self._load_or_init_state(run_id)
        orch_state.active_agent = agent.name
        orch_state.active_task_state = TaskState.RUNNING
        orch_state.save(self.base_dir)

        start = time.monotonic()
        telemetry.event(
            "agent.dispatched",
            _run_props(
                run_id,
                agent.name,
                run_started_at_commit=orch_state.run_started_at_commit,
            ),
            base_dir=self.base_dir,
        )

        try:
            result = agent.run(run_id, inputs)
        except Exception as e:
            telemetry.event(
                "agent.failed",
                _run_props(
                    run_id,
                    agent.name,
                    error_type=type(e).__name__,
                    duration_ms=int((time.monotonic() - start) * 1000),
                ),
                base_dir=self.base_dir,
            )
            raise

        orch_state.active_task_state = TaskState.COMPLETE
        orch_state.save(self.base_dir)
        telemetry.event(
            "agent.completed",
            _run_props(
                run_id,
                agent.name,
                duration_ms=int((time.monotonic() - start) * 1000),
                sub_task_count=len(result.sub_tasks),
            ),
            base_dir=self.base_dir,
        )

        if gate_handler is not None:
            self._run_gate(gate_handler, agent.name, result)

        return result

    def _run_gate(
        self,
        handler: GateHandler,
        agent_name: str,
        state: AgentRunState,
    ) -> None:
        telemetry.event(
            "gate.presented",
            _run_props(state.run_id, agent_name),
            base_dir=self.base_dir,
        )
        decision = handler.review(agent_name, state)
        telemetry.event(
            "gate.decided",
            _run_props(
                state.run_id,
                agent_name,
                outcome=decision.outcome.value,
                has_feedback=bool(decision.feedback),
            ),
            base_dir=self.base_dir,
        )
        if decision.outcome == GateOutcome.REJECTED:
            raise GateRejected(f"{agent_name} run rejected at gate")
        if decision.outcome == GateOutcome.MODIFY_REQUESTED:
            raise GateModifyRequested(decision.feedback)

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
