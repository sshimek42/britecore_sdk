# Async Caching Guide

Use this guide for exact behavior of async `v2` wrappers and cache tuning options.

## Where async wrappers live

- Wrapper exports: `src/britecore_sdk/api/api_calls/v2/__init__.py`
- Async transport: `src/britecore_sdk/api/britecore_async_api_client.py`
- Cache primitives: `src/britecore_sdk/api/request_cache.py`

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


async def main() -> None:
    # Cached read (first call live, second call cached).
    quote_1 = await aget_quote("quote_123")
    quote_2 = await aget_quote("quote_123")

    # Cached read with per-call TTL override.
    contact = await aget_contact("contact_123", cache_ttl_seconds=180)

    # Cached read with in-flight de-duplication enabled (default True).
    policy = await aretrieve_policy(
        policy_number="POL001",
        revision_state="active",
        dedupe_in_flight=True,
    )

    # Mutation invalidates quote namespace on success.
    _, created_quote_id = await acreate_full_quote({"quote": {"name": "Example"}})

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
fresh_quote = await aget_quote("quote_123", cache_bypass=True)

policy = await aretrieve_policy(
    policy_id="uuid",
    cache_enabled=True,
    cache_ttl_seconds=300,
    cache_key_parts=["tenant:acme", "view:summary"],
)
```

## Async dry-run behavior

Async clients support the same client-level dry-run default as the sync client:

```python
import asyncio

from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy


async def main() -> None:
    init_async_api_client(default_dry_run=True)
    preview = await aretrieve_policy(policy_number="POL001")
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
