# Phases 2-5: Typed Responses, Error Models, Pagination & Middleware (Archived Notes)

*Last updated: July 16, 2026*
*Document type: Archived implementation record*

## Overview

This document covers the implementation of Phases 2-5 of the v2.0.0 roadmap:

1. **Phase 2**: Typed Response Models — Type-safe API responses
2. **Phase 3**: Standardized Error Model — Structured exception metadata
3. **Phase 4**: Transport Middleware — Pluggable request/response hooks
4. **Phase 5**: Pagination Iterators — Automatic page management

---

## Phase 2: Typed Response Models

### Overview

Instead of returning `Any` or `dict`, endpoint wrappers now return typed dataclass models with IDE autocomplete support.

### Response Models Available

**`ResponseEnvelope`** — Base wrapper for API responses

```python
from britecore_sdk.api.responses import ResponseEnvelope

envelope = ResponseEnvelope.from_api({
    "success": True,
    "data": {...},
    "message": "Success"
})

print(f"Status: {envelope.status_code}")
print(f"Request ID: {envelope.request_id}")
print(f"Data: {envelope.data}")
```

**Domain-Specific Models:**

- `QuoteResponse` — Quote operations
- `PolicyResponse` — Policy operations
- `ContactResponse` — Contact operations
- `ListResponse` — Generic list wrapper
- `BatchOperationResponse` — Batch results

### Usage Example

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes
from britecore_sdk.api.responses import QuoteResponse

client = BritecoreAPIClient("site").init_client()

# Type-safe response
quote: QuoteResponse = quotes.retrieve_quote(
    quote_number="Q123",
    client=client
)

# IDE autocomplete + type checking
print(f"Premium: {quote.premium}")
print(f"Status: {quote.status}")
print(f"Term Days: {quote.term_days}")

# Access raw data for fields not in model
raw = quote.raw_data
print(f"All data: {raw}")
```

### Adoption Pattern

**Earlier dict-based pattern:**

```python
response = retrieve_quote(quote_number="Q123")
premium = response.get("premium")  # No type checking
```

**Typed-response pattern introduced in 2.0.0:**

```python
quote: QuoteResponse = retrieve_quote(quote_number="Q123", client=client)
premium = quote.premium  # Type-safe, IDE autocomplete
```

### Extending Response Models

Create custom models for your use case:

```python
from britecore_sdk.api.responses import QuoteResponse
from dataclasses import dataclass

@dataclass
class EnrichedQuoteResponse(QuoteResponse):
    """Extended quote with custom business logic."""

    is_profitable: bool = False
    profit_margin: float = 0.0

    @classmethod
    def from_api(cls, data: dict) -> "EnrichedQuoteResponse":
        base = super().from_api(data)
        margin = 0.15  # 15% margin
        is_profitable = base.premium >= base.premium * margin
        profit_margin = margin

        return cls(
            **{k: v for k, v in base.__dict__.items()},
            is_profitable=is_profitable,
            profit_margin=profit_margin,
        )
```

---

## Phase 3: Standardized Error Model

### Overview

All exceptions now include structured metadata: `status_code`, `error_code`, `request_id`, and `raw_payload`.

### Exception Structure

```python
try:
    retrieve_quote(quote_number="INVALID", client=client)
except NotFoundError as e:
    # Structured metadata
    print(f"Status: {e.status_code}")      # 404
    print(f"Error Code: {e.error_code}")   # "quote_not_found"
    print(f"Request ID: {e.request_id}")   # "abc123def456"
    print(f"Detail: {e.detail}")           # "Quote not found"
    print(f"Raw Payload: {e.raw_payload}") # Full server response
```

### Exception Types with Enhanced Metadata

| Exception | Status Code | Error Code |
|-----------|-------------|-----------|
| `AuthenticationError` | 401/403 | `authentication_failed` |
| `NotFoundError` | 404 | (from server) |
| `ValidationError` | 400/422 | `validation_error` |
| `RateLimitError` | 429 | `rate_limit_exceeded` |
| `ServerError` | 500+ | `server_error` |
| `RequestTimeoutError` | 408 | `request_timeout` |
| `ConfigurationError` | 400 | `configuration_error` |

### ValidationError Example

```python
from britecore_sdk.exceptions import ValidationError

