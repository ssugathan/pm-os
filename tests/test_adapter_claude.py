"""ClaudeAdapter tests — mocked client, error classification, response shape.

These never hit the real Anthropic API. A live smoke test (gated by
ANTHROPIC_API_KEY env var) can be added later if useful — for now mocks are
sufficient to verify the adapter's behavior.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import anthropic
import httpx
import pytest

from pmos.adapters.claude import ClaudeAdapter
from pmos.adapters.base import (
    MalformedResponseError,
    QuotaError,
    Response,
    TransientError,
)


def _fake_message(text: str = "hi", model: str = "claude-sonnet-4-6") -> SimpleNamespace:
    """Build a fake anthropic message response with the shape the adapter expects."""
    return SimpleNamespace(
        content=[SimpleNamespace(text=text, type="text")],
        usage=SimpleNamespace(input_tokens=12, output_tokens=4),
        model=model,
    )


def _api_status_error(cls: type, status_code: int, msg: str = "err") -> Exception:
    """Construct an anthropic.APIStatusError subclass for tests."""
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(status_code=status_code, request=req)
    return cls(message=msg, response=resp, body=None)


def test_call_returns_response_on_success():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_message(text="hello world")
    adapter = ClaudeAdapter(client=mock_client)

    result = adapter.call("test prompt")

    assert isinstance(result, Response)
    assert result.text == "hello world"
    assert result.tokens_in == 12
    assert result.tokens_out == 4
    assert result.model == "claude-sonnet-4-6"
    # The mock client was called with the right shape
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-sonnet-4-6"
    assert call_kwargs["messages"] == [{"role": "user", "content": "test prompt"}]


def test_call_passes_system_prompt_when_provided():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_message()
    adapter = ClaudeAdapter(client=mock_client)

    adapter.call("hi", system="You are helpful.")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["system"] == "You are helpful."


def test_call_uses_NOT_GIVEN_when_system_omitted():
    """Omitted system should pass anthropic.NOT_GIVEN, not empty string."""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_message()
    adapter = ClaudeAdapter(client=mock_client)

    adapter.call("hi")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["system"] is anthropic.NOT_GIVEN


def test_custom_model_and_max_tokens():
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_message()
    adapter = ClaudeAdapter(client=mock_client, model="claude-opus-4-7", max_tokens=2048)

    adapter.call("hi")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-opus-4-7"
    assert call_kwargs["max_tokens"] == 2048


# ---------- Error classification ----------


def test_rate_limit_becomes_transient():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = _api_status_error(
        anthropic.RateLimitError, 429, "rate limited"
    )
    adapter = ClaudeAdapter(client=mock_client)

    with pytest.raises(TransientError, match="rate limited"):
        adapter.call("hi")


def test_internal_server_error_becomes_transient():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = _api_status_error(
        anthropic.InternalServerError, 500, "boom"
    )
    adapter = ClaudeAdapter(client=mock_client)

    with pytest.raises(TransientError):
        adapter.call("hi")


def test_connection_error_becomes_transient():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.APIConnectionError(
        request=httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    )
    adapter = ClaudeAdapter(client=mock_client)

    with pytest.raises(TransientError):
        adapter.call("hi")


def test_authentication_error_becomes_quota():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = _api_status_error(
        anthropic.AuthenticationError, 401, "bad key"
    )
    adapter = ClaudeAdapter(client=mock_client)

    with pytest.raises(QuotaError):
        adapter.call("hi")


def test_permission_denied_becomes_quota():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = _api_status_error(
        anthropic.PermissionDeniedError, 403, "forbidden"
    )
    adapter = ClaudeAdapter(client=mock_client)

    with pytest.raises(QuotaError):
        adapter.call("hi")


def test_bad_request_becomes_malformed():
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = _api_status_error(
        anthropic.BadRequestError, 400, "bad prompt"
    )
    adapter = ClaudeAdapter(client=mock_client)

    with pytest.raises(MalformedResponseError, match="api status 400"):
        adapter.call("hi")


def test_empty_response_becomes_malformed():
    """A successful API call that returns no text content is malformed."""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = SimpleNamespace(
        content=[],
        usage=SimpleNamespace(input_tokens=5, output_tokens=0),
        model="claude-sonnet-4-6",
    )
    adapter = ClaudeAdapter(client=mock_client)

    with pytest.raises(MalformedResponseError, match="no text content"):
        adapter.call("hi")
