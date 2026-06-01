"""Judgment point system tests — modes, handlers, decision log persistence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pmos.agents.noop import NoOpAgent
from pmos.judgment import (
    AutoApproveJudgmentHandler,
    FixedJudgmentHandler,
    JudgmentMode,
    JudgmentRecord,
)
from pmos.state import AgentRunState


def _read_events(base_dir: Path) -> list[dict]:
    path = base_dir / "_system" / "telemetry" / "events.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------- record serialization ----------


def test_judgment_record_to_dict_roundtrip():
    r = JudgmentRecord(
        name="J1_scope",
        mode=JudgmentMode.AUTOMATED,
        question="include enterprise as background?",
        options=["yes", "no"],
        decision="yes",
        reasoning="regulatory landscape is enterprise-driven",
        context="user said focus on SMB",
    )
    d = r.to_dict()
    assert d["name"] == "J1_scope"
    assert d["mode"] == "automated"
    assert d["options"] == ["yes", "no"]
    assert d["decision"] == "yes"
    assert d["timestamp"]  # auto-set


# ---------- handler unit tests ----------


def test_auto_approve_handler_picks_first_option():
    handler = AutoApproveJudgmentHandler()
    decision, reasoning = handler.decide("J1", "?", ["a", "b", "c"], "")
    assert decision == "a"
    assert "first option" in reasoning


def test_fixed_handler_returns_canned_decisions():
    handler = FixedJudgmentHandler({"J1": ("b", "because"), "J2": ("c", "reason")})
    assert handler.decide("J1", "?", ["a", "b"], "") == ("b", "because")
    assert handler.decide("J2", "?", ["a", "b", "c"], "") == ("c", "reason")


def test_fixed_handler_raises_on_unknown_judgment():
    handler = FixedJudgmentHandler({})
    with pytest.raises(KeyError, match="J99"):
        handler.decide("J99", "?", ["a"], "")


# ---------- agent.judgment() automated path ----------


def test_automated_judgment_records_to_state_and_returns_decision(tmp_path: Path):
    agent = NoOpAgent(tmp_path, judgment_modes={"J1": "automated"})
    state = AgentRunState(agent_name="noop", run_id="r1")

    decision = agent.judgment(
        state,
        "J1",
        question="include enterprise context?",
        options=["yes", "no"],
        context="user said SMB",
        automated_decider=lambda: ("yes", "regulatory landscape is enterprise-driven"),
    )

    assert decision == "yes"
    assert len(state.judgment_log) == 1
    record = state.judgment_log[0]
    assert record["name"] == "J1"
    assert record["mode"] == "automated"
    assert record["decision"] == "yes"
    assert record["reasoning"] == "regulatory landscape is enterprise-driven"
    assert record["context"] == "user said SMB"


def test_automated_judgment_defaults_to_automated_when_mode_missing(tmp_path: Path):
    """Unknown judgment name → defaults to automated (per agent specs)."""
    agent = NoOpAgent(tmp_path)  # no judgment_modes
    state = AgentRunState(agent_name="noop", run_id="r2")

    decision = agent.judgment(
        state,
        "J_unknown",
        question="?",
        options=["a", "b"],
        automated_decider=lambda: ("a", "default"),
    )
    assert decision == "a"
    assert state.judgment_log[0]["mode"] == "automated"


def test_automated_judgment_raises_when_no_decider(tmp_path: Path):
    agent = NoOpAgent(tmp_path, judgment_modes={"J1": "automated"})
    state = AgentRunState(agent_name="noop", run_id="r3")
    with pytest.raises(ValueError, match="no automated_decider"):
        agent.judgment(state, "J1", "?", ["a"])


# ---------- agent.judgment() collaborative path ----------


def test_collaborative_judgment_uses_handler(tmp_path: Path):
    handler = FixedJudgmentHandler({"J2": ("flag prominently", "evidence contradicts")})
    agent = NoOpAgent(
        tmp_path,
        judgment_modes={"J2": "collaborative"},
        judgment_handler=handler,
    )
    state = AgentRunState(agent_name="noop", run_id="r4")

    decision = agent.judgment(
        state,
        "J2",
        question="how strongly to flag?",
        options=["gentle note", "flag prominently"],
        context="competitor X claim contradicted by recent launch",
    )

    assert decision == "flag prominently"
    record = state.judgment_log[0]
    assert record["mode"] == "collaborative"
    assert record["reasoning"] == "evidence contradicts"


def test_collaborative_judgment_raises_when_no_handler(tmp_path: Path):
    agent = NoOpAgent(tmp_path, judgment_modes={"J2": "collaborative"})
    state = AgentRunState(agent_name="noop", run_id="r5")
    with pytest.raises(ValueError, match="no judgment_handler"):
        agent.judgment(state, "J2", "?", ["a"])


# ---------- telemetry + persistence ----------


def test_judgment_emits_telemetry_event(tmp_path: Path):
    agent = NoOpAgent(tmp_path)
    state = AgentRunState(agent_name="noop", run_id="r6")
    agent.judgment(
        state,
        "J1",
        "?",
        ["a", "b"],
        automated_decider=lambda: ("a", "first"),
    )
    events = _read_events(tmp_path)
    fires = [e for e in events if e["event"] == "judgment.fired"]
    assert len(fires) == 1
    assert fires[0]["properties"]["judgment_name"] == "J1"
    assert fires[0]["properties"]["mode"] == "automated"
    assert fires[0]["properties"]["decision"] == "a"


def test_judgment_log_survives_state_save_and_load(tmp_path: Path):
    agent = NoOpAgent(tmp_path)
    state = AgentRunState(agent_name="noop", run_id="r7")
    agent.judgment(state, "J1", "?", ["a", "b"], automated_decider=lambda: ("a", "r1"))
    agent.judgment(state, "J2", "?", ["x", "y"], automated_decider=lambda: ("y", "r2"))

    loaded = AgentRunState.load(tmp_path, "noop", "r7")
    assert len(loaded.judgment_log) == 2
    assert loaded.judgment_log[0]["decision"] == "a"
    assert loaded.judgment_log[1]["decision"] == "y"


def test_multiple_judgments_in_one_run_accumulate(tmp_path: Path):
    agent = NoOpAgent(tmp_path)
    state = AgentRunState(agent_name="noop", run_id="r8")
    for i, opt in enumerate(["a", "b", "c"]):
        agent.judgment(
            state,
            f"J{i}",
            "?",
            [opt],
            automated_decider=lambda o=opt: (o, "auto"),
        )
    assert len(state.judgment_log) == 3
    assert [r["decision"] for r in state.judgment_log] == ["a", "b", "c"]
