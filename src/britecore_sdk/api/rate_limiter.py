"""
Client-side rate limiting for BriteCore API requests.

This module provides a token bucket-based rate limiter that can be optionally
enabled on a per-client basis. The rate limiter respects server-provided
rate limit headers (Retry-After) and supports both strict and adaptive modes.

Rate Limiting Strategy:
    - **Token Bucket Algorithm**: Tokens are added at a fixed rate (requests_per_second).
      Each request consumes one token. If no tokens are available, the request is delayed.
    - **Burst Capacity**: The bucket can hold up to burst_size tokens, allowing short bursts
      of traffic up to that limit.
    - **Adaptive Mode**: When a 429 response is received, the rate limiter automatically
      backs off and reduces the request rate until the server recovers.

Configuration:
    - `enabled`: Enable/disable the rate limiter (default: False)
    - `requests_per_second`: Target request rate (default: 10 req/s)
    - `burst_size`: Maximum burst capacity (default: 20 requests)
    - `adaptive_backoff`: Enable automatic backoff on 429 (default: True)
    - `backoff_timeout_seconds`: How long to back off after 429 (default: 60s)

Example::

    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    # Enable rate limiting at client init
    client = BritecoreAPIClient("my_site").init_client(
        enable_rate_limiter=True,
        rate_limiter_requests_per_second=5,
        rate_limiter_burst_size=10,
    )

    # Requests will now be rate-limited
    result = client.do_request(path="/api/v2/policies")

    # Per-request override via dry_run or other params (optional)
    # Future: rate_limiter_bypass=True to skip rate limiting for specific calls
"""

import time
from logging import Logger, getLogger
from typing import Any

LOGGER: Logger = getLogger("britecore_sdk")


