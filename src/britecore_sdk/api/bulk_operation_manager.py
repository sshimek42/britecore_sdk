"""Bulk operation manager with exponential backoff retry logic.

Provides context manager for reliable bulk operations with automatic retries.
"""

import asyncio
import time
from typing import Any, Callable, Optional


class BulkOperationManager:
    """Context manager for bulk operations with automatic retry on failures.

    Example::

        with BulkOperationManager(max_retries=3, backoff_factor=2) as bulk:
            for policy_data in policies_to_create:
                bulk.add_operation(policies.create_policy, policy_data=policy_data)
            results = bulk.execute()
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        backoff_max_seconds: float = 60.0,
        retry_on: list[int] | None = None,
        on_retry: Optional[Callable[[Exception, int, float], None]] = None,
    ):
        """Initialize bulk operation manager.

        Args:
            max_retries: Maximum number of retry attempts.
            backoff_factor: Multiplier for exponential backoff.
            backoff_max_seconds: Maximum seconds to wait between retries.
            retry_on: HTTP status codes to retry on (default: [429, 503]).
            on_retry: Callback function called on retry with (exception, attempt, wait_time).
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.backoff_max_seconds = backoff_max_seconds
        self.retry_on = retry_on or [429, 503]  # Rate limit and Service Unavailable
        self.on_retry = on_retry
        self.operations: list[tuple[Callable[..., Any], dict[str, Any]]] = []
        self.results: list[dict[str, Any]] = []
        self.failed: list[dict[str, Any]] = []

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass

    def add_operation(
        self,
        func: Callable[..., Any],
        **kwargs: Any,
    ) -> None:
        """Add an operation to the bulk queue.

        Args:
            func: Function to call for this operation.
            **kwargs: Keyword arguments to pass to the function.
        """
        self.operations.append((func, kwargs))

    def execute(self) -> dict[str, Any]:
        """Execute all operations with retries.

        Returns:
            Dictionary with results and failure information::

                {
                    "total": 100,
                    "succeeded": 95,
                    "failed": 5,
                    "results": [...],
                    "errors": [...]
                }
        """
        self.results = []
        self.failed = []

        for idx, (func, kwargs) in enumerate(self.operations):
            result = self._execute_with_retry(func, kwargs, operation_index=idx)
            if result["success"]:
                self.results.append(result)
            else:
                self.failed.append(result)

        return {
            "total": len(self.operations),
            "succeeded": len(self.results),
            "failed": len(self.failed),
            "results": self.results,
            "errors": self.failed,
        }

    def _execute_with_retry(
        self,
        func: Callable[..., Any],
        kwargs: dict[str, Any],
        operation_index: int = 0,
    ) -> dict[str, Any]:
        """Execute a single operation with retries.

        Args:
            func: Function to call.
            kwargs: Keyword arguments.
            operation_index: Index in operation list (for tracking).

        Returns:
            Result dictionary with success/error information.
        """
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                result = func(**kwargs)
                return {
                    "success": True,
                    "operation_index": operation_index,
                    "attempt": attempt + 1,
                    "result": result,
                    "error": None,
                }
            except Exception as e:
                last_error = e

                # Determine if we should retry
                should_retry = self._should_retry(e, attempt)

                if not should_retry or attempt >= self.max_retries:
                    # Don't retry or we've exhausted retries
                    break

                # Calculate backoff time
                wait_time = min(
                    self.backoff_factor ** attempt,
                    self.backoff_max_seconds,
                )

                # Call retry callback if provided
                if self.on_retry:
                    self.on_retry(e, attempt + 1, wait_time)

                # Wait before retry
                time.sleep(wait_time)

        return {
            "success": False,
            "operation_index": operation_index,
            "attempt": self.max_retries + 1,
            "result": None,
            "error": str(last_error or "Unknown error"),
        }

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if an error should trigger a retry.

        Args:
            error: The exception that occurred.
            attempt: Current attempt number.

        Returns:
            True if should retry, False otherwise.
        """
        # Check for HTTP status code in error
        error_str = str(error).lower()

        # Check common error codes
        for status_code in self.retry_on:
            if str(status_code) in error_str:
                return True

        # Check for rate limit related keywords
        if any(keyword in error_str for keyword in ["rate limit", "throttle", "too many"]):
            return True

        # Check for timeout/connection errors
        if any(keyword in error_str for keyword in ["timeout", "connection", "refused", "temporary failure"]):
            return True

        return False


class AsyncBulkOperationManager:
    """Async version of BulkOperationManager for concurrent operations.

    Example::

        async with AsyncBulkOperationManager(max_concurrent=5) as bulk:
            for policy_data in policies_to_create:
                bulk.add_operation(async_policies.create_policy, policy_data=policy_data)
            results = await bulk.execute()
    """

    def __init__(
        self,
        max_concurrent: int = 5,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        backoff_max_seconds: float = 60.0,
        retry_on: list[int] | None = None,
        on_retry: Optional[Callable[[Exception, int, float], None]] = None,
    ):
        """Initialize async bulk operation manager.

        Args:
            max_concurrent: Maximum concurrent operations.
            max_retries: Maximum retry attempts per operation.
            backoff_factor: Exponential backoff factor.
            backoff_max_seconds: Maximum backoff time.
            retry_on: HTTP status codes to retry on.
            on_retry: Callback on retry.
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.backoff_max_seconds = backoff_max_seconds
        self.retry_on = retry_on or [429, 503]
        self.on_retry = on_retry
        self.operations: list[tuple[Callable[..., Any], dict[str, Any]]] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        pass

    def add_operation(
        self,
        func: Callable[..., Any],
        **kwargs: Any,
    ) -> None:
        """Add an async operation to the queue."""
        self.operations.append((func, kwargs))

    async def execute(self) -> dict[str, Any]:
        """Execute all operations concurrently with retries.

        Returns:
            Dictionary with results and error information.
        """
        tasks = [
            self._execute_with_semaphore(idx, func, kwargs)
            for idx, (func, kwargs) in enumerate(self.operations)
        ]

        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        errors = []
        for result in all_results:
            if isinstance(result, Exception):
                errors.append({"error": str(result)})
            elif result.get("success"):
                results.append(result)
            else:
                errors.append(result)

        return {
            "total": len(self.operations),
            "succeeded": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }

    async def _execute_with_semaphore(
        self,
        idx: int,
        func: Callable[..., Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute operation with semaphore and retry logic."""
        async with self.semaphore:
            return await self._execute_with_retry(func, kwargs, idx)

    async def _execute_with_retry(
        self,
        func: Callable[..., Any],
        kwargs: dict[str, Any],
        operation_index: int = 0,
    ) -> dict[str, Any]:
        """Execute async operation with retries."""
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                result = await func(**kwargs)
                return {
                    "success": True,
                    "operation_index": operation_index,
                    "attempt": attempt + 1,
                    "result": result,
                    "error": None,
                }
            except Exception as e:
                last_error = e

                # Check if should retry
                should_retry = self._should_retry(e, attempt)

                if not should_retry or attempt >= self.max_retries:
                    break

                # Exponential backoff
                wait_time = min(
                    self.backoff_factor ** attempt,
                    self.backoff_max_seconds,
                )

                if self.on_retry:
                    self.on_retry(e, attempt + 1, wait_time)

                await asyncio.sleep(wait_time)

        return {
            "success": False,
            "operation_index": operation_index,
            "attempt": self.max_retries + 1,
            "result": None,
            "error": str(last_error or "Unknown error"),
        }

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if error should trigger retry."""
        error_str = str(error).lower()

        for status_code in self.retry_on:
            if str(status_code) in error_str:
                return True

        if any(keyword in error_str for keyword in ["rate limit", "throttle", "too many"]):
            return True

        if any(keyword in error_str for keyword in ["timeout", "connection", "refused"]):
            return True

        return False


__all__ = [
    "BulkOperationManager",
    "AsyncBulkOperationManager",
]

