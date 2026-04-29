"""
Example: Using Rate Limiting with the BriteCore SDK

This example demonstrates how to enable and configure client-side rate limiting
to ensure your application doesn't overwhelm the BriteCore API server.

Rate limiting is useful when:
- Making many requests in quick succession
- Batch processing large numbers of resources
- Running concurrent operations
- Implementing safe backoff behavior after 429 errors
"""

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk.exceptions import RateLimitError
import logging

# Enable debug logging to see rate limiting in action
logging.basicConfig(level=logging.DEBUG)

# ============================================================================
# Example 1: Enable Rate Limiting with Defaults
# ============================================================================

print("Example 1: Rate Limiting with Defaults")
print("-" * 50)

# Initialize client with rate limiting enabled (default settings)
# Default: 10 requests/second, burst size 20
client = BritecoreAPIClient("production").init_client(enable_rate_limiter=True)

print(f"Client initialized with rate limiter: {client.rate_limiter}")

# Make some requests - they'll be automatically rate-limited
for i in range(5):
    try:
        result = policies.retrieve_policy(
            policy_number=f"POL-{1000+i}",
        )
        print(f"Request {i+1} succeeded")
    except RateLimitError as e:
        print(f"Request {i+1} rate limited: {e}")
    except Exception as e:
        print(f"Request {i+1} failed: {e}")

# ============================================================================
# Example 2: Custom Rate Limiting Parameters
# ============================================================================

print("\nExample 2: Custom Rate Limiting Parameters")
print("-" * 50)

# Initialize with custom settings for conservative rate limiting
client = BritecoreAPIClient("production").init_client(
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5.0,     # 5 requests per second
    rate_limiter_burst_size=10,               # Allow burst of 10
    rate_limiter_adaptive_backoff=True,       # Back off on 429
    rate_limiter_backoff_timeout_seconds=60.0,  # Back off for 60 seconds
)

print(f"Client initialized with rate limiter: {client.rate_limiter}")

# Make requests - they'll be rate-limited at 5 req/s instead of 10 req/s
for i in range(3):
    try:
        print(f"Making request {i+1}...")
        result = policies.retrieve_policy(
            policy_number=f"POL-{2000+i}",
        )
        print(f"Request {i+1} succeeded")
    except Exception as e:
        print(f"Request {i+1} failed: {e}")

# ============================================================================
# Example 3: Monitoring Rate Limiter State
# ============================================================================

print("\nExample 3: Monitoring Rate Limiter State")
print("-" * 50)

client = BritecoreAPIClient("production").init_client(enable_rate_limiter=True)

# Get current state before any requests
state = client.rate_limiter.get_state()
print(f"Initial state: {state}")

# Make a request
try:
    result = policies.retrieve_policy(policy_number="POL-3000")
    print("Request succeeded")
except Exception as e:
    print(f"Request failed: {e}")

# Check state after request
state = client.rate_limiter.get_state()
print(f"State after request: {state}")
print(f"  - Available tokens: {state['tokens']:.2f}")
print(f"  - Burst capacity: {state['burst_size']}")
print(f"  - In backoff: {state['in_backoff']}")

# ============================================================================
# Example 4: Bypassing Rate Limiter for Critical Requests
# ============================================================================

print("\nExample 4: Bypassing Rate Limiter for Critical Requests")
print("-" * 50)

client = BritecoreAPIClient("production").init_client(enable_rate_limiter=True)

# Make a normal request (subject to rate limiting)
try:
    result = policies.retrieve_policy(
        policy_number="POL-4000",
    )
    print("Normal request succeeded (rate limited)")
except Exception as e:
    print(f"Normal request failed: {e}")

# Make a critical request that bypasses rate limiting
try:
    result = policies.retrieve_policy(
        policy_number="POL-4001",
        rate_limiter_bypass=True,  # Skip rate limiting for this request
    )
    print("Critical request succeeded (bypassed rate limiter)")
except Exception as e:
    print(f"Critical request failed: {e}")

# ============================================================================
# Example 5: Handling Rate Limit Errors
# ============================================================================

print("\nExample 5: Handling Rate Limit Errors")
print("-" * 50)

client = BritecoreAPIClient("production").init_client(enable_rate_limiter=False)

# Simulate rate limit error handling (without rate limiter to show server-side error)
try:
    result = policies.retrieve_policy(policy_number="POL-5000")
    print("Request succeeded")
except RateLimitError as e:
    print(f"Rate limit error: {e}")
    print(f"Retry after: {e.retry_after} seconds")
    # In a real application, you would implement exponential backoff here
except Exception as e:
    print(f"Request failed with other error: {e}")

# ============================================================================
# Example 6: Rate Limiter Configuration via Settings File
# ============================================================================

print("\nExample 6: Configuration via Settings File")
print("-" * 50)

print("""
Add this to your settings.toml to enable rate limiting:

[default]
rate_limiter_enabled = true
rate_limiter_requests_per_second = 10.0
rate_limiter_burst_size = 20
rate_limiter_adaptive_backoff = true
rate_limiter_backoff_timeout_seconds = 60.0

Then initialize the client without specifying rate limiter parameters:

client = BritecoreAPIClient("production").init_client()

The client will read rate limiting configuration from settings.toml.
""")

# ============================================================================
# Summary
# ============================================================================

print("\nSummary")
print("-" * 50)
print("""
Rate limiting is useful for:
1. Batch operations - make many requests safely
2. Parallel processing - multiple threads/processes
3. Graceful degradation - handle 429 errors automatically
4. Load distribution - spread requests over time

Key features:
- Token bucket algorithm for smooth rate limiting
- Configurable rate and burst size
- Adaptive backoff on 429 responses
- Per-request bypass option
- Monitoring via get_state()

For more information, see: docs/RATE_LIMITING.md
""")