try:
    create_quote(invalid_data, client=client)
except ValidationError as e:
    # Field-level validation errors
    print(f"Validation failed: {e.detail}")
    for field, errors in e.validation_errors.items():
        print(f"  {field}: {errors}")

    # Example output:
    # Validation failed: Quote validation failed
    #   premium: ["Must be positive"]
    #   effective_date: ["Must be in the future"]
```

### Usage in Error Handling

```python
from britecore_sdk.exceptions import (
    NotFoundError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
)

try:
    result = retrieve_policy(policy_number="P123", client=client)
except ValidationError as e:
    logger.error(
        f"Validation failed for {e.endpoint}: {e.detail}",
        extra={
            "request_id": e.request_id,
            "validation_errors": e.validation_errors,
        }
    )
    handle_validation_error(e)
except NotFoundError as e:
    logger.warning(
        f"Resource not found: {e.detail}",
        extra={"request_id": e.request_id}
    )
    return None
except RateLimitError as e:
    backoff = e.retry_after or 60
    logger.info(f"Rate limited. Retrying after {backoff}s")
    time.sleep(backoff)
    # Retry logic...
except AuthenticationError as e:
    logger.critical(f"Auth failed: {e.detail}")
    # Re-authenticate...
```

### Creating Custom Exceptions

```python
from britecore_sdk.exceptions import BritecoreError

raise BritecoreError.Base(
    "Custom error message",
    status_code=400,
    error_code="custom_error",
    request_id="req_123",
    raw_payload={"key": "value"}
)
```

---

## Phase 4: Transport Middleware System

### Overview

Middleware provides extensibility points for logging, tracing, header injection, custom retry logic, and more.

### Built-In Middleware

**`LoggingMiddleware`** — Log all requests/responses

```python
from britecore_sdk.api.middleware import LoggingMiddleware
from britecore_sdk import BritecoreAPIClient, configure_logging
import logging

configure_logging(level=logging.DEBUG)

client = BritecoreAPIClient("site").init_client()
client.add_middleware(LoggingMiddleware())

# Logs like:
# DEBUG → GET /api/v2/quotes/get_quote
# DEBUG ← 200 GET /api/v2/quotes/get_quote (45.2ms)
```

**`HeaderInjectionMiddleware`** — Inject custom headers

```python
from britecore_sdk.api.middleware import HeaderInjectionMiddleware

client.add_middleware(HeaderInjectionMiddleware({
    "X-Custom-Header": "my-value",
    "X-User-ID": "user123",
}))

# All requests now include these headers
```

**`RequestIdMiddleware`** — Automatic request ID generation

```python
from britecore_sdk.api.middleware import RequestIdMiddleware

client.add_middleware(RequestIdMiddleware())

# Generates and attaches X-Request-ID header to all requests
```

**`TimeoutMiddleware`** — Set global timeout

```python
from britecore_sdk.api.middleware import TimeoutMiddleware

client.add_middleware(TimeoutMiddleware(timeout_seconds=30))

# All requests default to 30 second timeout
```

### Custom Middleware Example

```python
from britecore_sdk.api.middleware import Middleware, RequestContext, ResponseContext

class MetricsMiddleware(Middleware):
    """Track request metrics."""

    def __init__(self, metrics_client):
        self.metrics = metrics_client

    def on_request(self, ctx: RequestContext) -> RequestContext:
        ctx.extra["start_time"] = time.time()
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        elapsed = time.time() - ctx.request_context.extra.get("start_time", 0)

        self.metrics.timing(
            f"http.{ctx.method.lower()}.duration_ms",
            elapsed * 1000,
            tags={
                "method": ctx.method,
                "path": ctx.path,
                "status": ctx.status_code,
            }
        )

        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        self.metrics.increment(
            "http.errors",
            tags={"path": ctx.path, "method": ctx.method}
        )
        return error

