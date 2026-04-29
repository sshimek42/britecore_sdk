# Rate Limiting in BriteCore SDK

This document describes the client-side rate limiting feature in the BriteCore SDK.
Rate limiting helps prevent overloading the API server and gracefully handles rate limit
responses (HTTP 429) from the server.

## Overview

The BriteCore SDK includes an **optional, opt-in** client-side rate limiter that uses a
**token bucket algorithm** to enforce a configurable request rate. When enabled, the rate
limiter automatically:

- **Throttles outbound requests** to stay below a configured rate limit
- **Allows controlled bursts** of traffic up to a configurable burst size
- **Automatically backs off** when the server responds with HTTP 429 (Too Many Requests)
- **Respects server hints** via the `Retry-After` header

Rate limiting is **disabled by default** and must be explicitly enabled. It applies
per-API-client instance, so multiple clients can have different rate limiting settings.

## Why Use Rate Limiting?

Rate limiting is useful when:

- You're making many requests to the BriteCore API in quick succession
- You want to reduce the risk of hitting the server's rate limits
- You need to distribute load across time windows
- You're batch-processing large numbers of resources

## Quick Start

### Enable Rate Limiting at Client Initialization

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

# Enable rate limiting with defaults (10 req/s, burst size 20)
client = BritecoreAPIClient("production").init_client(enable_rate_limiter=True)

# Requests will now be automatically rate-limited
result = client.do_request(path="/api/v2/policies", json={...})
```

### Configure Rate Limiting Parameters

```python
client = BritecoreAPIClient("production").init_client(
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5.0,   # 5 requests per second
    rate_limiter_burst_size=10,             # Allow up to 10-request bursts
    rate_limiter_adaptive_backoff=True,     # Back off on 429 responses
    rate_limiter_backoff_timeout_seconds=60.0,  # Back off for 60 seconds
)
```

### Use via RequestParameters

Since rate limiting is configured at the client level, it applies to all requests.
However, you can bypass rate limiting for specific requests:

```python
from britecore_sdk.api.api_calls.v2 import policies

# This request will skip rate limiting
result = policies.retrieve_policy(
    policy_number="POL-123",
    rate_limiter_bypass=True,  # Skip rate limiting for this call
)
```

## Configuration

### Via settings.toml (recommended for most users)

Add rate limiting configuration to your `settings.toml`:

```toml
[default]
rate_limiter_enabled = true
rate_limiter_requests_per_second = 10.0
rate_limiter_burst_size = 20
rate_limiter_adaptive_backoff = true
rate_limiter_backoff_timeout_seconds = 60.0

[production]
# More conservative for production
rate_limiter_requests_per_second = 5.0
rate_limiter_burst_size = 15

[development]
# More aggressive for development
rate_limiter_requests_per_second = 20.0
rate_limiter_burst_size = 40
```

### Via init_client Parameters

Override settings by passing parameters to `init_client()`:

```python
client = BritecoreAPIClient("production").init_client(
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5.0,
)
```

### Via Environment Variables

Configure rate limiting via environment variables (highest priority):

```bash
export BRITECORE_SDK_RATE_LIMITER_ENABLED=true
export BRITECORE_SDK_RATE_LIMITER_REQUESTS_PER_SECOND=10.0
export BRITECORE_SDK_RATE_LIMITER_BURST_SIZE=20
export BRITECORE_SDK_RATE_LIMITER_ADAPTIVE_BACKOFF=true
export BRITECORE_SDK_RATE_LIMITER_BACKOFF_TIMEOUT_SECONDS=60.0
```

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rate_limiter_enabled` | bool | `false` | Enable/disable the rate limiter |
| `rate_limiter_requests_per_second` | float | `10.0` | Target request rate (requests per second) |
| `rate_limiter_burst_size` | int | `20` | Maximum burst capacity (number of requests) |
| `rate_limiter_adaptive_backoff` | bool | `true` | Automatically back off on 429 responses |
| `rate_limiter_backoff_timeout_seconds` | float | `60.0` | Duration to back off after a 429 response |

