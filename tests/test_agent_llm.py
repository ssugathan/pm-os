"""LLMAgent + SmokeAgent tests — wire-through with mocked adapter.

Verifies:
- Template loaded, prompt assembled with provided components
- prompt_sha + prompt_dirty captured onto SubTaskRecord (and persisted)
- Strict mode raises before the adapter is called
- llm.call telemetry emitted with model + tokens + sha
- End-to-end via Orchestrator.dispatch works (state file written, base telemetry fires)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pmos.adapters.base import Response
from pmos.agents.llm import StrictPromptVersioningError
from pmos.agents.smoke import SmokeAgent
from pmos.config import Config, PromptVersioningConfig
from pmos.orchestrator import Orchestrator
from pmos.state import SubTaskStatus, TaskState


def _make_mock_adapter(text: str = "pong", model: str = "claude-sonnet-4-6"):
    adapter = MagicMock()
    adapter.call.return_value = Response(
        text=text,
        tokens_in=10,
        tokens_out=2,
        model=model,
    )
    return adapter


def _write_template(base_dir: Path, agent_name: str, sub_task: str, body: str) -> Path:
    path = base_dir / "_system" / "prompt-templates" / agent_name / f"{sub_task}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return path


def _seed_smoke_template(base_dir: Path) -> Path:
    return _write_template(
        base_dir,
        "smoke",
        "ping",
        "---\nagent: smoke\nsub_task: ping\nmodel: claude\n---\n\nRespond with pong",
    )


def _read_events(base_dir: Path) -> list[dict]:
    path = base_dir / "_system" / "telemetry" / "events.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def test_smoke_dispatch_calls_adapter_with_assembled_prompt(tmp_path: Path):
    _seed_smoke_template(tmp_path)
    adapter = _make_mock_adapter("pong")
    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=adapter,
        config=Config(),
        repo_root=tmp_path,
    )
    orch = Orchestrator(tmp_path)

    result = orch.dispatch(agent, run_id="s1", inputs={"project_context": "PROJ"})

    assert result.task_state == TaskState.COMPLETE
    assert result.sub_tasks[0].status == SubTaskStatus.COMPLETE
    assert result.sub_tasks[0].output["text"] == "pong"
    assert result.sub_tasks[0].output["tokens_in"] == 10
    assert result.sub_tasks[0].output["tokens_out"] == 2

    adapter.call.assert_called_once()
    prompt_arg = adapter.call.call_args.args[0]
    assert "PROJ" in prompt_arg  # project_context wired through
    assert "Respond with pong" in prompt_arg  # template body included


def test_prompt_sha_and_dirty_captured_on_record(tmp_path: Path):
    """Template lives outside any git repo here → sha empty, dirty True."""
    _seed_smoke_template(tmp_path)
    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=_make_mock_adapter(),
        config=Config(),
        repo_root=tmp_path,
    )
    orch = Orchestrator(tmp_path)

    result = orch.dispatch(agent, run_id="s2", inputs={})

    record = result.sub_tasks[0]
    assert record.prompt_sha == ""
    assert record.prompt_dirty is True


def test_prompt_sha_recorded_when_template_committed(tmp_path: Path):
    """Initialize a git repo, commit the template, verify sha is non-empty + dirty False."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@e.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, check=True)
    _seed_smoke_template(tmp_path)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=tmp_path, check=True)
    expected_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=_make_mock_adapter(),
        config=Config(),
        repo_root=tmp_path,
    )
    orch = Orchestrator(tmp_path)
    result = orch.dispatch(agent, run_id="s3", inputs={})

    record = result.sub_tasks[0]
    assert record.prompt_sha == expected_sha
    assert record.prompt_dirty is False


