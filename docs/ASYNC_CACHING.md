# Async Caching Guide

Use this guide for exact behavior of async `v2` wrappers, transport selection, and cache tuning options.

## Where async wrappers live

- Wrapper exports: `src/britecore_sdk/api/api_calls/v2/__init__.py`
- Async transport: `src/britecore_sdk/api/britecore_async_api_client.py`
- Cache primitives: `src/britecore_sdk/api/request_cache.py`

## Transport modes

`AsyncBritecoreAPIClient` supports two transport backends via the `async_transport`
constructor kwarg:

| Mode | Value | Behavior | Extra required |
| --- | --- | --- | --- |
| Threaded (default) | `"threaded"` | Wraps sync urllib3 client in `asyncio.to_thread` | None |
| Native async | `"httpx"` | Uses `httpx.AsyncClient` for true non-blocking I/O | `britecore_sdk[async-http]` |

### Threaded transport (default)

No extra packages needed. Existing code continues to work without changes.

```python
from britecore_sdk.api import AsyncBritecoreAPIClient

# default — threaded transport
client = AsyncBritecoreAPIClient(target_site="prod")
```

### httpx native async transport

Install the optional extra first:

```bash
pip install britecore_sdk[async-http]
```

```python
from britecore_sdk.api import AsyncBritecoreAPIClient

client = AsyncBritecoreAPIClient(target_site="prod", async_transport="httpx")
```

You can inject a pre-built `httpx.AsyncClient` for connection pool sharing or testing:

```python
import httpx
from britecore_sdk.api import AsyncBritecoreAPIClient

shared_httpx = httpx.AsyncClient(timeout=30)
client = AsyncBritecoreAPIClient(
    target_site="prod",
    async_transport="httpx",
    httpx_client=shared_httpx,
)
```

> **Note:** Dry-run requests always use the threaded transport even in `httpx` mode,
> since they do not actually send a network request.

## Default behavior

Read wrappers in async `v2` enable caching by default:

- Quotes (`aget_quote`): namespace `quotes`, TTL `60` seconds
- Contacts (`aget_contact`, `afind_contact_by_params`): namespace `contacts`, TTL `60` seconds
- Policies (`aretrieve_policy`, `aretrieve_policy_snapshot`, etc.): namespace `policies`, TTL `60` seconds

Mutation wrappers invalidate related read namespaces on successful (`HTTP 200`) responses:

- Quote mutations invalidate `quotes`
- Contact mutations invalidate `contacts`
- Policy mutations invalidate `policies`

## Exact usage

```python
import asyncio

from britecore_sdk.api.api_calls.v2 import (
    acreate_full_quote,
    aget_contact,
    aget_quote,
    aretrieve_policy,
)
from britecore_sdk.api.api_calls import get_async_api_client, init_async_api_client


async def main() -> None:
    init_async_api_client("your_site")
    client = get_async_api_client()

    # Cached read (first call live, second call cached).
    quote_1 = await aget_quote("quote_123", client=client)
    quote_2 = await aget_quote("quote_123", client=client)

    # Cached read with per-call TTL override.
    contact = await aget_contact("contact_123", client=client, cache_ttl_seconds=180)

    # Cached read with in-flight de-duplication enabled (default True).
    policy = await aretrieve_policy(
        policy_number="POL001",
        client=client,
        revision_state="active",
        dedupe_in_flight=True,
    )

    # Mutation invalidates quote namespace on success.
    _, created_quote_id = await acreate_full_quote({"quote": {"name": "Example"}}, client=client)

    print(quote_1, quote_2, contact, policy, created_quote_id)


asyncio.run(main())
```

## Cache controls (`RequestParameters`)

All async wrappers accept these optional kwargs:

- `cache_enabled`: enable/disable caching for a call
- `cache_ttl_seconds`: TTL override in seconds
- `cache_namespace`: namespace label used by invalidation
- `cache_key_parts`: additional deterministic cache key fragments
- `cache_bypass`: force live request and skip cache read/write
- `cache_invalidate_on_success`: namespaces to invalidate after successful mutation
- `dedupe_in_flight`: deduplicate concurrent identical requests
- `dry_run`: return a synthetic success payload without sending a live request
- `dry_run_include_sensitive_headers`: include unredacted headers in dry-run output

Example overrides:

```python
from britecore_sdk.api.api_calls import get_async_api_client

client = get_async_api_client()

fresh_quote = await aget_quote("quote_123", client=client, cache_bypass=True)

policy = await aretrieve_policy(
    policy_id="uuid",
    client=client,
    cache_enabled=True,
    cache_ttl_seconds=300,
    cache_key_parts=["tenant:acme", "view:summary"],
)
```

## Async dry-run behavior

Async clients support the same client-level dry-run default as the sync client:

```python
import asyncio

from britecore_sdk.api.api_calls import get_async_api_client, init_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy


async def main() -> None:
    init_async_api_client(client_dry_run=True)
    client = get_async_api_client()
    preview = await aretrieve_policy(policy_number="POL001", client=client)
    print(preview["dry_run"])
    print(preview["auth_skipped"])


asyncio.run(main())
```

Notes:

- Async dry-run requests bypass async cache reads/writes and in-flight dedupe.
- For OAuth sites, async dry-run skips token acquisition unless you explicitly pass headers.
- Per-call `dry_run=False` overrides an inherited client default.
- Sensitive request-body fields are always redacted in dry-run output (for example
  `api_key` and token/secret/password-like keys), even when sensitive headers are included.

## Manage cache manually

The module-level async client instance is shared and lazily initialized:

```python
from britecore_sdk.api.api_calls import get_async_api_client

client = get_async_api_client()
removed = client.invalidate_cache_namespaces(["quotes", "contacts", "policies"])
client.clear_cache()
print(removed)
```

## Notes

- Authorization headers are excluded from cache key generation.
- Cache writes happen only on successful (`HTTP 200`) responses.
- `cache_bypass=True` also bypasses in-flight dedupe for that request.
