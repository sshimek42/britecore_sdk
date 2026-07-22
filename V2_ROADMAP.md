# BriteCore SDK v2.0.0 Roadmap

*Last updated: July 16, 2026*
*Status: Planning & Implementation*

## Overview

v2.0.0 introduces **breaking changes** focused on moving away from implicit global state, improving type safety, standardizing error handling, and providing better extensibility. These changes align with modern Python SDK best practices.

---

## Breaking Changes & Migration Path

### Phase 1: Client Lifecycle Redesign

**Goal:** Move away from module-global implicit client state; make explicit client instances the default API.

#### Current State (legacy)

```python
# Implicit global client - hard to test, unclear dependencies
from britecore_sdk.api.api_calls import retrieve_quote
quote = retrieve_quote(quote_number="Q123")

# Or explicit but cumbersome
from britecore_sdk.api.api_calls import use_api_client, retrieve_quote
client = BritecoreAPIClient("site").init_client()
with use_api_client(client):
    quote = retrieve_quote(quote_number="Q123")
```

#### v2.0.0 Target

```python
# Explicit client is now primary pattern
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes

client = BritecoreAPIClient("site").init_client()
quote = quotes.retrieve_quote(quote_number="Q123", client=client)

# Or with context manager (preferred for cleanup)
with BritecoreAPIClient("site").init_client() as client:
    quote = quotes.retrieve_quote(quote_number="Q123", client=client)
```

#### Implementation Strategy
1. **Add optional `client` parameter** to all endpoint wrappers
2. **Fall back to module-level client** if not provided (for backwards compatibility during transition)
3. **Deprecate implicit client in a minor release** (after initial rollout)
4. **Remove implicit client fallback in v2.0.0**
5. **Update all examples** to use explicit client pattern
6. **Add type hints** for client parameter (remove `Unpack[RequestParameters]` anti-pattern)

#### Acceptance Criteria
- [ ] All v2 endpoint wrappers accept optional `client: BritecoreAPIClient` parameter
- [ ] Wrappers prefer explicit client over module-level client
- [ ] Examples use explicit client pattern throughout
- [ ] Migration guide covers the transition

---

### Phase 2: Typed Response Models

**Goal:** Reduce `Any` returns; provide typed response models (or typed envelopes) for sync + async parity.

#### Current State (legacy)

```python
# Returns `Any` - no IDE autocomplete, runtime surprises
result = retrieve_quote(quote_number="Q123")
quote_premium = result.get("premium")  # Could be anything!

# Types are unclear in async too
result = await aretrieve_quote(quote_number="Q123")  # Same Any return
```

#### v2.0.0 Target

```python
# Typed response models with autocomplete
from britecore_sdk.api.responses import QuoteResponse
from britecore_sdk.api.api_calls.v2 import quotes

quote: QuoteResponse = quotes.retrieve_quote(quote_number="Q123", client=client)
quote_premium = quote.premium  # Type-safe, IDE autocomplete

# Async has parity
quote: QuoteResponse = await quotes.aretrieve_quote(quote_number="Q123", client=client)
```

#### Response Model Structure

```python
# britecore_sdk/api/responses/__init__.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ResponseEnvelope:
    """Base envelope for all API responses."""
    success: bool
    data: Any  # The actual typed model
    message: Optional[str] = None
    messages: Optional[list[str]] = None
    request_id: str = ""  # Extracted from response headers
    status_code: int = 200

@dataclass
class QuoteResponse:
    """Typed response for quote retrieval."""
    quote_id: str
    quote_number: str
    status: str
    premium: float
    term_days: int
    effective_date: str
    # ... other fields

    @classmethod
    def from_api(cls, data: dict) -> "QuoteResponse":
        """Parse API response dict into typed model."""
        return cls(
            quote_id=data.get("id"),
            quote_number=data.get("quoteNumber"),
            # ...
        )
```

#### Implementation Strategy
1. **Define response models** for each domain (quotes, policies, contacts, etc.)
2. **Use `dataclass` or `pydantic` BaseModel** for runtime validation (opt-in)
3. **Create factory methods** (`.from_api()`) to hydrate models from API responses
4. **Update all wrappers** to return typed models instead of raw dicts/Any
5. **Maintain backwards compatibility shim** (legacy paths continue returning dict/Any)
6. **Provide both `ResponseEnvelope` and direct typed models** for flexibility

