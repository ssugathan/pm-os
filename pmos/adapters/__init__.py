"""Model adapters — thin layer over per-vendor SDKs.

Per design.md: an agent is NOT 1:1 with an LLM. Model allocation is per-sub-task,
swappable via config. Adapters give the orchestrator a uniform call surface so
swapping models is a config change, not a code change.

Adapters do NOT implement retry — that's orchestrator-level behavior per the
error handling strategy. Adapters classify errors via typed exceptions
(TransientError / QuotaError / MalformedResponseError) and the orchestrator
decides what to do.
"""

from pmos.adapters.base import (
    MalformedResponseError,
    ModelAdapter,
    QuotaError,
    Response,
    TransientError,
)
from pmos.adapters.claude import ClaudeAdapter

__all__ = [
    "ClaudeAdapter",
    "MalformedResponseError",
    "ModelAdapter",
    "QuotaError",
    "Response",
    "TransientError",
]
