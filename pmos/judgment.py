"""Judgment point system.

Per design.md: sub-tasks encounter judgment points (e.g., J1_scope_boundaries,
J7_assumption_contradiction). Each point has a config-driven mode:

- AUTOMATED — the agent decides via a caller-provided `automated_decider`
  (heuristic, LLM call, whatever the sub-task supplies). The decision is logged
  so a human can audit (and override at the agent's gate).
- COLLABORATIVE — the agent pauses and a JudgmentHandler asks the human.

Either way, the decision lands in `state.judgment_log` and a `judgment.fired`
telemetry event records it. The handler abstraction is the same shape as the
gate handler — plug a CLI for terminal use, FixedJudgmentHandler in tests, a
dashboard later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from pmos.state import now_iso


class JudgmentMode(str, Enum):
    AUTOMATED = "automated"
    COLLABORATIVE = "collaborative"


@dataclass
class JudgmentRecord:
    name: str
    mode: JudgmentMode
    question: str
    options: list[str]
    decision: str
    reasoning: str
    context: str = ""
    timestamp: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mode": self.mode.value,
            "question": self.question,
            "options": list(self.options),
            "decision": self.decision,
            "reasoning": self.reasoning,
            "context": self.context,
            "timestamp": self.timestamp,
        }


class JudgmentHandler(Protocol):
    """Called in collaborative mode. Returns (decision, reasoning)."""

    def decide(
        self,
        name: str,
        question: str,
        options: list[str],
        context: str,
    ) -> tuple[str, str]: ...


class AutoApproveJudgmentHandler:
    """Picks the first option. Useful for tests and trust-the-defaults configs."""

    def decide(
        self,
        name: str,
        question: str,
        options: list[str],
        context: str,
    ) -> tuple[str, str]:
        return options[0], "auto-approved (first option)"


class FixedJudgmentHandler:
    """Returns canned (decision, reasoning) per judgment name. Tests use this."""

    def __init__(self, decisions: dict[str, tuple[str, str]]):
        self.decisions = decisions

    def decide(
        self,
        name: str,
        question: str,
        options: list[str],
        context: str,
    ) -> tuple[str, str]:
        if name in self.decisions:
            return self.decisions[name]
        raise KeyError(f"No fixed decision for judgment {name!r}")


class CLIJudgmentHandler:
    """Terminal-based handler. Minimal — for richer prompts use a custom handler."""

    def decide(
        self,
        name: str,
        question: str,
        options: list[str],
        context: str,
    ) -> tuple[str, str]:
        print(f"\n## Judgment: {name}")
        print(f"Question: {question}")
        if context:
            print(f"Context: {context}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        choice = input(f"Pick 1-{len(options)} or type free-form: ").strip()
        try:
            idx = int(choice)
            decision = options[idx - 1]
        except (ValueError, IndexError):
            decision = choice
        reasoning = input("Reasoning (optional): ").strip() or "user choice"
        return decision, reasoning
