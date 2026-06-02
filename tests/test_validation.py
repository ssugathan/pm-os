"""Output validation tests — built-ins, framework, agent integration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pmos.agents.base import Agent
from pmos.orchestrator import Orchestrator
from pmos.state import AgentRunState, SubTaskStatus, TaskState
from pmos.validation import (
    ValidationFailed,
    ValidationReport,
    ValidationResult,
    has_keys,
    not_none,
    run_validators,
    under_word_count,
)


def _read_events(base_dir: Path) -> list[dict]:
    path = base_dir / "_system" / "telemetry" / "events.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------- ValidationReport ----------


def test_report_passed_when_all_checks_pass():
    report = ValidationReport(
        structural=[ValidationResult("a", True), ValidationResult("b", True)]
    )
    assert report.passed is True


def test_report_fails_when_any_check_fails():
    report = ValidationReport(
        structural=[ValidationResult("a", True), ValidationResult("b", False, "boom")]
    )
    assert report.passed is False
    failed = report.failed_checks()
    assert len(failed) == 1
    assert failed[0].check_name == "b"


def test_report_to_dict_includes_overall_pass():
    report = ValidationReport(content=[ValidationResult("x", True)])
    d = report.to_dict()
    assert d["overall_passed"] is True
    assert d["content"][0]["check"] == "x"


# ---------- Built-in validators ----------


def test_not_none_pass_and_fail():
    state = AgentRunState(agent_name="x", run_id="r")
    assert not_none()("anything", state).passed is True
    assert not_none()(None, state).passed is False


def test_has_keys_with_dict():
    state = AgentRunState(agent_name="x", run_id="r")
    v = has_keys("a", "b")
    assert v({"a": 1, "b": 2}, state).passed is True
    assert v({"a": 1}, state).passed is False
    assert v("not a dict", state).passed is False


def test_under_word_count_string():
    state = AgentRunState(agent_name="x", run_id="r")
    v = under_word_count(5)
    assert v("one two three", state).passed is True
    assert v("one two three four five six", state).passed is False


def test_under_word_count_dict_with_text_field():
    state = AgentRunState(agent_name="x", run_id="r")
    v = under_word_count(3)
    assert v({"text": "a b c"}, state).passed is True
    assert v({"text": "a b c d"}, state).passed is False


# ---------- run_validators aggregation ----------


def test_run_validators_combines_structural_and_content():
    state = AgentRunState(agent_name="x", run_id="r")
    validators = {
        "structural": [not_none()],
        "content": [has_keys("foo")],
    }
    report = run_validators(validators, {"foo": 1}, state)
    assert len(report.structural) == 1
    assert len(report.content) == 1
    assert report.passed is True


# ---------- Agent integration ----------


class _CountingAgent(Agent):
    """Test agent whose sub-task returns the call count. Useful for retry tests."""

    name = "counting"

    def __init__(self, base_dir, **kwargs):
        super().__init__(base_dir, **kwargs)
        self.call_count = 0

    def sub_tasks(self):
        return [("step", self._step)]

    def _step(self, state):
        self.call_count += 1
        return {"count": self.call_count}


def _passes_when_count_at_least(threshold: int):
    def check(output, state):
        ok = isinstance(output, dict) and output.get("count", 0) >= threshold
        return ValidationResult(
            f"count_ge_{threshold}", ok, "" if ok else f"count={output.get('count')}"
        )

    return check


def _always_fails(name: str = "always_fails"):
    def check(output, state):
        return ValidationResult(name, False, "deliberately failing")

    return check


def test_sub_task_passes_validation_on_first_try(tmp_path: Path):
    agent = _CountingAgent(
        tmp_path,
        validators={"step": {"structural": [_passes_when_count_at_least(1)]}},
    )
    orch = Orchestrator(tmp_path)
    result = orch.dispatch(agent, run_id="v1", inputs={})
    assert result.task_state == TaskState.COMPLETE
    assert agent.call_count == 1
    record = result.sub_tasks[0]
    assert record.validation["overall_passed"] is True


def test_sub_task_retries_until_validation_passes(tmp_path: Path):
    """First call returns count=1 (fails), retry returns count=2 (passes)."""
    agent = _CountingAgent(
        tmp_path,
        validators={"step": {"structural": [_passes_when_count_at_least(2)]}},
        max_validation_retries=2,
    )
    orch = Orchestrator(tmp_path)
    result = orch.dispatch(agent, run_id="v2", inputs={})

    assert result.task_state == TaskState.COMPLETE
    assert agent.call_count == 2  # initial + 1 retry
    record = result.sub_tasks[0]
    assert record.status == SubTaskStatus.COMPLETE
    assert record.validation["overall_passed"] is True
    assert record.output["count"] == 2

    events = _read_events(tmp_path)
    retries = [e for e in events if e["event"] == "validation.retry_triggered"]
    assert len(retries) == 1


def test_sub_task_fails_when_retries_exhausted(tmp_path: Path):
    agent = _CountingAgent(
        tmp_path,
        validators={"step": {"structural": [_always_fails()]}},
        max_validation_retries=2,
    )
    orch = Orchestrator(tmp_path)

    with pytest.raises(ValidationFailed, match="always_fails"):
        orch.dispatch(agent, run_id="v3", inputs={})

    # initial + 2 retries = 3 calls
    assert agent.call_count == 3

    # State should reflect the failure
    state = AgentRunState.load(tmp_path, "counting", "v3")
    assert state.sub_tasks[0].status == SubTaskStatus.FAILED
    assert "validation failed" in state.sub_tasks[0].error
    assert state.sub_tasks[0].validation["overall_passed"] is False


def test_sub_task_failed_event_emitted_with_validation_error_type(tmp_path: Path):
    agent = _CountingAgent(
        tmp_path,
        validators={"step": {"structural": [_always_fails()]}},
    )
    orch = Orchestrator(tmp_path)
    with pytest.raises(ValidationFailed):
        orch.dispatch(agent, run_id="v4", inputs={})

    events = _read_events(tmp_path)
    failed = next(e for e in events if e["event"] == "sub_task.failed")
    assert failed["properties"]["error_type"] == "ValidationFailed"


def test_no_validators_means_no_retries(tmp_path: Path):
    """When no validators are configured for a sub-task, output passes through."""
    agent = _CountingAgent(tmp_path)  # no validators
    orch = Orchestrator(tmp_path)
    result = orch.dispatch(agent, run_id="v5", inputs={})
    assert result.task_state == TaskState.COMPLETE
    assert agent.call_count == 1


def test_validation_persists_in_state_file(tmp_path: Path):
    agent = _CountingAgent(
        tmp_path,
        validators={"step": {"structural": [_passes_when_count_at_least(1)]}},
    )
    orch = Orchestrator(tmp_path)
    orch.dispatch(agent, run_id="v6", inputs={})

    loaded = AgentRunState.load(tmp_path, "counting", "v6")
    record = loaded.sub_tasks[0]
    assert record.validation is not None
    assert record.validation["overall_passed"] is True
    assert record.validation["structural"][0]["check"] == "count_ge_1"


def test_content_validators_also_run(tmp_path: Path):
    """Content validators run after structural and contribute to the overall result."""
    agent = _CountingAgent(
        tmp_path,
        validators={
            "step": {
                "structural": [not_none()],
                "content": [_passes_when_count_at_least(1)],
            }
        },
    )
    orch = Orchestrator(tmp_path)
    result = orch.dispatch(agent, run_id="v7", inputs={})
    record = result.sub_tasks[0]
    assert len(record.validation["structural"]) == 1
    assert len(record.validation["content"]) == 1