### Recommended Settings

- **Conservative (safe)**: `requests_per_second=5, burst_size=10` — suitable for production with strict rate limits
- **Moderate (balanced)**: `requests_per_second=10, burst_size=20` — default, good general-purpose setting
- **Aggressive (high throughput)**: `requests_per_second=20, burst_size=40` — suitable if the server permits high rates

## How It Works

### Token Bucket Algorithm

The rate limiter uses a **token bucket** to control request rates:

1. **Tokens represent requests**: Each outgoing HTTP request consumes one token
2. **Tokens are added at a fixed rate**: New tokens are added to the bucket at the
   configured `requests_per_second` rate (e.g., 2 tokens/second = 1 token every 500ms)
3. **Bucket has a maximum capacity**: The bucket can hold at most `burst_size` tokens
4. **Requests wait for tokens**: If no tokens are available, the request is delayed
   until a token becomes available

### Example

With `requests_per_second=10` and `burst_size=20`:

```
Time 0s:   Bucket full (20 tokens)
           Request 1-20 proceed instantly (consume 20 tokens)
           Bucket now: 0 tokens

Time 0.1s: 1 new token added (10 req/s → 1 token per 100ms)
           Request 21 proceeds (consume 1 token)
           Bucket now: 0 tokens

Time 0.2s: 1 new token added
           Request 22 proceeds (consume 1 token)
           Bucket now: 0 tokens

Time 1.0s: 8 new tokens added (didn't consume any for 0.8s after time 0.2s)
           Requests 23-30 proceed instantly (consume 8 tokens)
           Bucket now: 0 tokens
```

### Adaptive Backoff

When the server responds with HTTP 429 (Too Many Requests), the SDK:

1. Extracts the `Retry-After` header from the response (if present)
2. Activates "backoff mode" for the specified duration (or `backoff_timeout_seconds` if no header)
3. During backoff, **all requests are delayed** until the backoff period expires
4. After backoff expires, normal rate limiting resumes

This prevents cascading rate limit errors and allows the server to recover.

Example:

```
Server responds: HTTP 429 with Retry-After: 30

Rate limiter records this and enters backoff:
  - For the next 30 seconds, ALL requests wait for backoff to expire
  - After 30 seconds, the rate limiter resumes normal token bucket operation
  - If another 429 is received during recovery, backoff is re-triggered
```

## Logging

The rate limiter logs important events:

### INFO Level: Backoff Events

```
WARNING:britecore_sdk:Rate limit response received, backing off for 60.0 seconds (adaptive_backoff_enabled=True)
```

### DEBUG Level: Rate Limit Delays

```
DEBUG:britecore_sdk:[req_abc123] Rate limited: delayed 0.234s
```

Enable debug logging to see rate limiting in action:

```python
import logging
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
```

## Monitoring Rate Limiter State

### Check Current State

```python
client = BritecoreAPIClient("production").init_client(enable_rate_limiter=True)

# Get a snapshot of the rate limiter state
state = client.rate_limiter.get_state()
print(state)
# Output:
# {
#     'tokens': 15.2,
#     'burst_size': 20,
#     'requests_per_second': 10.0,
#     'in_backoff': False,
#     'backoff_remaining': 0.0,
# }
```

### State Fields

| Field | Type | Description |
|-------|------|-------------|
| `tokens` | float | Current number of available tokens |
| `burst_size` | int | Maximum token capacity |
| `requests_per_second` | float | Token replenishment rate |
| `in_backoff` | bool | Whether currently in backoff period |
| `backoff_remaining` | float | Seconds until backoff expires (0 if not backing off) |

### String Representation

```python
print(client.rate_limiter)
# Output: RateLimiter(requests_per_second=10.0, burst_size=20, tokens=18.50, in_backoff=False)
```

## Advanced Usage

### Reset Rate Limiter

Clear all state (useful for testing):

```python
client.rate_limiter.reset()
```

