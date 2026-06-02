"""Output validation — structural (always) + content (configurable).

Per design.md: sub-task outputs are validated before the sub-task is marked
COMPLETE. Structural checks are deterministic Python (cheap, always); content
checks may invoke an LLM (configurable). If validation fails, the sub-task is
re-run up to `max_validation_retries` times (default 2). If still failing,
ValidationFailed is raised and the sub-task is marked FAILED via the normal
exception path.

Validators are pluggable callables: `(output, state) -> ValidationResult`.
Built-ins below cover common structural checks; agent-specific content
validators (input coverage, consistency, hallucination flag, scope compliance)
land per-agent as real agents arrive.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from pmos.state import AgentRunState


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    message: str = ""

    def to_dict(self) -> dict:
        return {"check": self.check_name, "passed": self.passed, "message": self.message}


@dataclass
class ValidationReport:
    structural: list[ValidationResult] = field(default_factory=list)
    content: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.structural + self.content)

    def failed_checks(self) -> list[ValidationResult]:
        return [r for r in self.structural + self.content if not r.passed]

    def to_dict(self) -> dict:
        return {
            "structural": [r.to_dict() for r in self.structural],
            "content": [r.to_dict() for r in self.content],
            "overall_passed": self.passed,
        }


class ValidationFailed(Exception):
    """Validation failed and the per-sub-task retry budget is exhausted."""

    def __init__(self, report: ValidationReport):
        self.report = report
        failed = [r.check_name for r in report.failed_checks()]
        super().__init__(f"Validation failed after retries: {failed}")


# Validator signature
Validator = Callable[[Any, AgentRunState], ValidationResult]


# ---------- Built-in structural validators ----------


def not_none(name: str = "not_none") -> Validator:
    """Output must not be None."""

    def check(output: Any, state: AgentRunState) -> ValidationResult:
        ok = output is not None
        return ValidationResult(name, ok, "" if ok else "output was None")

    return check


def has_keys(*keys: str, name: str = "has_keys") -> Validator:
    """Output must be a dict containing all listed keys."""

    def check(output: Any, state: AgentRunState) -> ValidationResult:
        if not isinstance(output, dict):
            return ValidationResult(
                name, False, f"expected dict, got {type(output).__name__}"
            )
        missing = [k for k in keys if k not in output]
        if missing:
            return ValidationResult(name, False, f"missing keys: {missing}")
        return ValidationResult(name, True)

    return check


def under_word_count(limit: int, name: str = "under_word_count") -> Validator:
    """For string outputs (or dicts with a 'text' field), word count must be ≤ limit."""

    def check(output: Any, state: AgentRunState) -> ValidationResult:
        if isinstance(output, str):
            text = output
        elif isinstance(output, dict) and "text" in output:
            text = output["text"]
        else:
            return ValidationResult(
                name, False, f"can't word-count {type(output).__name__}"
            )
        count = len(text.split())
        ok = count <= limit
        return ValidationResult(name, ok, f"{count} words" + ("" if ok else f" > {limit}"))

    return check


def run_validators(
    validators: dict[str, list[Validator]],
    output: Any,
    state: AgentRunState,
) -> ValidationReport:
    """Run structural + content validators (in that order) and aggregate results."""
    report = ValidationReport()
    for v in validators.get("structural", []):
        report.structural.append(v(output, state))
    for v in validators.get("content", []):
        report.content.append(v(output, state))
    return report
