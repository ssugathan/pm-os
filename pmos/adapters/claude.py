"""ClaudeAdapter — Anthropic SDK wrapper.

Defaults to claude-sonnet-4-6 (good cost/capability balance). Override via the
`model` arg or by passing a configured Anthropic client.

Auth: relies on the SDK's default `ANTHROPIC_API_KEY` env var lookup. To use a
different auth path, construct an Anthropic client externally and pass it in.

Error classification:
- APIConnectionError, APITimeoutError, RateLimitError, InternalServerError (5xx) → TransientError
- AuthenticationError, PermissionDeniedError → QuotaError (won't resolve via retry)
- Other APIStatusError (4xx — BadRequest, NotFound, etc.) → MalformedResponseError
- Empty response.content → MalformedResponseError
"""

from __future__ import annotations

from typing import Any

import anthropic

from pmos.adapters.base import (
    MalformedResponseError,
    ModelAdapter,
    QuotaError,
    Response,
    TransientError,
)


class ClaudeAdapter(ModelAdapter):
    DEFAULT_MODEL = "claude-sonnet-4-6"
    DEFAULT_MAX_TOKENS = 8192

    def __init__(
        self,
        *,
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: anthropic.Anthropic | None = None,
    ):
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens
        self.client = client or anthropic.Anthropic()

    def call(
        self,
        prompt: str,
        *,
        system: str | None = None,
        **kwargs: Any,
    ) -> Response:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system or anthropic.NOT_GIVEN,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
        except (anthropic.APIConnectionError, anthropic.APITimeoutError) as e:
            raise TransientError(f"connection/timeout: {e}") from e
        except anthropic.RateLimitError as e:
            raise TransientError(f"rate limited: {e}") from e
        except anthropic.InternalServerError as e:
            raise TransientError(f"server error: {e}") from e
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as e:
            raise QuotaError(f"auth/permission: {e}") from e
        except anthropic.APIStatusError as e:
            # Other 4xx — BadRequest, NotFound, UnprocessableEntity, etc.
            raise MalformedResponseError(f"api status {e.status_code}: {e}") from e

        # Extract text from response content blocks
        text_parts = [block.text for block in message.content if hasattr(block, "text")]
        text = "".join(text_parts)
        if not text:
            raise MalformedResponseError("claude response had no text content")

        return Response(
            text=text,
            tokens_in=message.usage.input_tokens,
            tokens_out=message.usage.output_tokens,
            model=message.model,
            raw=message,
        )