### Manually Trigger Backoff

For testing or simulation:

```python
from britecore_sdk.api.rate_limiter import RateLimiter

limiter = RateLimiter()
limiter.record_rate_limit_response(retry_after=30)
```

### Access Direct Rate Limiter Methods

```python
client = BritecoreAPIClient("production").init_client(enable_rate_limiter=True)

# Acquire a token with timeout
try:
    delay = client.rate_limiter.acquire(timeout=5.0)
    print(f"Delayed {delay}s before acquiring token")
except TimeoutError:
    print("Rate limiter timeout exceeded")

# Get state
state = client.rate_limiter.get_state()
```

## Best Practices

### 1. Start Conservative, Adjust Based on Feedback

```python
# Start with conservative settings
client = BritecoreAPIClient("production").init_client(
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5.0,
)

# Monitor logs and adjust upward if you see no 429 errors
```

### 2. Use Different Settings Per Environment

```toml
[development]
rate_limiter_enabled = true
rate_limiter_requests_per_second = 20.0

[staging]
rate_limiter_enabled = true
rate_limiter_requests_per_second = 10.0

[production]
rate_limiter_enabled = true
rate_limiter_requests_per_second = 5.0
```

### 3. Monitor Rate Limiter Logs

Enable debug logging to see when rate limiting is active:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 4. Don't Bypass Rate Limiter Unnecessarily

Use `rate_limiter_bypass=True` only for critical requests that must proceed immediately:

```python
# Only bypass for truly critical requests
result = critical_endpoint(
    account_id="ACC-123",
    rate_limiter_bypass=True,
)
```

### 5. Handle RateLimitError Gracefully

If you need to distinguish between client-side and server-side rate limits:

```python
from britecore_sdk.exceptions import RateLimitError

try:
    result = policies.retrieve_policy(policy_number="POL-123")
except RateLimitError as e:
    print(f"Rate limited: {e.retry_after}s wait recommended")
    # Retry with exponential backoff
```

## Comparison: Client-Side vs Server-Side Rate Limiting

| Aspect | Client-Side (SDK) | Server-Side (429) |
|--------|-------------------|-------------------|
| **Activation** | Opt-in, explicit | Automatic |
| **When it helps** | Proactive (before hitting limit) | Reactive (after hitting limit) |
| **Configuration** | Fully configurable | Server-defined |
| **Recommended use** | Batch operations, bulk imports | Fallback mechanism |
| **Overhead** | Minimal delay for throughput control | Request retries required |
| **Best with** | Known rate limits | Unknown/variable limits |

## Troubleshooting

### Rate Limiter Seems Too Aggressive (Requests Waiting a Long Time)

**Cause**: `requests_per_second` is set too low

**Solution**: Increase the rate:

```python
client = BritecoreAPIClient("production").init_client(
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=15.0,  # Increase from 5.0
)
```

### Getting 429 Errors Despite Rate Limiter Enabled

**Cause**: Concurrent requests from multiple processes/threads, or burst size too small

**Solutions**:
1. Increase burst size to absorb spikes
2. Reduce `requests_per_second` further
3. Implement application-level serialization (mutex/lock)

```python
client = BritecoreAPIClient("production").init_client(
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5.0,
    rate_limiter_burst_size=30,  # Increase burst capacity
)
```

### Rate Limiter Backing Off After 429

**Expected behavior**: This is working as designed!

When a 429 response is received:
- The rate limiter enters backoff mode
- All requests wait for the backoff duration
- This allows the server to recover
- After backoff, requests resume at the configured rate

**To see backoff activity**:

```python
import logging
logging.getLogger("britecore_sdk").setLevel(logging.WARNING)  # See backoff messages
```

## See Also

- [BriteCore API documentation](https://api.britecore.io/docs) for server-side rate limits
- [Configuration Management](CONFIG_MANAGEMENT.md) for settings file hierarchy
- [Troubleshooting](TROUBLESHOOTING.md) for common issues

