"""ModelAdapter ABC + typed errors.

Adapters classify SDK errors into three categories that map to design.md's
error handling strategy:

- TransientError → retry with exponential backoff (timeout, 429, 5xx, network)
- QuotaError → no retry, pause and warn (usage cap, billing, auth)
- MalformedResponseError → retry with same prompt up to 2 times (4xx other than auth/quota, empty/truncated)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class TransientError(Exception):
    """Retryable error — backoff and try again."""


class QuotaError(Exception):
    """Non-retryable — usage cap, billing, or auth. Pause and warn."""


class MalformedResponseError(Exception):
    """Response was malformed or unexpected. Retry up to N times with same prompt."""


@dataclass
class Response:
    """Uniform response shape across all model adapters."""

    text: str
    tokens_in: int
    tokens_out: int
    model: str
    raw: Any = None  # vendor-specific response object, useful for debugging


class ModelAdapter(ABC):
    """Subclasses implement `call()`. Raise typed errors above for failure modes."""

    @abstractmethod
    def call(
        self,
        prompt: str,
        *,
        system: str | None = None,
        **kwargs: Any,
    ) -> Response:
        """Send `prompt` (and optional `system`) to the model, return Response.

        Raises:
            TransientError: retryable failure (caller backs off + retries)
            QuotaError: non-retryable, pause and warn user
            MalformedResponseError: bad response shape, retry up to 2x same prompt
        """
        raise NotImplementedError
