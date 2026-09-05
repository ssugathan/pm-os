"""No-op test agent. Three sub-tasks that simulate work. Used to validate
dispatch + crash recovery without depending on any LLM API.

Supports controlled crash injection via the `crash_at` constructor arg —
construct with `crash_at="work"` for the first run to simulate failure mid-loop,
then re-run without the flag to test recovery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from pmos.agents.base import Agent
from pmos.state import AgentRunState, now_iso


class NoOpAgent(Agent):
    name = "noop"

    def __init__(self, base_dir: Path, crash_at: str | None = None, **kwargs):
        super().__init__(base_dir, **kwargs)
        self.crash_at = crash_at

    def sub_tasks(self) -> list[tuple[str, Callable[[AgentRunState], Any]]]:
        return [
            ("setup", self._setup),
            ("work", self._work),
            ("finalize", self._finalize),
        ]

    def _setup(self, state: AgentRunState) -> dict:
        self._maybe_crash("setup")
        return {"step": "setup", "at": now_iso()}

    def _work(self, state: AgentRunState) -> dict:
        self._maybe_crash("work")
        return {"step": "work", "at": now_iso()}

    def _finalize(self, state: AgentRunState) -> dict:
        self._maybe_crash("finalize")
        return {"step": "finalize", "at": now_iso()}

    def _maybe_crash(self, sub_task_name: str) -> None:
        if self.crash_at == sub_task_name:
            raise RuntimeError(f"simulated crash at {sub_task_name}")
