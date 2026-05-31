"""LLMAgent — base class for agents whose sub-tasks call an LLM via a templated prompt.

Subclasses define `sub_tasks()` as usual; each sub-task callable typically calls
`self._call_template(state, sub_task_name, PromptComponents(...))` to perform the
LLM call. The helper handles:

- Loading the template at `<template_dir>/<agent.name>/<sub_task_name>.md`
- Capturing `prompt_sha` + `prompt_dirty` onto the SubTaskRecord
- Enforcing `prompt_versioning.strict` config — refuses to dispatch dirty templates
- Assembling the prompt from the provided components + template body
- Calling the adapter and emitting `llm.call` telemetry (model, tokens, duration, sha)
"""

from __future__ import annotations

import time
from pathlib import Path

from pmos import telemetry
from pmos.adapters.base import ModelAdapter, Response
from pmos.agents.base import Agent
from pmos.config import Config
from pmos.prompts import (
    PromptComponents,
    assemble_prompt,
    load_template,
    prompt_sha,
)
from pmos.state import AgentRunState, SubTaskRecord


class StrictPromptVersioningError(RuntimeError):
    """Raised when prompt_versioning.strict is True and the template is dirty."""


class LLMAgent(Agent):
    def __init__(
        self,
        base_dir: Path,
        *,
        adapter: ModelAdapter,
        config: Config,
        repo_root: Path | None = None,
        template_dir: Path | None = None,
    ):
        super().__init__(base_dir)
        self.adapter = adapter
        self.config = config
        self.repo_root = Path(repo_root) if repo_root else Path(base_dir)
        self.template_dir = (
            Path(template_dir)
            if template_dir
            else Path(base_dir) / "_system" / "prompt-templates"
        )

    def _find_record(self, state: AgentRunState, sub_task_name: str) -> SubTaskRecord:
        for record in state.sub_tasks:
            if record.name == sub_task_name:
                return record
        raise KeyError(f"No sub-task record named {sub_task_name!r}")

    def _call_template(
        self,
        state: AgentRunState,
        sub_task_name: str,
        components: PromptComponents,
    ) -> Response:
        template_path = self.template_dir / self.name / f"{sub_task_name}.md"
        metadata, body = load_template(template_path)

        sha, dirty = prompt_sha(template_path, self.repo_root)
        record = self._find_record(state, sub_task_name)
        record.prompt_sha = sha
        record.prompt_dirty = dirty
        state.save(self.base_dir)  # persist SHA + dirty before the LLM call fires

        if dirty and self.config.prompt_versioning.strict:
            raise StrictPromptVersioningError(
                f"{template_path} has uncommitted changes; refusing to dispatch "
                "(prompt_versioning.strict=true)"
            )

        components.task_instructions = body
        prompt = assemble_prompt(components)
        system = metadata.get("system")

        start = time.monotonic()
        response = self.adapter.call(prompt, system=system)
        telemetry.event(
            "llm.call",
            {
                "run_id": state.run_id,
                "agent": self.name,
                "sub_task": sub_task_name,
                "model": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "duration_ms": int((time.monotonic() - start) * 1000),
                "prompt_sha": sha,
                "prompt_dirty": dirty,
            },
            base_dir=self.base_dir,
        )
        return response
