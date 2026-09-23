"""Client-side token-bucket rate limiter with optional adaptive backoff."""

import logging
import time
from logging import Logger, getLogger
from typing import Any

from britecore_sdk.base_logger import LogCategory, log_with_category

LOGGER: Logger = getLogger("britecore_sdk")


class RateLimiter:
    """Client-side rate limiter using token bucket semantics."""

    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst_size: int = 20,
        adaptive_backoff_enabled: bool = True,
        backoff_timeout_seconds: float = 60.0,
    ) -> None:
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
        self._backoff_until: float = 0.0

    def acquire(self, timeout: float | None = None) -> float:
        """Acquire one token, waiting as needed, and return wait duration."""
        start_time = time.monotonic()

        while True:
            now = time.monotonic()

            if self._backoff_until > now:
                backoff_remaining = self._backoff_until - now
                if (
                    timeout is not None
                    and (now - start_time) + backoff_remaining > timeout
                ):
                    elapsed = now - start_time
                    log_with_category(
                        LOGGER,
                        logging.DEBUG,
                        "Rate limiter acquire timeout during backoff",
                        LogCategory.RATE_LIMIT,
                        event="rate_limit_timeout_backoff",
                        timeout_seconds=timeout,
                        elapsed_seconds=round(elapsed, 6),
                    )
                    raise TimeoutError(
                        f"Rate limit acquire exceeded timeout ({timeout}s) after {elapsed:.2f}s"
                    )
                time.sleep(min(backoff_remaining, 0.01))
                continue

            elapsed_since_refill = now - self._last_refill_time
            tokens_to_add = elapsed_since_refill * self.requests_per_second
            self._tokens = min(self._tokens + tokens_to_add, float(self.burst_size))
            self._last_refill_time = now

            if self._tokens >= 1.0:
                self._tokens -= 1.0
                elapsed = now - start_time
                if elapsed > 0:
                    log_with_category(
                        LOGGER,
                        logging.DEBUG,
                        "Rate limiter delayed request",
                        LogCategory.RATE_LIMIT,
                        event="rate_limit_wait",
                        wait_seconds=round(elapsed, 6),
                    )
                return elapsed

            wait_time = (1.0 - self._tokens) / self.requests_per_second
            total_wait = (now - start_time) + wait_time
            if timeout is not None and total_wait > timeout:
                elapsed = now - start_time
                log_with_category(
                    LOGGER,
                    logging.DEBUG,
                    "Rate limiter acquire timeout waiting for token",
                    LogCategory.RATE_LIMIT,
                    event="rate_limit_timeout_token_wait",
                    timeout_seconds=timeout,
                    elapsed_seconds=round(elapsed, 6),
                )
                raise TimeoutError(
                    f"Rate limit acquire exceeded timeout ({timeout}s) after {elapsed:.2f}s"
                )

            time.sleep(min(wait_time, 0.01))

    def record_rate_limit_response(self, retry_after: int | None = None) -> None:
        """Record a 429 response and activate adaptive backoff when enabled."""
        if not self._adaptive_backoff_enabled:
            log_with_category(
                LOGGER,
                logging.DEBUG,
                "Rate limit response received but adaptive backoff disabled",
                LogCategory.RATE_LIMIT,
                event="rate_limit_backoff_disabled",
            )
            return

        now = time.monotonic()
        backoff_duration = (
            retry_after if retry_after is not None else self._backoff_timeout
        )
        self._backoff_until = now + backoff_duration
        log_with_category(
            LOGGER,
            logging.WARNING,
            "Rate limit response received, entering adaptive backoff",
            LogCategory.RATE_LIMIT,
            event="rate_limit_backoff_started",
            backoff_seconds=round(backoff_duration, 6),
        )

    def reset(self) -> None:
        """Reset backoff and token bucket state to initial values."""
        self._tokens = float(self.burst_size)
        self._last_refill_time = time.monotonic()
        self._backoff_until = 0.0
        log_with_category(
            LOGGER,
            logging.DEBUG,
            "Rate limiter reset to initial state",
            LogCategory.RATE_LIMIT,
            event="rate_limit_reset",
            burst_size=self.burst_size,
            requests_per_second=self.requests_per_second,
        )

    def get_state(self) -> dict[str, Any]:
        """Return a snapshot of internal limiter state."""
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