#### Acceptance Criteria
- [ ] Response models defined for all major domains (quotes, policies, contacts, etc.)
- [ ] All v2 wrappers return typed models (not `Any` or `dict`)
- [ ] Async wrappers return same types as sync equivalents
- [ ] Response models support `.from_api()` factory pattern
- [ ] Pydantic validation available (opt-in via `settings.toml`)
- [ ] Type stubs (`.pyi`) generated or provided for IDE support

---

### Phase 3: Standardized Error Model

**Goal:** Standardize exceptions with `status_code`, `error_code`, `request_id`, and raw payload attached.

#### Current State (legacy)

```python
# Error details scattered across exception message
try:
    retrieve_quote(quote_number="Q123")
except AuthenticationError as e:
    print(str(e))  # Message only, no structured data
    # No access to HTTP status, error code, or request ID
```

#### v2.0.0 Target

```python
# Rich exception context
from britecore_sdk.exceptions import NotFoundError, ValidationError

try:
    retrieve_quote(quote_number="INVALID")
except NotFoundError as e:
    print(e.status_code)      # 404
    print(e.error_code)       # "quote_not_found"
    print(e.request_id)       # "abc123def456"
    print(e.detail)           # "Quote INVALID does not exist"
    print(e.raw_payload)      # Full server response dict

except ValidationError as e:
    print(e.status_code)      # 400
    print(e.error_code)       # "invalid_field"
    print(e.validation_errors) # {"premium": ["Must be positive"]}
```

#### Exception Hierarchy (v2.0.0)

```python
class BritecoreError(Exception):
    """Base exception - now with structured metadata."""
    status_code: int
    error_code: Optional[str]
    request_id: Optional[str]
    detail: str
    raw_payload: dict

    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        request_id: Optional[str] = None,
        raw_payload: Optional[dict] = None,
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
        self.raw_payload = raw_payload or {}
        super().__init__(detail)

# Flat aliases still available
class AuthenticationError(BritecoreError):
    pass

class NotFoundError(BritecoreError):
    pass

class ValidationError(BritecoreError):
    validation_errors: dict
```

#### Implementation Strategy
1. **Enhance `BritecoreError` base class** with status_code, error_code, request_id, raw_payload
2. **Update `process_result()`** to extract and attach metadata to exceptions
3. **Extract request_id from response headers** (`X-Request-ID` or similar)
4. **Parse server error payloads** to extract structured error details
5. **Preserve backwards compatibility** - existing `str(exception)` still works
6. **Document exception handling patterns** in TROUBLESHOOTING.md

#### Acceptance Criteria
- [ ] All exceptions have `status_code`, `error_code`, `request_id` attributes
- [ ] `process_result()` populates exception metadata from API responses
- [ ] Request ID extracted and attached to exceptions + logged
- [ ] Validation errors available as `.validation_errors` dict
- [ ] Raw payload preserved for debugging
- [ ] Backwards compatible - `str(exception)` produces readable message

---

### Phase 4: Transport Boundary & Middleware

**Goal:** Introduce pluggable transport/middleware hooks for retry, logging, tracing, custom headers.

#### Current State (legacy)

```python
# Limited customization - stuck with built-in retry/rate limit logic
client = BritecoreAPIClient("site").init_client()
# No way to inject custom logging, tracing, headers without subclassing
```

#### v2.0.0 Target

```python
# Rich middleware/hook system
from britecore_sdk.transport import Middleware, RequestContext, ResponseContext

class TracingMiddleware(Middleware):
    def on_request(self, ctx: RequestContext) -> RequestContext:
        """Before request is sent."""
        ctx.headers["X-Trace-ID"] = self.tracer.start_span()
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        """After response received."""
        self.tracer.end_span(status=ctx.status_code)
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        """On request error."""
        self.tracer.record_error(error)
        return error

class CustomRetryMiddleware(Middleware):
    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        if ctx.status_code == 429:
            # Custom backoff logic
            backoff = calculate_backoff(ctx.response_data)
            raise RetryableError(backoff_seconds=backoff)
        return ctx

client = BritecoreAPIClient("site").init_client(
    middleware=[
        TracingMiddleware(tracer=my_tracer),
        CustomRetryMiddleware(),
    ]
)

# Or add middleware post-init
client.add_middleware(LoggingMiddleware(logger=my_logger))
```

