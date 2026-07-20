"""Request timing middleware for performance monitoring.

Tracks and logs request timing to identify bottlenecks.
"""

import time
from typing import Any, Callable

from britecore_sdk.base_logger import LogCategory, log_with_category
from logging import Logger, getLogger

SLOW_REQUEST_THRESHOLD_MS = 1000  # Warn if request takes > 1 second


class TimingMiddleware:
    """Track and log request timing for performance monitoring."""

    def __init__(
        self,
        logger: Logger | None = None,
        slow_threshold_ms: float = SLOW_REQUEST_THRESHOLD_MS,
    ):
        """Initialize timing middleware.

        Args:
            logger: Logger instance (uses britecore_sdk logger if None).
            slow_threshold_ms: Threshold in milliseconds for "slow" requests.
        """
        self._logger = logger or getLogger("britecore_sdk")
        self._slow_threshold_ms = slow_threshold_ms
        self._timings: dict[str, float] = {}

    def on_request_start(self, req_id: str, path: str, method: str) -> None:
        """Record request start time.

        Args:
            req_id: Request correlation ID.
            path: Request path.
            method: HTTP method (GET, POST, etc.).
        """
        self._timings[req_id] = time.time()
        log_with_category(
            self._logger,
            10,  # DEBUG level
            f"Request started: {method} {path}",
            LogCategory.PERF,
            request_id=req_id,
            method=method,
            path=path,
        )

    def on_request_end(self, req_id: str, method: str, path: str, status_code: int) -> None:
        """Record request end and log timing.

        Args:
            req_id: Request correlation ID.
            method: HTTP method.
            path: Request path.
            status_code: HTTP response status code.
        """
        if req_id not in self._timings:
            return

        elapsed_sec = time.time() - self._timings.pop(req_id)
        elapsed_ms = elapsed_sec * 1000

        log_with_category(
            self._logger,
            20,  # INFO level
            f"[{req_id}] {method} {path}: {elapsed_ms:.1f}ms ({status_code})",
            LogCategory.PERF,
            request_id=req_id,
            method=method,
            path=path,
            status_code=status_code,
            elapsed_ms=elapsed_ms,
        )

        # Warn if slow
        if elapsed_ms > self._slow_threshold_ms:
            log_with_category(
                self._logger,
                30,  # WARNING level
                f"[{req_id}] Slow request: {method} {path} took {elapsed_ms:.1f}ms",
                LogCategory.PERF,
                request_id=req_id,
                is_slow=True,
            )

    def wrap_request_function(
        self,
        func: Callable[..., Any],
        method: str,
        path: str,
    ) -> Callable[..., Any]:
        """Wrap a request function to add timing.

        Args:
            func: Request function to wrap.
            method: HTTP method.
            path: Request path.

        Returns:
            Wrapped function with timing.
        """
        def wrapper(*args, **kwargs) -> Any:
            import uuid
            req_id = str(uuid.uuid4())[:8]

            self.on_request_start(req_id, path, method)
            try:
                result = func(*args, **kwargs)
                status_code = getattr(result, "status", 200)
                self.on_request_end(req_id, method, path, status_code)
                return result
            except Exception as e:
                # Still log timing on error
                self.on_request_end(req_id, method, path, 0)
                raise

        return wrapper


# Global middleware instance
_timing_middleware: TimingMiddleware | None = None


def get_timing_middleware(
    slow_threshold_ms: float = SLOW_REQUEST_THRESHOLD_MS,
) -> TimingMiddleware:
    """Get or create the global timing middleware instance.

    Args:
        slow_threshold_ms: Threshold for slow request warnings.

    Returns:
        TimingMiddleware instance.
    """
    global _timing_middleware
    if _timing_middleware is None:
        _timing_middleware = TimingMiddleware(slow_threshold_ms=slow_threshold_ms)
    return _timing_middleware


def reset_timing_middleware() -> None:
    """Reset the global timing middleware."""
    global _timing_middleware
    _timing_middleware = None


__all__ = [
    "TimingMiddleware",
    "get_timing_middleware",
    "reset_timing_middleware",
]

