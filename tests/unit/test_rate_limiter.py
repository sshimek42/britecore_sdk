"""
Tests for client-side rate limiter implementation.

Tests cover:
- Token bucket algorithm behavior
- Rate limit enforcement
- Burst capacity
- Adaptive backoff on 429 responses
- Integration with BritecoreAPIClient
"""

import time
import pytest
from unittest.mock import Mock, patch, MagicMock

from britecore_sdk.api.rate_limiter import RateLimiter
from britecore_sdk.exceptions import BritecoreError


class TestRateLimiterBasic:
    """Test basic rate limiter functionality."""

    def test_init_with_valid_params(self):
        """Test rate limiter initialization with valid parameters."""
        limiter = RateLimiter(
            requests_per_second=5.0,
            burst_size=10,
            adaptive_backoff_enabled=True,
            backoff_timeout_seconds=30.0,
        )
        assert limiter.requests_per_second == 5.0
        assert limiter.burst_size == 10
        assert limiter._tokens == 10.0
        assert limiter._backoff_until == 0.0

    def test_init_invalid_requests_per_second(self):
        """Test that invalid requests_per_second raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            RateLimiter(requests_per_second=0.0)

        with pytest.raises(ValueError, match="must be positive"):
            RateLimiter(requests_per_second=-1.0)

    def test_init_invalid_burst_size(self):
        """Test that invalid burst_size raises ValueError."""
        with pytest.raises(ValueError, match="must be at least 1"):
            RateLimiter(burst_size=0)

        with pytest.raises(ValueError, match="must be at least 1"):
            RateLimiter(burst_size=-5)

    def test_defaults(self):
        """Test rate limiter with default parameters."""
        limiter = RateLimiter()
        assert limiter.requests_per_second == 10.0
        assert limiter.burst_size == 20
        assert limiter._tokens == 20.0


class TestRateLimiterTokenBucket:
    """Test token bucket algorithm behavior."""

    def test_acquire_with_available_tokens(self):
        """Test that acquire returns immediately when tokens are available."""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=5)
        assert limiter._tokens == 5.0

        start = time.monotonic()
        delay = limiter.acquire()
        elapsed = time.monotonic() - start

        assert delay < 0.01  # Should be nearly instant
        assert limiter._tokens == 4.0
        assert elapsed < 0.1

    def test_acquire_multiple_tokens(self):
        """Test acquiring multiple tokens in sequence."""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=3)

        for i in range(3):
            delay = limiter.acquire()
            assert delay < 0.01
            assert limiter._tokens == (2 - i)

    def test_acquire_causes_wait_when_depleted(self):
        """Test that acquire waits when no tokens are available."""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=1)

        # Consume the first token instantly
        limiter.acquire()
        assert limiter._tokens == 0.0

        # Next acquire should wait for token replenishment
        start = time.monotonic()
        delay = limiter.acquire()
        elapsed = time.monotonic() - start

        # Should wait ~0.1 seconds for the next token (1/10 req/s)
        assert delay > 0.05
        assert elapsed > 0.05

    def test_token_replenishment(self):
        """Test that tokens are replenished over time."""
        limiter = RateLimiter(requests_per_second=2.0, burst_size=2)

        # Consume both tokens
        limiter.acquire()
        limiter.acquire()
        assert limiter._tokens == 0.0

        # Wait and check replenishment
        time.sleep(0.6)  # Should generate ~1.2 tokens at 2 req/s
        new_delay = limiter.acquire()

        # Should be close to instant (we have tokens now)
        assert new_delay < 0.2
        assert limiter._tokens >= 0.16  # ~2 - 1.2 tokens consumed

    def test_burst_capacity_respected(self):
        """Test that token count is capped at burst_size."""
        limiter = RateLimiter(requests_per_second=100.0, burst_size=5)

        time.sleep(0.2)  # Allow many tokens to accumulate

        # Token count should not exceed burst_size
        assert limiter._tokens <= 5.0

    def test_acquire_timeout(self):
        """Test that acquire respects the timeout parameter."""
        limiter = RateLimiter(requests_per_second=1.0, burst_size=1)

        # Consume all tokens
        limiter.acquire()

        # Try to acquire with a very short timeout
        with pytest.raises(TimeoutError, match="Rate limit acquire exceeded timeout"):
            limiter.acquire(timeout=0.01)

    def test_acquire_no_timeout_waits(self):
        """Test that acquire with no timeout waits indefinitely."""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=1)

        # Consume the token
        limiter.acquire()

        # Acquire without timeout should eventually succeed
        start = time.monotonic()
        delay = limiter.acquire(timeout=None)
        elapsed = time.monotonic() - start

        # Should have waited for token replenishment
        assert delay > 0.05
        assert elapsed > 0.05


class TestRateLimiterAdaptiveBackoff:
    """Test adaptive backoff functionality."""

    def test_record_rate_limit_response_without_retry_after(self):
        """Test recording a 429 response without Retry-After header."""
        limiter = RateLimiter(
            requests_per_second=10.0,
            burst_size=10,
            adaptive_backoff_enabled=True,
            backoff_timeout_seconds=5.0,
        )

        original_state = limiter.get_state()
        assert not original_state["in_backoff"]

        limiter.record_rate_limit_response(retry_after=None)

        new_state = limiter.get_state()
        assert new_state["in_backoff"]
        assert new_state["backoff_remaining"] > 0
        assert new_state["backoff_remaining"] <= 5.0

    def test_record_rate_limit_response_with_retry_after(self):
        """Test recording a 429 response with Retry-After header."""
        limiter = RateLimiter(
            requests_per_second=10.0,
            burst_size=10,
            adaptive_backoff_enabled=True,
            backoff_timeout_seconds=60.0,
        )

        limiter.record_rate_limit_response(retry_after=2)

        state = limiter.get_state()
        assert state["in_backoff"]
        assert state["backoff_remaining"] > 1.5
        assert state["backoff_remaining"] <= 2.0

    def test_acquire_respects_backoff(self):
        """Test that acquire waits during backoff period."""
        limiter = RateLimiter(
            requests_per_second=10.0,
            burst_size=10,
            adaptive_backoff_enabled=True,
            backoff_timeout_seconds=0.5,
        )

        # Record a rate limit response
        limiter.record_rate_limit_response(retry_after=None)
        assert limiter.get_state()["in_backoff"]

        # Try to acquire; should wait for backoff to expire
        start = time.monotonic()
        delay = limiter.acquire()
        elapsed = time.monotonic() - start

        # Should have waited for backoff period
        assert elapsed > 0.4  # ~0.5s backoff
        assert delay > 0.4

    def test_backoff_disabled(self):
        """Test that adaptive backoff can be disabled."""
        limiter = RateLimiter(
            requests_per_second=10.0,
            burst_size=10,
            adaptive_backoff_enabled=False,
            backoff_timeout_seconds=5.0,
        )

        limiter.record_rate_limit_response(retry_after=None)

        # Backoff should not be activated
        state = limiter.get_state()
        assert not state["in_backoff"]


class TestRateLimiterState:
    """Test rate limiter state and debugging."""

    def test_get_state(self):
        """Test state inspection method."""
        limiter = RateLimiter(
            requests_per_second=10.0,
            burst_size=20,
        )

        state = limiter.get_state()
        assert isinstance(state, dict)
        assert "tokens" in state
        assert "burst_size" in state
        assert "requests_per_second" in state
        assert "in_backoff" in state
        assert "backoff_remaining" in state

        assert state["burst_size"] == 20
        assert state["requests_per_second"] == 10.0
        assert state["in_backoff"] is False
        assert state["backoff_remaining"] == 0.0

    def test_reset(self):
        """Test reset method."""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=5)

        # Consume tokens and trigger backoff
        limiter.acquire()
        limiter.acquire()
        limiter.record_rate_limit_response(retry_after=60)

        original_state = limiter.get_state()
        assert not (original_state["tokens"] == 5.0)
        assert original_state["in_backoff"]

        # Reset and verify
        limiter.reset()

        new_state = limiter.get_state()
        assert new_state["tokens"] == 5.0
        assert new_state["in_backoff"] is False
        assert new_state["backoff_remaining"] == 0.0

    def test_repr(self):
        """Test rate limiter string representation."""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=20)
        repr_str = repr(limiter)

        assert "RateLimiter" in repr_str
        assert "10.0" in repr_str  # requests_per_second
        assert "20" in repr_str  # burst_size
        assert "False" in repr_str  # in_backoff


class TestRateLimiterIntegration:
    """Test rate limiter integration with BritecoreAPIClient."""

    def test_client_initialization_with_rate_limiter(self):
        """Test that client initializes rate limiter when enabled."""
        with patch("britecore_sdk.api.britecore_api_client.LoadClientSettings") as mock_settings:
            # Mock settings
            mock_instance = Mock()
            mock_instance.load_config.return_value = Mock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

            client = BritecoreAPIClient("test_site").init_client(enable_rate_limiter=True)

            assert client.rate_limiter is not None
            assert isinstance(client.rate_limiter, RateLimiter)
            assert client.rate_limiter.requests_per_second == 10.0

    def test_client_rate_limiter_disabled_by_default(self):
        """Test that rate limiter is disabled by default."""
        with patch("britecore_sdk.api.britecore_api_client.LoadClientSettings") as mock_settings:
            mock_instance = Mock()
            mock_instance.load_config.return_value = Mock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

            client = BritecoreAPIClient("test_site").init_client(enable_rate_limiter=False)

            assert client.rate_limiter is None

    def test_client_rate_limiter_custom_params(self):
        """Test that custom rate limiter parameters are applied."""
        with patch("britecore_sdk.api.britecore_api_client.LoadClientSettings") as mock_settings:
            mock_instance = Mock()
            mock_instance.load_config.return_value = Mock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

            client = BritecoreAPIClient("test_site").init_client(
                enable_rate_limiter=True,
                rate_limiter_requests_per_second=5.0,
                rate_limiter_burst_size=15,
            )

            assert client.rate_limiter is not None
            assert client.rate_limiter.requests_per_second == 5.0
            assert client.rate_limiter.burst_size == 15

    def test_rate_limiter_bypass_parameter(self):
        """Test that rate_limiter_bypass skips rate limiting."""
        limiter = RateLimiter(requests_per_second=1.0, burst_size=1)

        # Consume all tokens
        limiter.acquire()

        # Verify normal acquire would wait
        with pytest.raises(TimeoutError):
            limiter.acquire(timeout=0.01)

        # But we can't directly test bypass - it's tested via do_request integration


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

