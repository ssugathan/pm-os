"""Prompt template loading + assembly + SHA capture.

Prompt files live at `_system/prompt-templates/[agent]/[task].md` with YAML
frontmatter for metadata (agent, sub_task, model, effort, turn_type) and a
markdown body for the prompt itself.

Assembly produces a single string from the 5 components per design.md:
project_context, sprint_context, artifacts, task_state, task_instructions.
Sections are separated by `---` lines for readability and parseability.

SHA capture (per the prompt versioning convention):
- prompt_sha — `git log -1 --format=%H` for the file at dispatch time
- dirty — true if the file has uncommitted changes (or is untracked)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PromptComponents:
    """The 5 components that make up an assembled prompt (per design.md)."""

    project_context: str = ""
    sprint_context: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)  # filename -> content
    task_state: str = ""
    task_instructions: str = ""


def parse_template(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter + markdown body. Returns (metadata, body).

    If no frontmatter, returns ({}, text). A literal `---` in the body is
    preserved because the split caps at 2.
    """
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return {}, text
    # Strip leading "---\n" then split on next "---" line
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text
    metadata = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return metadata, body


def load_template(template_path: Path) -> tuple[dict[str, Any], str]:
    """Read template file and parse frontmatter + body."""
    with open(template_path) as f:
        return parse_template(f.read())


def assemble_prompt(components: PromptComponents) -> str:
    """Concatenate the 5 components into a single user-message string.

    Sections separated by `---` for readability. Empty components are skipped.
    """
    sections: list[str] = []

    if components.project_context.strip():
        sections.append(f"# Project context\n\n{components.project_context.strip()}")

    if components.sprint_context.strip():
        sections.append(f"# Sprint context\n\n{components.sprint_context.strip()}")

    if components.artifacts:
        parts = ["# Artifacts"]
        for name, content in components.artifacts.items():
            parts.append(f"\n## {name}\n\n{content.strip()}")
        sections.append("\n".join(parts))

    if components.task_state.strip():
        sections.append(f"# Task state\n\n{components.task_state.strip()}")

    if components.task_instructions.strip():
        sections.append(f"# Task instructions\n\n{components.task_instructions.strip()}")

    return "\n\n---\n\n".join(sections)


def prompt_sha(template_path: Path, repo_root: Path) -> tuple[str, bool]:
    """Capture (sha, dirty) for a prompt template at dispatch time.

    - sha: last commit that touched this file, empty if untracked / no history.
    - dirty: true if the file has uncommitted changes OR is untracked.

    Caller decides what to do with dirty (warn-and-record by default; refuse
    dispatch when `prompt_versioning.strict` is true).
    """
    template_path = Path(template_path).resolve()
    repo_root = Path(repo_root).resolve()
    try:
        rel = template_path.relative_to(repo_root)
    except ValueError:
        # Template not under repo_root — can't version it
        return "", True

    rel_str = str(rel)

    sha_result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", rel_str],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    sha = sha_result.stdout.strip() if sha_result.returncode == 0 else ""

    if not sha:
        # No history — untracked or never committed
        return "", True

    # `git diff --quiet HEAD --` exits 1 if there are uncommitted changes
    diff_result = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", rel_str],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    dirty = diff_result.returncode != 0

    return sha, dirty
