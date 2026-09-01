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

import time
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from json import dumps
from typing import Any, Literal

from britecore_sdk.exceptions import ReadOnlyViolation

WRITE_METHODS = frozenset({"PUT", "PATCH", "DELETE"})
WRITE_PATH_MARKERS = (
    "/new_",
    "/create_",
    "/update_",
    "/delete_",
    "/remove_",
    "/cancel_",
    "/reinstate_",
    "/add_",
    "/submit_",
    "/bind_",
    "/issue_",
)
READ_PATH_MARKERS = (
    "/retrieve_",
    "/get_",
    "/search_",
    "/find_",
    "/list_",
)


def _matches_any(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    normalized_path = path.strip().lower()
    return any(pattern in normalized_path for pattern in patterns)


def classify_write_operation(
    method: str,
    path: str,
    *,
    allowlist: list[str] | tuple[str, ...] | None = None,
    denylist: list[str] | tuple[str, ...] | None = None,
) -> bool:
    """Return True when the request looks like a mutating operation."""
    normalized_method = method.strip().upper()
    normalized_path = path.strip().lower()
    normalized_allowlist = tuple(
        entry.strip().lower() for entry in (allowlist or []) if entry
    )
    normalized_denylist = tuple(
        entry.strip().lower() for entry in (denylist or []) if entry
    )

    if _matches_any(normalized_path, normalized_allowlist):
        return False
    if _matches_any(normalized_path, normalized_denylist):
        return True

    if normalized_method in WRITE_METHODS:
        return True
    if normalized_method != "POST":
        return False

    if _matches_any(normalized_path, READ_PATH_MARKERS):
        return False
    return _matches_any(normalized_path, WRITE_PATH_MARKERS)


@dataclass
class RequestContext:
    """Context for request middleware hooks."""

    method: str  # "GET", "POST", "PUT", "DELETE"
    path: str  # "/api/v2/quotes/get_quote"
    headers: dict[str, Any] = field(default_factory=dict)
    body: dict[str, Any] | None = None
    timeout: Any | None = None
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
    body: Any | None = None
    timestamp: float = field(default_factory=time.time)
    request_context: RequestContext | None = None

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time since request in milliseconds."""
        if self.request_context and hasattr(self.request_context, "timestamp"):
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

    def __init__(self, logger: Any | None = None):
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


class WriteGuardMiddleware(Middleware):
    """Enforces read-only behavior by classifying and guarding write operations."""

    def __init__(
        self,
        policy: Literal["allow", "warn", "block"] = "block",
        *,
        allowlist: list[str] | tuple[str, ...] | None = None,
        denylist: list[str] | tuple[str, ...] | None = None,
        warning_callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        normalized_policy = policy.strip().lower()
        if normalized_policy not in {"allow", "warn", "block"}:
            raise ValueError("policy must be one of: allow, warn, block")

        self.policy = normalized_policy
        self.allowlist = [entry.strip().lower() for entry in (allowlist or []) if entry]
        self.denylist = [entry.strip().lower() for entry in (denylist or []) if entry]
        self.warning_callback = warning_callback

    def is_write_operation(self, method: str, path: str) -> bool:
        return classify_write_operation(
            method,
            path,
            allowlist=self.allowlist,
            denylist=self.denylist,
        )

    def on_request(self, ctx: RequestContext) -> RequestContext:
        if self.policy == "allow":
            return ctx

        if not self.is_write_operation(ctx.method, ctx.path):
            return ctx

        event = {
            "method": ctx.method,
            "path": ctx.path,
            "policy": self.policy,
            "timestamp": ctx.timestamp,
        }
        ctx.extra["write_guard"] = event

        message = (
            f"Write operation attempted while write policy is '{self.policy}': "
            f"{ctx.method} {ctx.path}"
        )

        if self.policy == "warn":
            warnings.warn(message, UserWarning, stacklevel=3)
            if self.warning_callback is not None:
                self.warning_callback(event)
            return ctx

        raise ReadOnlyViolation(
            message,
            endpoint=ctx.path,
            method=ctx.method,
        )

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        return error


class AuditMiddleware(Middleware):
    """Emits structured audit events for request activity (writes by default)."""

    def __init__(
        self,
        *,
        audit_only_writes: bool = True,
        allowlist: list[str] | tuple[str, ...] | None = None,
        denylist: list[str] | tuple[str, ...] | None = None,
        audit_callback: Callable[[dict[str, Any]], None] | None = None,
        logger: Any | None = None,
        log_level: Literal["debug", "info"] = "info",
    ):
        from britecore_sdk import logger as default_logger

        self.audit_only_writes = audit_only_writes
        self.allowlist = [entry.strip().lower() for entry in (allowlist or []) if entry]
        self.denylist = [entry.strip().lower() for entry in (denylist or []) if entry]
        self.audit_callback = audit_callback
        self.logger = logger or default_logger
        self.log_level = "debug" if log_level == "debug" else "info"

    def _should_audit(self, method: str, path: str) -> bool:
        if not self.audit_only_writes:
            return True
        return classify_write_operation(
            method,
            path,
            allowlist=self.allowlist,
            denylist=self.denylist,
        )

    def on_request(self, ctx: RequestContext) -> RequestContext:
        if not self._should_audit(ctx.method, ctx.path):
            return ctx

        event = {
            "event": "sdk_request_audit",
            "method": ctx.method,
            "path": ctx.path,
            "timestamp": ctx.timestamp,
            "write_operation": classify_write_operation(
                ctx.method,
                ctx.path,
                allowlist=self.allowlist,
                denylist=self.denylist,
            ),
        }
        ctx.extra.setdefault("audit_events", []).append(event)

        getattr(self.logger, self.log_level)("AUDIT %s", dumps(event, sort_keys=True))
        if self.audit_callback is not None:
            self.audit_callback(event)
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
    "WriteGuardMiddleware",
    "AuditMiddleware",
    "classify_write_operation",
]