def test_strict_mode_raises_before_adapter_call_on_dirty(tmp_path: Path):
    """With strict=True, dirty template should raise without ever calling adapter."""
    _seed_smoke_template(tmp_path)  # untracked → dirty
    adapter = _make_mock_adapter()
    config = Config(prompt_versioning=PromptVersioningConfig(strict=True))
    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=adapter,
        config=config,
        repo_root=tmp_path,
    )
    orch = Orchestrator(tmp_path)

    with pytest.raises(StrictPromptVersioningError, match="uncommitted changes"):
        orch.dispatch(agent, run_id="s4", inputs={})

    adapter.call.assert_not_called()


def test_llm_call_telemetry_event_emitted(tmp_path: Path):
    _seed_smoke_template(tmp_path)
    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=_make_mock_adapter(text="pong", model="claude-sonnet-4-6"),
        config=Config(),
        repo_root=tmp_path,
    )
    orch = Orchestrator(tmp_path)
    orch.dispatch(agent, run_id="s5", inputs={})

    events = _read_events(tmp_path)
    llm_calls = [e for e in events if e["event"] == "llm.call"]
    assert len(llm_calls) == 1

    props = llm_calls[0]["properties"]
    assert props["agent"] == "smoke"
    assert props["sub_task"] == "ping"
    assert props["model"] == "claude-sonnet-4-6"
    assert props["tokens_in"] == 10
    assert props["tokens_out"] == 2
    assert "duration_ms" in props
    assert "prompt_sha" in props
    assert "prompt_dirty" in props


def test_llmagent_find_record_raises_on_unknown_name(tmp_path: Path):
    _seed_smoke_template(tmp_path)
    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=_make_mock_adapter(),
        config=Config(),
        repo_root=tmp_path,
    )
    from pmos.state import AgentRunState, SubTaskRecord

    state = AgentRunState(
        agent_name="smoke",
        run_id="x",
        sub_tasks=[SubTaskRecord(name="ping")],
    )
    with pytest.raises(KeyError, match="nonexistent"):
        agent._find_record(state, "nonexistent")


# ---------- Retry integration ----------


@pytest.fixture
def no_sleep(monkeypatch):
    """Stub time.sleep in retry so retry-flow tests don't actually wait."""
    monkeypatch.setattr("pmos.retry.time.sleep", lambda s: None)


def test_adapter_transient_then_success_retries_and_records_telemetry(
    tmp_path: Path, no_sleep
):
    from pmos.adapters.base import TransientError

    _seed_smoke_template(tmp_path)
    adapter = MagicMock()
    adapter.call.side_effect = [
        TransientError("temporary"),
        Response(text="pong", tokens_in=10, tokens_out=2, model="claude-sonnet-4-6"),
    ]
    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=adapter,
        config=Config(),
        repo_root=tmp_path,
    )
    orch = Orchestrator(tmp_path)

    result = orch.dispatch(agent, run_id="r1", inputs={})

    assert result.task_state == TaskState.COMPLETE
    assert adapter.call.call_count == 2

    events = _read_events(tmp_path)
    retries = [e for e in events if e["event"] == "retry.attempted"]
    assert len(retries) == 1
    assert retries[0]["properties"]["error_type"] == "transient"
    assert retries[0]["properties"]["retry_num"] == 1
    # llm.call event still fires after the successful call
    llm_calls = [e for e in events if e["event"] == "llm.call"]
    assert len(llm_calls) == 1


def test_adapter_quota_propagates_without_retry(tmp_path: Path, no_sleep):
    from pmos.adapters.base import QuotaError

    _seed_smoke_template(tmp_path)
    adapter = MagicMock()
    adapter.call.side_effect = QuotaError("usage limit hit")
    agent = SmokeAgent(
        base_dir=tmp_path,
        adapter=adapter,
        config=Config(),
        repo_root=tmp_path,
    )
    orch = Orchestrator(tmp_path)

    with pytest.raises(QuotaError, match="usage limit"):
        orch.dispatch(agent, run_id="r2", inputs={})

    assert adapter.call.call_count == 1  # no retry on quota
    events = _read_events(tmp_path)
    retries = [e for e in events if e["event"] == "retry.attempted"]
    assert len(retries) == 1
    assert retries[0]["properties"]["error_type"] == "quota"