#### Implementation Strategy
1. **Define `Middleware` base class** with hooks: `on_request`, `on_response`, `on_error`
2. **Define `RequestContext` and `ResponseContext`** to pass through middleware chain
3. **Refactor `do_request()`** to execute middleware chain
4. **Provide built-in middleware**: `RetryMiddleware`, `LoggingMiddleware`, `RateLimitMiddleware`
5. **Support middleware stack** - order matters
6. **Document middleware patterns** with examples (OpenTelemetry, custom logging, etc.)

#### Acceptance Criteria
- [ ] `Middleware` base class defined with hook methods
- [ ] `RequestContext` and `ResponseContext` types defined
- [ ] Middleware chain execution in `do_request()`
- [ ] Built-in middleware for retry, logging, rate limiting
- [ ] `add_middleware()` and `remove_middleware()` on client
- [ ] Examples: OpenTelemetry integration, custom logging, header injection
- [ ] Documentation and tests for middleware system

---

### Phase 5: Pagination Ergonomics

**Goal:** Add iterator helpers for list endpoints instead of manual page plumbing.

#### Current State (legacy)

```python
# Manual pagination - error-prone
page = 1
all_quotes = []
while True:
    response = list_quotes(page=page, limit=100, client=client)
    all_quotes.extend(response["data"])
    if len(response["data"]) < 100:
        break
    page += 1
```

#### v2.0.0 Target

```python
# Iterator-based pagination - Pythonic
from britecore_sdk.api.api_calls.v2 import quotes

# Option 1: Iterator pattern
for quote in quotes.iter_quotes(limit=100, client=client):
    print(f"Quote: {quote.quote_number}")

# Option 2: Collect all with auto-pagination
all_quotes = list(quotes.iter_quotes(client=client))

# Option 3: Async iterator
async for quote in quotes.aiter_quotes(client=client):
    print(f"Quote: {quote.quote_number}")
```

#### Iterator Implementation

```python
from typing import Iterator, AsyncIterator
from britecore_sdk.api.responses import QuoteResponse

def iter_quotes(
    client: BritecoreAPIClient,
    limit: int = 100,
    **kwargs
) -> Iterator[QuoteResponse]:
    """Iterate over all quotes, handling pagination automatically."""
    page = 1
    while True:
        response = list_quotes(page=page, limit=limit, client=client, **kwargs)
        if not response.data:
            break
        for item in response.data:
            yield QuoteResponse.from_api(item)
        if len(response.data) < limit:
            break
        page += 1

async def aiter_quotes(
    client: AsyncBritecoreAPIClient,
    limit: int = 100,
    **kwargs
) -> AsyncIterator[QuoteResponse]:
    """Async iterator for quotes with automatic pagination."""
    page = 1
    while True:
        response = await alist_quotes(page=page, limit=limit, client=client, **kwargs)
        if not response.data:
            break
        for item in response.data:
            yield QuoteResponse.from_api(item)
        if len(response.data) < limit:
            break
        page += 1
```

#### Implementation Strategy
1. **Add `iter_*()` function** for each list endpoint
2. **Add `aiter_*()` async function** for each list endpoint
3. **Support `limit` parameter** for page size
4. **Support filtering kwargs** (pass through to underlying list function)
5. **Handle `is_last_page` or similar** field in API responses
6. **Document pagination patterns** with examples

#### Acceptance Criteria
- [ ] Iterator functions added for all list endpoints
- [ ] Async iterator functions added for all list endpoints
- [ ] Manual pagination still supported (backwards compatible)
- [ ] Iterator handles empty results gracefully
- [ ] Iterator supports filtering parameters
- [ ] Examples document iterator usage patterns

---

### Phase 6: Legacy Cleanup

**Goal:** Remove/deprecate v1-only or compatibility shims from core path; keep migration helpers in separate module.

#### Current State (legacy)

```
src/britecore_sdk/
├── classes/           # Legacy compatibility layer (deprecated)
├── api/api_calls/
│   ├── v1/           # Old versioned endpoints (still supported for backwards compat)
│   └── v2/           # New endpoints
└── ...
```

#### v2.0.0 Target

