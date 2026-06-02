"""Base Agent class. Subclasses define their sub-tasks.

An agent is a Python module that owns a responsibility and runs a sequence of
sub-tasks. Per design.md, an agent is NOT 1:1 with an LLM — different sub-tasks
may use different models or no model at all.

The run loop is idempotent on completed sub-tasks: re-running an agent with the
same run_id resumes from the first incomplete sub-task. This is how crash
recovery works.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from pmos import telemetry
from pmos.judgment import JudgmentHandler, JudgmentMode, JudgmentRecord
from pmos.state import (
    AgentRunState,
    SubTaskRecord,
    SubTaskStatus,
    TaskState,
    now_iso,
)
from pmos.validation import (
    ValidationFailed,
    Validator,
    run_validators,
)


class Agent:
    """Subclasses set `name` and implement `sub_tasks()`.

    `sub_tasks()` returns an ordered list of (name, callable) tuples.
    Each callable takes `(state: AgentRunState)` and returns the output to record.

    Optional kwargs:
    - judgment_modes: maps judgment point name → "automated" | "collaborative"
    - judgment_handler: invoked for collaborative judgments
    """

    name: str = "base"

    def __init__(
        self,
        base_dir: Path,
        *,
        judgment_modes: dict[str, str] | None = None,
        judgment_handler: JudgmentHandler | None = None,
        validators: dict[str, dict[str, list[Validator]]] | None = None,
        max_validation_retries: int = 2,
    ):
        self.base_dir = Path(base_dir)
        self.judgment_modes = judgment_modes or {}
        self.judgment_handler = judgment_handler
        self.validators = validators or {}
        self.max_validation_retries = max_validation_retries

    def sub_tasks(self) -> list[tuple[str, Callable[[AgentRunState], Any]]]:
        raise NotImplementedError

    def _execute_sub_task(
        self,
        state: AgentRunState,
        record: SubTaskRecord,
        sub_task_name: str,
        func: Callable[[AgentRunState], Any],
    ) -> None:
        record.status = SubTaskStatus.RUNNING
        state.save(self.base_dir)
        sub_start = time.monotonic()
        telemetry.event(
            "sub_task.started",
            {
                "run_id": state.run_id,
                "agent": self.name,
                "sub_task": sub_task_name,
                "prompt_sha": record.prompt_sha,
                "prompt_dirty": record.prompt_dirty,
            },
            base_dir=self.base_dir,
        )

        validators = self.validators.get(sub_task_name, {})
        attempts_remaining = self.max_validation_retries

        while True:
            try:
                output = func(state)
            except Exception as e:
                record.status = SubTaskStatus.FAILED
                record.error = str(e)
                state.save(self.base_dir)
                telemetry.event(
                    "sub_task.failed",
                    {
                        "run_id": state.run_id,
                        "agent": self.name,
                        "sub_task": sub_task_name,
                        "error_type": type(e).__name__,
                        "duration_ms": int((time.monotonic() - sub_start) * 1000),
                    },
                    base_dir=self.base_dir,
                )
                raise

            report = run_validators(validators, output, state)
            record.validation = report.to_dict()

            if report.passed:
                break

            if attempts_remaining > 0:
                attempts_remaining -= 1
                telemetry.event(
                    "validation.retry_triggered",
                    {
                        "run_id": state.run_id,
                        "agent": self.name,
                        "sub_task": sub_task_name,
                        "failed_checks": [r.check_name for r in report.failed_checks()],
                        "attempts_remaining": attempts_remaining,
                    },
                    base_dir=self.base_dir,
                )
                state.save(self.base_dir)
                continue

            # exhausted
            record.status = SubTaskStatus.FAILED
            record.error = f"validation failed: {[r.check_name for r in report.failed_checks()]}"
            record.output = output
            state.save(self.base_dir)
            telemetry.event(
                "sub_task.failed",
                {
                    "run_id": state.run_id,
                    "agent": self.name,
                    "sub_task": sub_task_name,
                    "error_type": "ValidationFailed",
                    "duration_ms": int((time.monotonic() - sub_start) * 1000),
                },
                base_dir=self.base_dir,
            )
            raise ValidationFailed(report)

        record.status = SubTaskStatus.COMPLETE
        record.output = output
        state.save(self.base_dir)
        telemetry.event(
            "sub_task.completed",
            {
                "run_id": state.run_id,
                "agent": self.name,
                "sub_task": sub_task_name,
                "duration_ms": int((time.monotonic() - sub_start) * 1000),
            },
            base_dir=self.base_dir,
        )

    def judgment(
        self,
        state: AgentRunState,
        name: str,
        question: str,
        options: list[str],
        context: str = "",
        *,
        automated_decider: Callable[[], tuple[str, str]] | None = None,
    ) -> str:
        """Fire a judgment point. Returns the chosen decision string.

        Mode comes from `judgment_modes[name]`, defaulting to AUTOMATED.
        - AUTOMATED requires `automated_decider` — sub-task supplies the logic
          (heuristic, LLM call, etc.) that returns (decision, reasoning).
        - COLLABORATIVE requires `judgment_handler` on the agent — the human
          decides via the handler.

        The decision is appended to `state.judgment_log`, state is saved, and a
        `judgment.fired` telemetry event is emitted.
        """
        mode = JudgmentMode(self.judgment_modes.get(name, JudgmentMode.AUTOMATED.value))

        if mode is JudgmentMode.AUTOMATED:
            if automated_decider is None:
                raise ValueError(
                    f"Judgment {name!r} is automated but no automated_decider was provided"
                )
            decision, reasoning = automated_decider()
        else:
            if self.judgment_handler is None:
                raise ValueError(
                    f"Judgment {name!r} is collaborative but agent has no judgment_handler"
                )
            decision, reasoning = self.judgment_handler.decide(
                name, question, options, context
            )

        record = JudgmentRecord(
            name=name,
            mode=mode,
            question=question,
            options=list(options),
            decision=decision,
            reasoning=reasoning,
            context=context,
        )
        state.judgment_log.append(record.to_dict())
        state.save(self.base_dir)

        telemetry.event(
            "judgment.fired",
            {
                "run_id": state.run_id,
                "agent": self.name,
                "judgment_name": name,
                "mode": mode.value,
                "decision": decision,
            },
            base_dir=self.base_dir,
        )

        return decision

    def run(self, run_id: str, inputs: dict[str, Any]) -> AgentRunState:
        """Run from scratch or resume an existing run. Idempotent on completed sub-tasks."""
        defs = self.sub_tasks()

        try:
            state = AgentRunState.load(self.base_dir, self.name, run_id)
        except FileNotFoundError:
            state = AgentRunState(
                agent_name=self.name,
                run_id=run_id,
                inputs=inputs,
                started_at=now_iso(),
                sub_tasks=[SubTaskRecord(name=name) for name, _ in defs],
            )

        state.task_state = TaskState.RUNNING
        state.save(self.base_dir)

        for record, (sub_task_name, func) in zip(state.sub_tasks, defs, strict=True):
            if record.status == SubTaskStatus.COMPLETE:
                continue  # idempotent skip
            self._execute_sub_task(state, record, sub_task_name, func)

        state.task_state = TaskState.COMPLETE
        state.save(self.base_dir)
        return state