# Usage
client.add_middleware(MetricsMiddleware(my_metrics_client))
```

### OpenTelemetry Integration

```python
from opentelemetry import trace
from britecore_sdk.api.middleware import Middleware, RequestContext, ResponseContext

class OTelMiddleware(Middleware):
    """Distributed tracing with OpenTelemetry."""

    def __init__(self):
        self.tracer = trace.get_tracer(__name__)

    def on_request(self, ctx: RequestContext) -> RequestContext:
        ctx.extra["span"] = self.tracer.start_as_current_span(
            f"http.{ctx.method.lower()}"
        )
        span = ctx.extra["span"]
        span.set_attribute("http.method", ctx.method)
        span.set_attribute("http.url", ctx.path)
        return ctx

    def on_response(self, ctx: ResponseContext) -> ResponseContext:
        span = ctx.request_context.extra.get("span")
        if span:
            span.set_attribute("http.status_code", ctx.status_code)
            span.end()
        return ctx

    def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
        span = ctx.extra.get("span")
        if span:
            span.record_exception(error)
            span.end()
        return error

client.add_middleware(OTelMiddleware())
```

### Middleware Execution Order

Middleware executes in registration order:

```python
client.add_middleware(RequestIdMiddleware())          # 1st
client.add_middleware(LoggingMiddleware())            # 2nd
client.add_middleware(HeaderInjectionMiddleware(...)) # 3rd

# Request flow: RequestId → Logging → Headers → HTTP
# Response flow: HTTP → Headers (reversed) → Logging → RequestId
```

---

## Phase 5: Pagination Iterators

### Overview

Automatic pagination with iterator pattern eliminates manual page management.

### Iterator Functions Available

| Function | Returns | Async Equivalent |
|----------|---------|------------------|
| `iter_quotes()` | Iterator[dict] | `aiter_quotes()` |
| `iter_policies()` | Iterator[dict] | `aiter_policies()` |
| `iter_contacts()` | Iterator[dict] | `aiter_contacts()` |

### Usage Examples

**Simple Iterator:**

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.iterators import iter_quotes

client = BritecoreAPIClient("site").init_client()

for quote in iter_quotes(client=client, limit=100):
    print(f"Quote: {quote['quoteNumber']}")
    process_quote(quote)
```

**Collect All Results:**

```python
# Get all quotes as a list
all_quotes = list(iter_quotes(client=client))
print(f"Total quotes: {len(all_quotes)}")
```

**Async Iterator:**

```python
from britecore_sdk import AsyncBritecoreAPIClient
from britecore_sdk.api.iterators import aiter_quotes

async with AsyncBritecoreAPIClient("site").init_client() as client:
    async for quote in aiter_quotes(client=client):
        print(f"Quote: {quote['quoteNumber']}")
        await process_quote(quote)
```

**With Filters:**

```python
for policy in iter_policies(
    client=client,
    limit=50,
    status="active",
    customer_id="cust_123"
):
    print(f"Policy: {policy['policyNumber']}")
```

### Adoption Pattern

**Earlier manual pagination pattern:**

```python
page = 1
all_quotes = []
while True:
    response = list_quotes(page=page, limit=100)
    all_quotes.extend(response["data"])
    if len(response["data"]) < 100:
        break
    page += 1
```

**Iterator-based pattern introduced in 2.0.0:**

```python
# Option 1: Iterator
for quote in iter_quotes(client=client):
    process_quote(quote)

# Option 2: Collect all
all_quotes = list(iter_quotes(client=client))

# Option 3: With limit
for quote in iter_quotes(client=client, limit=50):
    process_quote(quote)
```

### Combining with Response Models

```python
from britecore_sdk.api.iterators import iter_quotes
from britecore_sdk.api.responses import QuoteResponse

for quote_dict in iter_quotes(client=client):
    quote = QuoteResponse.from_api(quote_dict)
    print(f"Premium: {quote.premium}")  # Type-safe access
```

---

