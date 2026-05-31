"""Prompt template + assembly + SHA capture tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from pmos.prompts import (
    PromptComponents,
    assemble_prompt,
    load_template,
    parse_template,
    prompt_sha,
)


# ---------- parse_template ----------


def test_parse_template_with_frontmatter():
    text = """---
agent: research
sub_task: scope_definition
model: claude
effort: standard
---

You are a research assistant. Do the thing.
"""
    metadata, body = parse_template(text)
    assert metadata == {
        "agent": "research",
        "sub_task": "scope_definition",
        "model": "claude",
        "effort": "standard",
    }
    assert body.startswith("You are a research assistant.")


def test_parse_template_without_frontmatter():
    text = "Just a body, no frontmatter."
    metadata, body = parse_template(text)
    assert metadata == {}
    assert body == "Just a body, no frontmatter."


def test_parse_template_preserves_dashes_in_body():
    """A literal `---` inside the body should not get eaten by frontmatter parsing."""
    text = """---
agent: research
---

Body line 1

---

Body line 3 after a divider.
"""
    metadata, body = parse_template(text)
    assert metadata == {"agent": "research"}
    assert "---" in body  # the body divider survived


def test_load_template_reads_file(tmp_path: Path):
    path = tmp_path / "tmpl.md"
    path.write_text("---\nagent: x\n---\n\nbody here\n")
    metadata, body = load_template(path)
    assert metadata == {"agent": "x"}
    assert body.strip() == "body here"


# ---------- assemble_prompt ----------


def test_assemble_prompt_full():
    c = PromptComponents(
        project_context="PROJECT",
        sprint_context="SPRINT",
        artifacts={"brief.md": "BRIEF", "rubric.md": "RUBRIC"},
        task_state="STATE",
        task_instructions="INSTRUCTIONS",
    )
    out = assemble_prompt(c)
    # All sections present, in order
    assert out.index("# Project context") < out.index("# Sprint context")
    assert out.index("# Sprint context") < out.index("# Artifacts")
    assert out.index("# Artifacts") < out.index("# Task state")
    assert out.index("# Task state") < out.index("# Task instructions")
    # Artifact sub-headings
    assert "## brief.md" in out
    assert "## rubric.md" in out
    # Content present
    for content in ["PROJECT", "SPRINT", "BRIEF", "RUBRIC", "STATE", "INSTRUCTIONS"]:
        assert content in out


def test_assemble_prompt_skips_empty():
    c = PromptComponents(task_instructions="just instructions")
    out = assemble_prompt(c)
    assert "# Project context" not in out
    assert "# Sprint context" not in out
    assert "# Artifacts" not in out
    assert "# Task state" not in out
    assert "# Task instructions" in out


def test_assemble_prompt_empty_components_returns_empty_string():
    out = assemble_prompt(PromptComponents())
    assert out == ""


def test_assemble_prompt_strips_section_whitespace():
    c = PromptComponents(project_context="\n\n  CONTENT  \n\n")
    out = assemble_prompt(c)
    assert "CONTENT" in out
    # No leading whitespace after the heading
    assert "# Project context\n\nCONTENT" in out


# ---------- prompt_sha ----------


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Initialize a tmp git repo with deterministic identity."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, check=True)
    return tmp_path


def _commit(repo: Path, message: str) -> str:
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=repo, check=True)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_prompt_sha_committed_clean(git_repo: Path):
    template = git_repo / "_system" / "prompt-templates" / "research" / "scope.md"
    template.parent.mkdir(parents=True)
    template.write_text("---\nagent: research\n---\n\nbody\n")
    expected_sha = _commit(git_repo, "add template")

    sha, dirty = prompt_sha(template, git_repo)
    assert sha == expected_sha
    assert dirty is False


def test_prompt_sha_committed_then_modified(git_repo: Path):
    template = git_repo / "prompt.md"
    template.write_text("---\nagent: x\n---\n\noriginal\n")
    expected_sha = _commit(git_repo, "add")

    # Modify the file (uncommitted change)
    template.write_text("---\nagent: x\n---\n\nmodified\n")

    sha, dirty = prompt_sha(template, git_repo)
    assert sha == expected_sha  # still points to last commit
    assert dirty is True


def test_prompt_sha_untracked_file(git_repo: Path):
    # Need at least one commit for HEAD to exist
    (git_repo / "seed.txt").write_text("seed")
    _commit(git_repo, "seed")

    template = git_repo / "untracked.md"
    template.write_text("never committed")

    sha, dirty = prompt_sha(template, git_repo)
    assert sha == ""
    assert dirty is True


def test_prompt_sha_template_outside_repo(git_repo: Path, tmp_path: Path):
    """Templates outside the repo root can't be versioned — return dirty."""
    other_dir = tmp_path / "elsewhere"
    other_dir.mkdir()
    template = other_dir / "stray.md"
    template.write_text("hi")
    sha, dirty = prompt_sha(template, git_repo)
    assert sha == ""
    assert dirty is True