class RateLimiter:
    """
    Client-side rate limiter using token bucket algorithm.

    Implements a token bucket with fixed replenishment rate. Each request
    consumes one token; if none are available, the request is delayed until
    tokens become available (or the bucket refills).

    All state is instance-level; multiple rate limiters can coexist in the
    same process without interfering.

    Attributes:
        requests_per_second: Target request rate (tokens added per second).
        burst_size: Maximum number of tokens the bucket can hold.
        _tokens: Current token count (float for sub-second granularity).
        _last_refill_time: Timestamp of the last token refill.
        _backoff_until: Timestamp until which rate limiting is backed off (adaptive mode).
        _adaptive_backoff_enabled: Whether to enable automatic backoff on 429.
        _backoff_timeout: How long to back off after a 429 response.
    """

    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: int = 20,
        adaptive_backoff_enabled: bool = True,
        backoff_timeout_seconds: float = 60.0,
    ) -> None:
        """
        Initialize the rate limiter with token bucket parameters.

        Args:
            requests_per_second: Rate at which tokens are added to the bucket.
                Default: 10.0 requests per second.
            burst_size: Maximum number of tokens to hold in the bucket.
                Default: 20 requests (allows 2x burst).
            adaptive_backoff_enabled: If True, automatically reduce rate on 429 responses.
                Default: True.
            backoff_timeout_seconds: Duration (in seconds) to back off after a 429.
                Default: 60.0 seconds.

        Raises:
            ValueError: If requests_per_second <= 0 or burst_size < 1.
        """
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if burst_size < 1:
            raise ValueError("burst_size must be at least 1")

        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self._adaptive_backoff_enabled = adaptive_backoff_enabled
        self._backoff_timeout = backoff_timeout_seconds

        self._tokens: float = float(burst_size)
        self._last_refill_time: float = time.monotonic()
        self._backoff_until: float = 0.0  # Timestamp; 0 = no backoff active

    def acquire(self, timeout: float | None = None) -> float:
        """
        Acquire one token from the bucket, blocking if necessary.

        This method waits until a token is available, then returns. If timeout
        is specified and is exceeded, returns the wait time actually elapsed
        (not capped at timeout), allowing callers to distinguish over-timeout waits.

        Args:
            timeout: Maximum time in seconds to wait for a token.
                If None, wait indefinitely (blocking behavior).

        Returns:
            The time in seconds that the caller was delayed (0.0 if no wait).

        Raises:
            TimeoutError: If timeout is exceeded before a token is available.

        Example::

            limiter = RateLimiter(requests_per_second=10)
            delay = limiter.acquire()
            if delay > 0:
                LOGGER.debug(f"Rate limited: delayed {delay:.2f}s")
        """
        start_time = time.monotonic()

        while True:
            now = time.monotonic()

            # Check if we're in backoff period
            if self._backoff_until > now:
                # In backoff; wait for backoff to expire
                backoff_remaining = self._backoff_until - now
                if timeout is not None and (now - start_time) + backoff_remaining > timeout:
                    elapsed = now - start_time
                    raise TimeoutError(
                        f"Rate limit acquire exceeded timeout ({timeout}s) after {elapsed:.2f}s"
                    )
                time.sleep(min(backoff_remaining, 0.01))  # Short sleep before retrying
                continue

            # Refill tokens based on elapsed time since last refill
            elapsed_since_refill = now - self._last_refill_time
            tokens_to_add = elapsed_since_refill * self.requests_per_second
            self._tokens = min(self._tokens + tokens_to_add, float(self.burst_size))
            self._last_refill_time = now

            # Try to acquire one token
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                elapsed = now - start_time
                return elapsed

            # No token available; calculate wait time and check timeout
            wait_time = (1.0 - self._tokens) / self.requests_per_second
            total_wait = (now - start_time) + wait_time

            if timeout is not None and total_wait > timeout:
                elapsed = now - start_time
                raise TimeoutError(
                    f"Rate limit acquire exceeded timeout ({timeout}s) after {elapsed:.2f}s"
                )

            # Sleep for a short interval and retry
            time.sleep(min(wait_time, 0.01))

    def record_rate_limit_response(self, retry_after: int | None = None) -> None:
        """
        Record that a 429 (rate limited) response was received from the server.

        In adaptive backoff mode, this method reduces the request rate to back off
        gracefully. The rate reduction remains in effect until backoff_timeout is
        exceeded, at which point normal rate limiting resumes.

        Args:
            retry_after: Optional Retry-After header value (in seconds) from the server.
                If provided and adaptive backoff is enabled, the backoff duration
                is increased to at least this value. If None, uses backoff_timeout.
        """
        if not self._adaptive_backoff_enabled:
            return

        now = time.monotonic()
        backoff_duration = retry_after if retry_after is not None else self._backoff_timeout
        self._backoff_until = now + backoff_duration

        LOGGER.warning(
            "Rate limit response received, backing off for %.1f seconds "
            "(adaptive_backoff_enabled=True)",
            backoff_duration,
        )

    def reset(self) -> None:
        """
        Reset the rate limiter to its initial state.

        Clears any active backoff and resets the token bucket to full capacity.
        Useful for testing or when switching configurations.
        """
        self._tokens = float(self.burst_size)
        self._last_refill_time = time.monotonic()
        self._backoff_until = 0.0
        LOGGER.debug("Rate limiter reset to initial state")

    def get_state(self) -> dict[str, Any]:
        """
        Return a snapshot of the rate limiter's current state (for debugging).

        Returns:
            Dictionary with keys:
                - tokens: Current token count
                - burst_size: Maximum burst capacity
                - requests_per_second: Token replenishment rate
                - in_backoff: True if currently backing off
                - backoff_remaining: Seconds until backoff ends (0 if not backing off)
        """
        now = time.monotonic()
        in_backoff = self._backoff_until > now
        backoff_remaining = max(0.0, self._backoff_until - now)

        return {
            "tokens": self._tokens,
            "burst_size": self.burst_size,
            "requests_per_second": self.requests_per_second,
            "in_backoff": in_backoff,
            "backoff_remaining": backoff_remaining,
        }

    def __repr__(self) -> str:
        state = self.get_state()
        return (
            f"RateLimiter("
            f"requests_per_second={self.requests_per_second}, "
            f"burst_size={self.burst_size}, "
            f"tokens={state['tokens']:.2f}, "
            f"in_backoff={state['in_backoff']}"
            f")"
        )