```
src/britecore_sdk/
├── api/api_calls/
│   ├── v2/           # Current active endpoints (all v2)
│   └── _compat/      # Migration helpers ONLY (moved from v1/)
├── models/           # Response models
├── validators/       # Input validators
├── transport/        # Pluggable transport/middleware
├── responses/        # Response envelopes
└── ...

# Removed or moved:
# - classes/           → Remove entirely, direct to models/validators
# - api_calls/v1/*     → Move useful utilities to _compat/
# - Legacy compatibility shims
```

#### What Gets Removed

```python
# REMOVED in v2.0.0:
from britecore_sdk.classes.quote import Quote  # ❌ Use models instead

# REMOVED in v2.0.0:
from britecore_sdk.api.api_calls.v1.custom_ui import ...  # ❌ Moved to compat helpers with migration guide

# STILL WORKS in v2.0.0:
from britecore_sdk.api.api_calls.v2.quotes import retrieve_quote  # ✅
```

#### Migration Helpers Module

```
src/britecore_sdk/api/_compat/
├── __init__.py
├── v1_route_mapping.py   # Maps old v1 imports to new locations
├── migration_guide.md    # User-facing migration instructions
└── examples/
    └── v1_to_v2_migration.py
```

#### Implementation Strategy
1. **Audit `classes/` module** - move useful models to `models/`, remove rest
2. **Review `api_calls/v1/`** - preserve supported wrappers when the upstream API still has no `v2` equivalent
3. **Move migration shims** to `api/_compat/` with clear deprecation notices
4. **Update imports in `__init__.py`** to point to new locations
5. **Remove circular import workarounds** and other v1-specific hacks
6. **Create archived adoption notes** in `docs/migrations/`

#### Acceptance Criteria
- [ ] `classes/` module removed or fully deprecated
- [ ] Supported `api_calls/v1` wrappers retained when no `v2` SDK equivalent exists
- [ ] Migration helpers available in `_compat/` with clear instructions
- [ ] No circular imports or compatibility shims in core path
- [ ] `__all__` exports cleaned up
- [ ] Archived adoption notes provided for the major 2.0.0 design changes

---

## Implementation Timeline

### Week 1-2: Foundation
- Phase 1: Client lifecycle parameter support
- Phase 3: Enhanced exception model

### Week 3-4: Type Safety
- Phase 2: Response models and typed returns
- Phase 5: Pagination iterators

### Week 5-6: Extensibility
- Phase 4: Transport middleware system
- Phase 6: Legacy cleanup

---

## Version Strategy

> **Historical note:** This roadmap captured pre-release planning. The current 2.x policy does **not** treat all `api_calls/v1` wrappers as legacy, and it does not require a blanket SDK-wide `v1`→`v2` rewrite.

### 1.6.0 (Minor - Deprecations)
- Add deprecation warnings for implicit client usage
- Add new explicit client pattern alongside old one
- Response models available but optional
- Typed exceptions available but not default
- New middleware system available for early adopters

### 1.7.0 (Minor - Foundation)
- Pagination iterators available
- Adoption/design notes published
- Deprecations become more vocal

### v2.0.0 (Major - Breaking)
- Remove implicit client fallback
- Only explicit client API available
- Response models mandatory
- Typed exceptions with metadata
- Transport middleware required pattern
- Legacy `classes/` removed
- Supported `api_calls/v1` wrappers retained where the upstream API or SDK coverage still requires them

---

## Testing Strategy

Each phase should include:
- Unit tests for new functionality
- Integration tests with mock API
- Backwards compatibility tests (where applicable)
- Migration path tests (old code still works, with warnings)
- Type checking tests (mypy, pyright)

---

## Documentation Updates

For each phase:
1. Update CHANGELOG.md with changes
2. Update DEPRECATION.md if applicable
3. Add/update docstrings with examples
4. Create/update migration guide in `docs/migrations/`
5. Update README.md and GETTING_STARTED.md
6. Add examples in `examples/`

---

## Success Metrics

- [ ] All phases completed
- [ ] 100% type hint coverage (no `Any` in public API)
- [ ] Zero breaking changes in 1.x releases
- [ ] Clear adoption guidance for explicit-client patterns and related 2.0.0 design changes
- [ ] Cleaner, more maintainable codebase
- [ ] Community feedback positive on v2 design

---

## See Also

- [DEPRECATION.md](DEPRECATION.md) — Deprecation policy
- [AGENTS.md](AGENTS.md) — Development workflow
- [CONTRIBUTING.md](CONTRIBUTING.md) — Maintainer guidelines
