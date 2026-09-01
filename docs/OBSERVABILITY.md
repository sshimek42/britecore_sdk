# Observability & Monitoring Guide

*Last updated: April 28, 2026*
*Document type: Integration guide*

This guide covers logging, tracing, correlation IDs, and monitoring patterns for the BriteCore SDK.

---

## Overview

The SDK provides observability features for monitoring and debugging API interactions:

1. **Structured logging** — All SDK operations logged to `britecore_sdk` logger
2. **X-SDK-Request-ID headers** — Every outbound request carries short correlation ID
3. **Debug logging** — Per-request details (URL, headers redacted, response time)
4. **Async cache observability** — Cache hit/miss tracking
5. **Rate limit detection** — Automatic handling with debug output

---

## Logging Basics

### Default Behavior (No Handler)

By default, the SDK uses Python's `NullHandler` — it does not configure global logging:

```python
import britecore_sdk

# No console output even with debug code
result = britecore_sdk.api.api_calls.get_api_client()  # Silent
```

This is library-safe — your application controls logging.

### App-Owned Logging (Recommended)

Enable logging in your application and the SDK will respect it:

```python
import logging
import britecore_sdk

# Configure root logger or just britecore_sdk logger
logging.basicConfig(level=logging.INFO)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

# Now SDK debug output appears
result = britecore_sdk.api.api_calls.get_api_client()
```

**Output example:**

```text
DEBUG:britecore_sdk:[req_id: a1b2c3d4] → GET /api/v2/policies?policy_number=POL001
DEBUG:britecore_sdk:[req_id: a1b2c3d4] ← 200 OK (45ms)
```

### SDK-Managed Logging (Optional)

Use `configure_logging()` to let the SDK add its own handler:

```python
import logging
from britecore_sdk import configure_logging

# SDK adds a stream handler with custom formatter
configure_logging(level="DEBUG")

# Or with a file handler
configure_logging(level="DEBUG", log_file="/var/log/britecore_sdk.log")

# Your app can still configure other loggers
logging.getLogger("requests").setLevel(logging.WARNING)
```

---

## X-SDK-Request-ID Headers

Every outbound HTTP request carries a short correlation ID (e.g., `a1b2c3d4`):

```text
X-SDK-Request-ID: a1b2c3d4
```

This ID appears in:
- Request debug logs: `[req_id: a1b2c3d4] → GET ...`
- Response debug logs: `[req_id: a1b2c3d4] ← 200 OK`
- SDK error messages

Use the correlation ID to:
- Track a request through server logs
- Link SDK requests to BriteCore API access logs
- Debug multi-step workflows

### Capturing Correlation IDs in Your App

```python
import logging
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

logger = logging.getLogger(__name__)

# Enable debug logging to capture correlation IDs
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

# Make an API call
result = policies.retrieve_policy(policy_number="POL001")

# The correlation ID is in the debug logs
# Extract it from BriteCore response headers (if included)
if "X-SDK-Request-ID" in result.get("_headers", {}):
    correlation_id = result["_headers"]["X-SDK-Request-ID"]
    logger.info(f"Policy lookup: correlation_id={correlation_id}")
```

### Accessing Correlation IDs from Exceptions

When a request fails, SDK exceptions include `request_id` so you can correlate
errors with request logs and server-side traces.

```python
import logging
from britecore_sdk import NotFoundError
from britecore_sdk.api.api_calls.v2 import policies

logger = logging.getLogger(__name__)

try:
    policies.retrieve_policy(policy_number="INVALID")
except NotFoundError as exc:
    logger.error(
        "Policy lookup failed (request_id=%s): %s",
        exc.request_id,
        exc,
    )
```

---

## Debug Logging Levels

### Level: INFO (Default)

High-level events:

```text
INFO:britecore_sdk:Auth mode selected during init_client: oauth
INFO:britecore_sdk:Initialized BritecoreAPIClient for site: production
```

### Level: DEBUG

Detailed request/response cycle:

```text
DEBUG:britecore_sdk:[req_id: a1b2c3d4] → GET /api/v2/policies?policy_number=POL001
DEBUG:britecore_sdk:[req_id: a1b2c3d4] ← 200 OK (45ms)
DEBUG:britecore_sdk:[req_id: a1b2c3d4] Response shape: success=True, data={...}
```

### Level: WARNING

Unusual conditions:

```text
WARNING:britecore_sdk:Rate limit approaching (429 response detected)
WARNING:britecore_sdk:OAuth token refresh failed; using cached token
WARNING:britecore_sdk:Slow response time: 5234ms (threshold: 5000ms)
```

---

## Authentication Mode Detection

Enable debug logging to see which auth mode the SDK selected:

```python
import logging
from britecore_sdk.api.api_calls import init_api_client

logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

# API Key auth (client_id/client_secret blank)
client = init_api_client(
    "site1",
    base_url="https://api.example.com",
    api_key="key123"
)
# Output: "Auth mode selected during init_client: api_key"

# OAuth auth (client_id + client_secret provided)
client = init_api_client(
    "site2",
    base_url="https://api.example.com",
    client_id="id456",
    client_secret="secret789"
)
# Output: "Auth mode selected during init_client: oauth"
```

---

## Structured Logging with Context

Add request context to all logs for multi-tenant or multi-service scenarios:

```python
import logging
from britecore_sdk.api.api_calls.v2 import policies

logger = logging.getLogger(__name__)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

# Add context to all SDK logs for this request
def lookup_policy(site_name: str, policy_number: str, user_id: str):
    """Lookup a policy and log with context."""
    # Use a context filter to add site_name and user_id to all logs
    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.site_name = site_name
            record.user_id = user_id
            return True

    logger_instance = logging.getLogger("britecore_sdk")
    logger_instance.addFilter(ContextFilter())

    try:
        result = policies.retrieve_policy(policy_number=policy_number)
        logger.info(
            f"Policy lookup success",
            extra={"site_name": site_name, "user_id": user_id, "policy": policy_number}
        )
        return result
    except Exception as e:
        logger.error(
            f"Policy lookup failed: {e}",
            extra={"site_name": site_name, "user_id": user_id, "policy": policy_number}
        )
        raise
    finally:
        logger_instance.removeFilter(ContextFilter())

# Usage
lookup_policy("production", "POL001", "user123")
```

---

## Rate Limiting & Retry Observability

The SDK automatically handles rate limiting (429 responses). Monitor it with logging:

```python
import logging
from britecore_sdk.api.api_calls.v2 import policies

logging.getLogger("britecore_sdk").setLevel(logging.INFO)

# Make a request that triggers rate limiting
try:
    result = policies.retrieve_policy(policy_number="POL001")
except Exception as e:
    logger.warning(f"Rate limit exceeded, retrying: {e}")
    # SDK retries automatically (default: 5 retries with linear backoff)
```

**Configuration for rate limit behavior:**

```toml
# settings.toml
[default]
web_timeout = 5        # Request timeout
web_retry = 5          # Number of retries on 5xx errors
web_timeout_long = 50  # Timeout for long-running ops
```

---

## Audit Middleware

The SDK provides `AuditMiddleware` for structured request auditing, especially useful when
using admin-scoped credentials.

Default behavior:

- Audits write-like operations only (`audit_only_writes = true`)
- Logs structured event JSON to the `britecore_sdk` logger
- Supports `audit_callback` for external sinks (SIEM, metrics, custom audit pipelines)

Set `audit_only_writes = false` when you need full request audit trails (reads + writes).

### Configuration keys

```toml
[default]
enable_audit_middleware = true
audit_only_writes = true
audit_log_level = "info"      # info | debug
write_allowlist = []
write_denylist = []
```

### Event shape

`AuditMiddleware` emits events like:

```json
{
  "event": "sdk_request_audit",
  "method": "POST",
  "path": "/api/v2/contacts/new_contact",
  "timestamp": 1756700000.123,
  "write_operation": true
}
```

### Callback integration example

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

def send_to_audit_sink(event: dict) -> None:
    # Replace with your SIEM/event-bus publish logic.
    print("AUDIT", event)

client = BritecoreAPIClient("production").init_client(
    enable_audit_middleware=True,
    audit_only_writes=True,
    audit_log_level="info",
    audit_callback=send_to_audit_sink,
)
```

---

## Async Cache Observability

Monitor async cache hit/miss rates:

```python
import asyncio
import logging
from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

