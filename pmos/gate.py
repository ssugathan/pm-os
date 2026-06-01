"""Gate flow — post-agent human approval point.

Per design.md: gates are mandatory pauses where the orchestrator presents agent
output to a human and waits for one of three outcomes:
- Approved → orchestrator advances
- Rejected → orchestrator stops, preserves work
- Modify-requested → orchestrator re-runs the agent with feedback

For Phase 1 single-agent dispatch, the gate is optional (caller passes a
GateHandler to dispatch()). When pipeline orchestration arrives, gates become
mandatory between agents. The MODIFY_REQUESTED outcome raises so the caller
decides what to do — the simplest caller (a script) just re-dispatches; a
richer caller (a future pipeline orchestrator) might rebuild context first.

Two built-in handlers:
- AutoApproveHandler — tests, or "trust this agent unconditionally" config
- CLIGateHandler — terminal prompt, the default for interactive use

Real UIs (eventual dashboard) will implement GateHandler with their own review
surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from pmos.state import AgentRunState


class GateOutcome(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFY_REQUESTED = "modify_requested"


@dataclass
class GateDecision:
    outcome: GateOutcome
    feedback: str = ""  # populated for MODIFY_REQUESTED; optional for others


class GateHandler(Protocol):
    """Review the agent's run and return a GateDecision."""

    def review(self, agent_name: str, state: AgentRunState) -> GateDecision: ...


class GateRejected(Exception):
    """Raised when the gate handler rejects an agent run. Caller stops the pipeline."""


class GateModifyRequested(Exception):
    """Raised when the gate handler asks for modification. `feedback` carries the
    user's reason; caller decides how to re-dispatch the agent."""

    def __init__(self, feedback: str):
        super().__init__(f"Modify requested: {feedback}")
        self.feedback = feedback


class AutoApproveHandler:
    """Always approves. Use in tests and in trust-the-agent config paths."""

    def review(self, agent_name: str, state: AgentRunState) -> GateDecision:
        return GateDecision(outcome=GateOutcome.APPROVED)


class CLIGateHandler:
    """Terminal-based gate. Prints a brief summary; reads a/m/r from stdin.

    Kept deliberately minimal — for richer review (diff viewing, inline edits)
    use a different handler. Real dashboards will implement GateHandler with
    their own review surface.
    """

    def review(self, agent_name: str, state: AgentRunState) -> GateDecision:
        print(f"\n## Gate: {agent_name} agent complete (run_id={state.run_id})")
        print(f"Sub-tasks: {len(state.sub_tasks)} total")
        for st in state.sub_tasks:
            print(f"  - {st.name}: {st.status.value}")
        choice = input("Approve / Modify / Reject [a/m/r]: ").strip().lower()
        if choice.startswith("a") or choice == "":
            return GateDecision(outcome=GateOutcome.APPROVED)
        if choice.startswith("m"):
            feedback = input("Feedback: ").strip()
            return GateDecision(outcome=GateOutcome.MODIFY_REQUESTED, feedback=feedback)
        return GateDecision(outcome=GateOutcome.REJECTED)