## Combining Phases 2-5

### Full Example: Type-Safe Error Handling with Iteration

```python
from britecore_sdk import BritecoreAPIClient, configure_logging
from britecore_sdk.api.iterators import iter_quotes
from britecore_sdk.api.responses import QuoteResponse
from britecore_sdk.api.middleware import LoggingMiddleware, RequestIdMiddleware
from britecore_sdk.exceptions import NotFoundError, ValidationError, RateLimitError
import logging

# Setup
configure_logging(level=logging.DEBUG)
client = BritecoreAPIClient("production").init_client()
client.add_middleware(RequestIdMiddleware())
client.add_middleware(LoggingMiddleware())

# Iterate with error handling
processed = 0
errors = []

try:
    for quote_dict in iter_quotes(client=client, limit=100):
        try:
            # Type-safe model
            quote = QuoteResponse.from_api(quote_dict)

            # Process with known types
            if quote.premium > 1000:
                print(f"High-value quote: {quote.quote_number}")
                # Handle high-value quote

            processed += 1

        except ValidationError as e:
            logger.error(
                f"Validation error processing quote: {e.detail}",
                extra={"request_id": e.request_id}
            )
            errors.append({"quote": quote_dict, "error": e})
        except Exception as e:
            logger.exception(f"Unexpected error processing quote")
            errors.append({"quote": quote_dict, "error": e})

except RateLimitError as e:
    logger.warning(f"Rate limited while iterating: {e.detail}")
    # Could implement backoff and retry
except NotFoundError as e:
    logger.warning(f"Resource not found: {e.detail}")
except Exception as e:
    logger.critical(f"Critical error during iteration: {e}")

print(f"Processed: {processed}")
print(f"Errors: {len(errors)}")
```

---

## Migration Checklist: Phases 2-5

### Phase 2: Typed Responses
- [ ] Update endpoints to return typed models instead of `Any`/`dict`
- [ ] Create `ResponseEnvelope` wrappers for complex responses
- [ ] Update tests to assert typed model properties
- [ ] Update examples to show typed response usage

### Phase 3: Error Model
- [ ] Add `status_code`, `error_code`, `request_id` to all exceptions
- [ ] Extract error codes from API responses
- [ ] Update `process_result()` to populate exception metadata
- [ ] Add `raw_payload` support to exceptions
- [ ] Update error handling patterns in codebase

### Phase 4: Middleware
- [ ] Implement middleware hook system in `BritecoreAPIClient.do_request()`
- [ ] Create `add_middleware()` and `remove_middleware()` methods
- [ ] Implement built-in middleware (logging, request ID, headers, timeout)
- [ ] Update examples with middleware usage
- [ ] Document OpenTelemetry integration pattern

### Phase 5: Pagination
- [ ] Create `iter_*()` and `aiter_*()` functions for each list endpoint
- [ ] Add tests for iterator pagination logic
- [ ] Combine with typed response models
- [ ] Update examples with iterator patterns
- [ ] Document edge cases (empty results, single page, etc.)

---

## Performance Considerations

### Typed Response Models
- **Minimal overhead**: Dataclass initialization is very fast (< 1ms typically)
- **Memory**: Models use same memory as dicts, plus type metadata
- **Recommendation**: Always use typed models for better maintainability

### Pagination Iterators
- **Lazy loading**: Pages fetched on-demand, not upfront
- **Memory efficient**: Process results one page at a time
- **Recommendation**: Use iterators for large result sets

### Middleware
- **Hook overhead**: Each middleware adds ~1-2ms per request
- **Chain length**: Keep chain < 5 middleware for best performance
- **Recommendation**: Use middleware only when needed, avoid heavy processing

---

## See Also

- [V2_ROADMAP.md](../V2_ROADMAP.md) — Full v2.0.0 roadmap
- [PHASE1-CLIENT-LIFECYCLE.md](./PHASE1-CLIENT-LIFECYCLE.md) — Phase 1 details
- [DEPRECATION.md](../DEPRECATION.md) — Deprecation policy
