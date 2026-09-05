"""Retry wrapper for adapter calls.

Per design.md error handling strategy:
- TransientError → exponential backoff per policy.backoff_seconds, up to
  policy.max_attempts retries, then raise RetryExhaustedError
- MalformedResponseError → up to policy.malformed_response_retries retries (no
  backoff — likely a prompt issue, not a load issue), then raise
- QuotaError → no retry, propagates immediately (user must resolve subscription)
- Anything else → propagates (treated as a bug, not retryable)

`on_retry` callback fires BEFORE each backoff sleep (and before raising for
quota), so callers can emit telemetry like `retry.attempted` per attempt.

When retries are exhausted, the orchestrator's existing exception path takes
over: the sub-task is marked FAILED in the agent state file, and the next
recover() call will retry the whole sub-task (the design.md "cross-resume"
attempt counting is deferred to a follow-up commit).
"""

from __future__ import annotations

import time
from typing import Any, Callable, TypeVar

from pmos.adapters.base import (
    MalformedResponseError,
    QuotaError,
    TransientError,
)
from pmos.config import RetryConfig

T = TypeVar("T")


class RetryExhaustedError(Exception):
    """Max retries hit. Wraps the last underlying error."""


def retry_call(
    fn: Callable[[], T],
    *,
    policy: RetryConfig,
    on_retry: Callable[[dict[str, Any]], None] | None = None,
) -> T:
    """Call `fn()` with retry per `policy`. See module docstring for full semantics."""
    transient_retries = 0
    malformed_retries = 0

    while True:
        try:
            return fn()
        except QuotaError:
            if on_retry is not None:
                on_retry({"error_type": "quota", "retry_num": 0, "sleep_seconds": 0})
            raise
        except TransientError as e:
            transient_retries += 1
            if transient_retries > policy.max_attempts:
                raise RetryExhaustedError(
                    f"transient errors after {policy.max_attempts} retries: {e}"
                ) from e
            backoff = policy.backoff_seconds[
                min(transient_retries - 1, len(policy.backoff_seconds) - 1)
            ]
            if on_retry is not None:
                on_retry(
                    {
                        "error_type": "transient",
                        "retry_num": transient_retries,
                        "sleep_seconds": backoff,
                        "error_message": str(e),
                    }
                )
            time.sleep(backoff)
        except MalformedResponseError as e:
            malformed_retries += 1
            if malformed_retries > policy.malformed_response_retries:
                raise RetryExhaustedError(
                    f"malformed responses after {policy.malformed_response_retries} retries: {e}"
                ) from e
            if on_retry is not None:
                on_retry(
                    {
                        "error_type": "malformed",
                        "retry_num": malformed_retries,
                        "sleep_seconds": 0,
                        "error_message": str(e),
                    }
                )
            # no sleep — likely a prompt issue, not a load issue
