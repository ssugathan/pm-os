"""Config loading tests — defaults, yaml read, overrides deep-merge."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from pmos.config import (
    Config,
    ContextBudget,
    PromptVersioningConfig,
    _deep_merge,
    default_config_path,
    load_config,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_dataclass_defaults_are_sensible():
    cfg = Config()
    assert cfg.prompt_versioning.strict is False
    assert cfg.retry.max_attempts == 5
    assert cfg.retry.backoff_seconds == [2, 4, 8, 16, 32]
    assert cfg.validation.structural == "always"
    assert cfg.validation.content.consistency is False
    assert cfg.telemetry.distinct_id == "pm_os_user"


def test_context_budget_available_for_prompt():
    cb = ContextBudget(max_input_tokens=180_000, reserved_for_output=30_000)
    assert cb.available_for_prompt == 150_000


def test_load_config_with_no_yaml_returns_defaults(tmp_path: Path):
    # tmp_path has no _system/orchestrator/default_config.yaml — should fall back
    cfg = load_config(tmp_path)
    assert isinstance(cfg, Config)
    assert cfg.prompt_versioning.strict is False
    assert cfg.context_budgets == {}  # no defaults yaml = no budgets defined


def _seed_default_yaml(base_dir: Path) -> None:
    real_default = PROJECT_ROOT / "_system" / "orchestrator" / "default_config.yaml"
    dest = default_config_path(base_dir)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(real_default, dest)


def test_load_config_reads_default_yaml(tmp_path: Path):
    """Copy the real default_config.yaml into a tmp tree and load it."""
    _seed_default_yaml(tmp_path)

    cfg = load_config(tmp_path)

    # Context budgets populated
    assert "claude" in cfg.context_budgets
    assert cfg.context_budgets["claude"].max_input_tokens == 180_000
    assert cfg.context_budgets["claude"].available_for_prompt == 150_000
    assert cfg.context_budgets["gemini"].max_input_tokens == 900_000
    assert cfg.context_budgets["gpt"].max_input_tokens == 120_000

    # Retry from yaml
    assert cfg.retry.max_attempts == 5
    assert cfg.retry.backoff_seconds == [2, 4, 8, 16, 32]

    # Validation
    assert cfg.validation.structural == "always"
    assert cfg.validation.content.consistency is False
    assert cfg.validation.content.input_coverage is True


def test_load_config_with_overrides_deep_merges(tmp_path: Path):
    """Overrides should layer on top of defaults via deep merge."""
    _seed_default_yaml(tmp_path)

    overrides_path = tmp_path / "config-overrides.yaml"
    overrides_path.write_text(
        yaml.safe_dump(
            {
                "prompt_versioning": {"strict": True},
                "validation": {"content": {"consistency": True}},
                "context_budgets": {
                    "claude": {"max_input_tokens": 200_000, "reserved_for_output": 40_000}
                },
            }
        )
    )

    cfg = load_config(tmp_path, overrides_path=overrides_path)

    # Override wins on leaf
    assert cfg.prompt_versioning.strict is True
    assert cfg.validation.content.consistency is True

    # Non-overridden leaves stay at default
    assert cfg.validation.content.input_coverage is True
    assert cfg.validation.structural == "always"

    # Replaced claude budget; gemini + gpt untouched
    assert cfg.context_budgets["claude"].max_input_tokens == 200_000
    assert cfg.context_budgets["claude"].available_for_prompt == 160_000
    assert cfg.context_budgets["gemini"].max_input_tokens == 900_000


def test_deep_merge_replaces_lists():
    """Lists are leaf values — replaced wholesale, not concatenated."""
    base = {"retry": {"backoff_seconds": [2, 4, 8]}}
    override = {"retry": {"backoff_seconds": [1, 2]}}
    merged = _deep_merge(base, override)
    assert merged == {"retry": {"backoff_seconds": [1, 2]}}


def test_deep_merge_preserves_unrelated_keys():
    base = {"a": 1, "nested": {"x": 1, "y": 2}}
    override = {"nested": {"y": 99}}
    merged = _deep_merge(base, override)
    assert merged == {"a": 1, "nested": {"x": 1, "y": 99}}


def test_repo_default_yaml_is_loadable_by_real_loader():
    """Smoke test: the actual default_config.yaml in the repo loads cleanly."""
    cfg = load_config(PROJECT_ROOT)
    assert "claude" in cfg.context_budgets
    assert isinstance(cfg.prompt_versioning, PromptVersioningConfig)


def test_load_with_nonexistent_overrides_falls_through_to_defaults(tmp_path: Path):
    """Missing overrides yaml is treated as empty — defaults stay intact.

    Pins current behavior. If we later want missing-overrides to raise (so config
    bugs aren't silently hidden), update this test.
    """
    _seed_default_yaml(tmp_path)
    cfg = load_config(tmp_path, overrides_path=tmp_path / "nonexistent.yaml")
    assert cfg.context_budgets["claude"].max_input_tokens == 180_000
