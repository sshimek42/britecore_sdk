# Migration Guide: `2.4.x` -> `2.5.x`

*Last updated: September 8, 2026*
*Document type: Migration guidance*

`2.5.x` focuses on migration signaling for upcoming `v3.0.0` removals.
This release line keeps behavior compatible, but emits `DeprecationWarning` on legacy runtime paths.

## What changed in `2.5.x`

Three legacy patterns now emit runtime warnings:

| Deprecated pattern | Warning trigger | Migration target |
| --- | --- | --- |
| Implicit wrapper fallback (`client=` omitted) | Calling wrappers/workflows without explicit client | Pass `client=` directly, or scope sync calls with `use_api_client(...)` |
| Global lifecycle helpers (`init_api_client(...)`, `init_async_api_client(...)`, `reset_api_client()`) as primary app pattern | Calling those helpers in normal app flows | Construct explicit client instances and pass them to wrappers/workflows |
| Legacy batch alias keys (`quote_id`/`quote_data`, `contact_id`/`contact_data`) | Running batch helpers with default `include_legacy_keys=True` | Use canonical `id`/`data` keys and set `include_legacy_keys=False` |

Planned removal target for all three: `v3.0.0`.

## Quick migration checklist

- [ ] Prefer explicit client construction at app startup.
- [ ] Pass explicit `client=` in wrapper and workflow calls.
- [ ] Update batch consumers to read `id`/`data` only.
- [ ] Set `include_legacy_keys=False` in batch helpers once consumers are updated.
- [ ] Turn deprecations into test failures in CI to prevent regressions.

## Before/after examples

### 1) Wrapper calls: implicit fallback -> explicit `client=`

Before (deprecated path):

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import quotes

init_api_client("production")
quote = quotes.retrieve_quote(quote_number="Q-123")
```

After (recommended):

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes

client = BritecoreAPIClient("production").init_client()
quote = quotes.retrieve_quote(quote_number="Q-123", client=client)
```

### 2) Sync multi-call scope: module-global state -> scoped binding

If explicit `client=` threading everywhere is not feasible yet, use `use_api_client(...)` as an intermediate migration step for sync code.

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls import use_api_client
from britecore_sdk.api.api_calls.v2 import policies

client = BritecoreAPIClient("production").init_client()
with use_api_client(client):
    # Existing wrapper calls can run in this scope while you migrate.
    policy = policies.retrieve_policy(policy_number="POL-123")
```

### 3) Batch results: legacy aliases -> canonical keys

Before (default emits warning):

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

result = create_full_quotes_batch(quotes_json)
legacy_id = result["results"][0]["quote_id"]
```

After (recommended):

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

result = create_full_quotes_batch(quotes_json, include_legacy_keys=False)
quote_id = result["results"][0]["id"]
quote_data = result["results"][0]["data"]
```

Async batch follows the same pattern (`acreate_full_quotes_batch`, `acreate_contacts_batch`).

## CI guardrail: fail on deprecations

Use Python warnings flags in CI to catch remaining migration gaps early.

```bash
pytest -W error::DeprecationWarning
```

For more selective enforcement, scope by module path:

```bash
pytest -W error::DeprecationWarning:britecore_sdk.api
```

## Related docs

- `DEPRECATION.md` - active deprecation policy and removal targets
- `CHANGELOG.md` - shipped/announced release details
- `TROUBLESHOOTING.md` - diagnosis steps for warning behavior and migration edge cases
