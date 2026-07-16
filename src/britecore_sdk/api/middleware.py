"""v2.0.0 Transport Middleware System.

Provides pluggable middleware hooks for request/response processing, enabling
extensibility for logging, tracing, retry logic, header injection, and more.

**Basic Middleware Example:**

    from britecore_sdk.api.middleware import Middleware, RequestContext, ResponseContext
    from britecore_sdk import BritecoreAPIClient

    class LoggingMiddleware(Middleware):
        '''Log all requests and responses.'''

        def on_request(self, ctx: RequestContext) -> RequestContext:
            '''Called before request is sent.'''
            print(f"→ {ctx.method} {ctx.path}")
            return ctx

        def on_response(self, ctx: ResponseContext) -> ResponseContext:
            '''Called after response received.'''
            print(f"← {ctx.status_code} {ctx.path} ({ctx.elapsed_ms}ms)")
            return ctx

        def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
            '''Called on request error.'''
            print(f"✗ Error: {error}")
            return error

    # Register middleware
    client = BritecoreAPIClient("site").init_client()
    client.add_middleware(LoggingMiddleware())

    # All requests now flow through the middleware

**Advanced Example: OpenTelemetry Integration:**

    from opentelemetry import trace

    class TracingMiddleware(Middleware):
        def __init__(self, tracer=None):
            self.tracer = tracer or trace.get_tracer(__name__)

        def on_request(self, ctx: RequestContext) -> RequestContext:
            ctx.span = self.tracer.start_as_current_span(
                f"http.{ctx.method.lower()}"
            )
            ctx.span.set_attribute("http.method", ctx.method)
            ctx.span.set_attribute("http.url", ctx.path)
            return ctx

        def on_response(self, ctx: ResponseContext) -> ResponseContext:
            if hasattr(ctx, 'span'):
                ctx.span.set_attribute("http.status_code", ctx.status_code)
                ctx.span.end()
            return ctx

**Custom Retry Middleware:**

    class RetryMiddleware(Middleware):
        def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
            self.max_retries = max_retries
            self.backoff_factor = backoff_factor

        def on_response(self, ctx: ResponseContext) -> ResponseContext:
            if ctx.status_code in (429, 500, 502, 503):
                # Signal retry by raising special exception
                raise RetryableError(f"HTTP {ctx.status_code}", backoff=self.backoff_factor)
            return ctx
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import time
from abc import ABC, abstractmethod


@dataclass
class RequestContext:
    """Context for request middleware hooks."""

    method: str  # "GET", "POST", "PUT", "DELETE"
    path: str  # "/api/v2/quotes/get_quote"
    headers: dict[str, Any] = field(default_factory=dict)
    body: Optional[dict[str, Any]] = None
    timeout: Optional[float] = None
    timestamp: float = field(default_factory=time.time)

    # Middleware can attach arbitrary context
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseContext:
    """Context for response middleware hooks."""

    status_code: int
    path: str
    method: str
    headers: dict[str, Any] = field(default_factory=dict)
    body: Optional[Any] = None
    timestamp: float = field(default_factory=time.time)
    request_context: Optional[RequestContext] = None

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time since request in milliseconds."""
        if self.request_context and hasattr(self.request_context, 'timestamp'):
            return (self.timestamp - self.request_context.timestamp) * 1000
        return 0

    # Middleware can attach arbitrary context
    extra: dict[str, Any] = field(default_factory=dict)


class Middleware(ABC):
    """Base class for all middleware.

    Subclass and override hooks to customize request/response processing.
    Middleware is executed in order for each request/response cycle.
    """

    @abstractmethod
    def on_request(self, ctx: RequestContext) -> RequestContext:
        """Called before request is sent.

        Args:
            ctx: Request context with method, path, headers, body.

        Returns:
            RequestContext: Modified context (can mutate or create new).

        Raises:
            Exception: Any exception aborts the request (on_error hook called).
        """
        ...

    @abstractmethod
    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        """Called after successful response received.

        Args:
            ctx: Response context with status_code, headers, body.

        Returns:
            ResponseContext: Modified context.

        Raises:
            Exception: Any exception triggers on_error hook and may retry.
        """
        ...

    @abstractmethod
    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        """Called when request fails.

        Args:
            error: The exception that occurred.
            ctx: Request context that caused the error.

        Returns:
            Exception: The exception to raise (can be modified or wrapped).
        """
        ...


class NoOpMiddleware(Middleware):
    """Default no-op middleware - does nothing."""

    def on_request(self, ctx: RequestContext) -> RequestContext:
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        return error


# ============================================================================
# BUILT-IN MIDDLEWARE
# ============================================================================

class RequestIdMiddleware(Middleware):
    """Adds X-Request-ID header to all requests."""

    def on_request(self, ctx: RequestContext) -> RequestContext:
        import secrets
        request_id = secrets.token_hex(6)  # 12 character hex string
        ctx.headers["X-Request-ID"] = request_id
        ctx.extra["request_id"] = request_id
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        # Extract from response headers if present
        if "X-Request-ID" in ctx.headers:
            ctx.extra["request_id"] = ctx.headers["X-Request-ID"]
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        return error


class LoggingMiddleware(Middleware):
    """Logs all requests and responses."""

    def __init__(self, logger: Optional[Any] = None):
        from britecore_sdk import logger as default_logger
        self.logger = logger or default_logger

    def on_request(self, ctx: RequestContext) -> RequestContext:
        self.logger.debug(f"→ {ctx.method} {ctx.path}")
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        self.logger.debug(
            f"← {ctx.status_code} {ctx.method} {ctx.path} ({ctx.elapsed_ms:.1f}ms)"
        )
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        self.logger.error(f"✗ {ctx.method} {ctx.path}: {error}", exc_info=True)
        return error


class HeaderInjectionMiddleware(Middleware):
    """Injects custom headers into all requests."""

    def __init__(self, headers: dict[str, str]):
        self.headers = headers

    def on_request(self, ctx: RequestContext) -> RequestContext:
        ctx.headers.update(self.headers)
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        return error


class TimeoutMiddleware(Middleware):
    """Sets timeout on all requests if not already set."""

    def __init__(self, timeout_seconds: float = 30):
        self.timeout_seconds = timeout_seconds

    def on_request(self, ctx: RequestContext) -> RequestContext:
        if ctx.timeout is None:
            ctx.timeout = self.timeout_seconds
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        return error


__all__ = [
    "Middleware",
    "NoOpMiddleware",
    "RequestContext",
    "ResponseContext",
    "RequestIdMiddleware",
    "LoggingMiddleware",
    "HeaderInjectionMiddleware",
    "TimeoutMiddleware",
]