async def main():
    init_async_api_client()

    # First call — cache miss (fetches from API)
    result1 = await aretrieve_policy(policy_number="POL001")
    # DEBUG: [req_id: xxxxx] → GET /api/v2/policies?policy_number=POL001
    # DEBUG: [req_id: xxxxx] ← 200 OK (45ms)

    # Second call within TTL — cache hit (no network)
    result2 = await aretrieve_policy(policy_number="POL001")
    # DEBUG: [req_id: yyyyy] Cache hit for /api/v2/policies?policy_number=POL001

    print(f"Same data: {result1 == result2}")  # True

asyncio.run(main())
```

---

## Dry-Run Mode for Testing

Use dry-run mode to log request details without sending live requests:

```python
import logging
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

# Initialize in dry-run mode
client = init_api_client(
    "prod",
    base_url="https://api.example.com",
    api_key="key123",
    client_dry_run=True
)

# Make a call — logs show request details, no actual HTTP
result = policies.retrieve_policy(policy_number="POL001")

# Check dry-run flag in response
print(result["dry_run"])  # True
print(result["auth_skipped"])  # OAuth key acquisition skipped
```

---

## Monitoring in Production

### Recommended Logging Setup

```python
import logging
import logging.handlers

# Create logger with JSON output for ELK/Datadog compatibility
logger = logging.getLogger("britecore_sdk")
logger.setLevel(logging.INFO)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    "/var/log/app/britecore_sdk.log",
    maxBytes=10_485_760,  # 10 MB
    backupCount=5
)

# Formatter for structured logging
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

### Metrics to Monitor

Use your application's metrics system to track:

```python
import time
import logging
from britecore_sdk.api.api_calls.v2 import policies

logger = logging.getLogger(__name__)
metrics = {}  # Or use prometheus, datadog, etc.

# Track request latency
start = time.time()
result = policies.retrieve_policy(policy_number="POL001")
latency_ms = (time.time() - start) * 1000

metrics["policy_lookup_latency_ms"] = latency_ms
logger.info(f"Policy lookup: {latency_ms:.1f}ms")

# Track errors
try:
    result = policies.retrieve_policy(policy_number="INVALID")
except Exception as e:
    metrics["policy_lookup_error_count"] = metrics.get("policy_lookup_error_count", 0) + 1
    logger.error(f"Policy lookup error: {e}")
```

---

## Correlation ID Propagation (Distributed Tracing)

Pass correlation IDs to downstream services:

```python
import logging
import uuid
from britecore_sdk.api.api_calls.v2 import policies

logger = logging.getLogger(__name__)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

def process_policy_in_workflow(policy_number: str, workflow_id: str = None):
    """
    Process a policy and propagate trace ID to downstream services.
    """
    workflow_id = workflow_id or str(uuid.uuid4())

    # Fetch from BriteCore (SDK adds X-SDK-Request-ID automatically)
    result = policies.retrieve_policy(policy_number=policy_number)

    # Extract SDK correlation ID from debug logs or response
    # Use the same ID in calls to downstream services
    logger.info(
        f"Fetched policy from BriteCore",
        extra={
            "workflow_id": workflow_id,
            "policy_number": policy_number,
            "source": "britecore_sdk"
        }
    )

    # Call downstream service with same workflow_id
    # This allows end-to-end trace reconstruction
    downstream_result = call_internal_service(
        policy_number=policy_number,
        workflow_id=workflow_id
    )

    return downstream_result
```

---

## Troubleshooting with Logs

### "No output from SDK"

**Solution:** Enable debug logging in your app:

```python
import logging
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO)
```

### "Which auth mode is being used?"

**Solution:** Check INFO logs during init:

```python
logging.getLogger("britecore_sdk").setLevel(logging.INFO)
client = init_api_client("site")
# Look for: "Auth mode selected during init_client: api_key" or "oauth"
```

### "Requests are timing out"

**Solution:** Enable debug logs to see response times:

```python
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
# Look for: "[req_id: xxxxx] ← 200 OK (5234ms)"
# Compare against web_timeout setting
```

### "Rate limit is being hit"

**Solution:** Check for warnings:

```python
logging.getLogger("britecore_sdk").setLevel(logging.WARNING)
# Look for: "Rate limit approaching (429 response detected)"
```

---

## See Also

- [GETTING_STARTED.md](../GETTING_STARTED.md) — Initial logging setup
- [docs/MULTI_TENANCY.md](MULTI_TENANCY.md) — Including site context in logs
- [CONFIG_MANAGEMENT.md](../CONFIG_MANAGEMENT.md) — Timeout and retry configuration
