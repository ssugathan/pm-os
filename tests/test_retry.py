"""retry_call tests — error classification, backoff sequence, exhaustion, callback."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from pmos.adapters.base import MalformedResponseError, QuotaError, TransientError
from pmos.config import RetryConfig
from pmos.retry import RetryExhaustedError, retry_call


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Stub time.sleep so tests don't actually wait."""
    monkeypatch.setattr("pmos.retry.time.sleep", lambda s: None)


def test_success_on_first_try_returns_value():
    fn = MagicMock(return_value="ok")
    result = retry_call(fn, policy=RetryConfig())
    assert result == "ok"
    assert fn.call_count == 1


def test_transient_then_success_retries_once():
    fn = MagicMock(side_effect=[TransientError("t1"), "ok"])
    on_retry = MagicMock()
    result = retry_call(fn, policy=RetryConfig(), on_retry=on_retry)
    assert result == "ok"
    assert fn.call_count == 2
    on_retry.assert_called_once()
    props = on_retry.call_args.args[0]
    assert props["error_type"] == "transient"
    assert props["retry_num"] == 1
    assert props["sleep_seconds"] == 2  # first backoff in default policy


def test_all_transient_raises_retry_exhausted_at_cap():
    fn = MagicMock(side_effect=TransientError("always fails"))
    with pytest.raises(RetryExhaustedError, match="after 5 retries"):
        retry_call(fn, policy=RetryConfig(max_attempts=5))
    # initial + 5 retries = 6 total calls
    assert fn.call_count == 6


def test_backoff_sequence_follows_policy():
    """Verify the backoff sleeps use the policy.backoff_seconds values in order."""
    fn = MagicMock(side_effect=[TransientError("e")] * 3 + ["ok"])
    on_retry = MagicMock()
    retry_call(fn, policy=RetryConfig(), on_retry=on_retry)
    sleeps = [c.args[0]["sleep_seconds"] for c in on_retry.call_args_list]
    assert sleeps == [2, 4, 8]


def test_backoff_clamps_to_last_value_if_more_retries_than_backoffs():
    """If max_attempts > len(backoff_seconds), the last backoff value is reused."""
    fn = MagicMock(side_effect=[TransientError("e")] * 7 + ["ok"])
    on_retry = MagicMock()
    retry_call(
        fn,
        policy=RetryConfig(max_attempts=10, backoff_seconds=[2, 4, 8]),
        on_retry=on_retry,
    )
    sleeps = [c.args[0]["sleep_seconds"] for c in on_retry.call_args_list]
    assert sleeps == [2, 4, 8, 8, 8, 8, 8]


def test_quota_error_propagates_immediately():
    fn = MagicMock(side_effect=QuotaError("billing"))
    on_retry = MagicMock()
    with pytest.raises(QuotaError, match="billing"):
        retry_call(fn, policy=RetryConfig(), on_retry=on_retry)
    assert fn.call_count == 1
    on_retry.assert_called_once()
    assert on_retry.call_args.args[0]["error_type"] == "quota"


def test_malformed_then_success_no_sleep():
    fn = MagicMock(side_effect=[MalformedResponseError("bad"), "ok"])
    on_retry = MagicMock()
    result = retry_call(fn, policy=RetryConfig(), on_retry=on_retry)
    assert result == "ok"
    assert fn.call_count == 2
    on_retry.assert_called_once()
    props = on_retry.call_args.args[0]
    assert props["error_type"] == "malformed"
    assert props["sleep_seconds"] == 0


def test_malformed_exhausts_at_cap():
    fn = MagicMock(side_effect=MalformedResponseError("bad"))
    with pytest.raises(RetryExhaustedError, match="malformed responses after 2 retries"):
        retry_call(fn, policy=RetryConfig(malformed_response_retries=2))
    # 1 initial + 2 retries = 3 calls before raising
    assert fn.call_count == 3


def test_unknown_exception_propagates():
    """Unexpected exceptions are not caught — treated as bugs, not retried."""
    fn = MagicMock(side_effect=ValueError("unexpected"))
    with pytest.raises(ValueError, match="unexpected"):
        retry_call(fn, policy=RetryConfig())
    assert fn.call_count == 1


def test_mixed_transient_and_malformed_counts_separately():
    """A transient retry shouldn't burn a malformed retry slot or vice versa."""
    fn = MagicMock(
        side_effect=[
            TransientError("t1"),
            MalformedResponseError("m1"),
            TransientError("t2"),
            "ok",
        ]
    )
    on_retry = MagicMock()
    result = retry_call(fn, policy=RetryConfig(), on_retry=on_retry)
    assert result == "ok"
    assert fn.call_count == 4
    types = [c.args[0]["error_type"] for c in on_retry.call_args_list]
    assert types == ["transient", "malformed", "transient"]
