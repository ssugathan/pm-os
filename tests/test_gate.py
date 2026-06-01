"""Gate flow tests — handlers and dispatch integration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pmos.agents.noop import NoOpAgent
from pmos.gate import (
    AutoApproveHandler,
    GateDecision,
    GateModifyRequested,
    GateOutcome,
    GateRejected,
)
from pmos.orchestrator import Orchestrator
from pmos.state import AgentRunState, TaskState


def _read_events(base_dir: Path) -> list[dict]:
    path = base_dir / "_system" / "telemetry" / "events.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


class _RejectHandler:
    def review(self, agent_name: str, state: AgentRunState) -> GateDecision:
        return GateDecision(outcome=GateOutcome.REJECTED)


class _ModifyHandler:
    def __init__(self, feedback: str = "please rework"):
        self.feedback = feedback

    def review(self, agent_name: str, state: AgentRunState) -> GateDecision:
        return GateDecision(outcome=GateOutcome.MODIFY_REQUESTED, feedback=self.feedback)


class _RecordingApproveHandler:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def review(self, agent_name: str, state: AgentRunState) -> GateDecision:
        self.calls.append((agent_name, state.run_id))
        return GateDecision(outcome=GateOutcome.APPROVED)


# ---------- handler unit tests ----------


def test_auto_approve_handler_returns_approved():
    handler = AutoApproveHandler()
    state = AgentRunState(agent_name="x", run_id="r1")
    decision = handler.review("x", state)
    assert decision.outcome == GateOutcome.APPROVED


def test_gate_decision_default_feedback_empty():
    d = GateDecision(outcome=GateOutcome.APPROVED)
    assert d.feedback == ""


# ---------- dispatch integration ----------


def test_dispatch_without_gate_handler_behaves_as_before(tmp_path: Path):
    orch = Orchestrator(tmp_path)
    agent = NoOpAgent(tmp_path)
    result = orch.dispatch(agent, run_id="g0", inputs={})
    assert result.task_state == TaskState.COMPLETE
    # No gate events
    events = _read_events(tmp_path)
    assert not any(e["event"].startswith("gate.") for e in events)


def test_dispatch_with_approve_handler_returns_result_and_emits_telemetry(tmp_path: Path):
    orch = Orchestrator(tmp_path)
    agent = NoOpAgent(tmp_path)
    handler = _RecordingApproveHandler()

    result = orch.dispatch(agent, run_id="g1", inputs={}, gate_handler=handler)

    assert result.task_state == TaskState.COMPLETE
    assert handler.calls == [("noop", "g1")]

    events = _read_events(tmp_path)
    gate_events = [e for e in events if e["event"].startswith("gate.")]
    names = [e["event"] for e in gate_events]
    assert "gate.presented" in names
    assert "gate.decided" in names
    decided = next(e for e in gate_events if e["event"] == "gate.decided")
    assert decided["properties"]["outcome"] == "approved"
    assert decided["properties"]["has_feedback"] is False


def test_dispatch_with_reject_handler_raises_gate_rejected(tmp_path: Path):
    orch = Orchestrator(tmp_path)
    agent = NoOpAgent(tmp_path)

    with pytest.raises(GateRejected, match="noop run rejected"):
        orch.dispatch(agent, run_id="g2", inputs={}, gate_handler=_RejectHandler())

    events = _read_events(tmp_path)
    decided = next(e for e in events if e["event"] == "gate.decided")
    assert decided["properties"]["outcome"] == "rejected"


def test_dispatch_with_modify_handler_raises_with_feedback(tmp_path: Path):
    orch = Orchestrator(tmp_path)
    agent = NoOpAgent(tmp_path)

    with pytest.raises(GateModifyRequested) as exc_info:
        orch.dispatch(
            agent,
            run_id="g3",
            inputs={},
            gate_handler=_ModifyHandler("be more specific"),
        )

    assert exc_info.value.feedback == "be more specific"

    events = _read_events(tmp_path)
    decided = next(e for e in events if e["event"] == "gate.decided")
    assert decided["properties"]["outcome"] == "modify_requested"
    assert decided["properties"]["has_feedback"] is True


def test_gate_does_not_fire_when_agent_run_fails(tmp_path: Path):
    """If the agent itself raises, the gate should never be invoked."""
    orch = Orchestrator(tmp_path)
    crashing_agent = NoOpAgent(tmp_path, crash_at="work")
    handler = _RecordingApproveHandler()

    with pytest.raises(RuntimeError, match="simulated crash"):
        orch.dispatch(crashing_agent, run_id="g4", inputs={}, gate_handler=handler)

    assert handler.calls == []  # never invoked
    events = _read_events(tmp_path)
    assert not any(e["event"].startswith("gate.") for e in events)
