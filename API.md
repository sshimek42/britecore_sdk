# API Reference

*Last updated: April 28, 2026*
*Document type: Living reference guide*

**BriteCore Libraries** - API endpoint reference

---

## Overview

This document provides a reference for implemented SDK endpoint wrappers.

External API docs are available at [https://api.britecore.com/](https://api.britecore.com/), but
`api_specs/current/britecore.json` in this repository remains the canonical contract for this SDK.

Files under `api_specs/legacy/` are archival reference material for historical
research and backlog planning, not the default support contract for the current SDK.

The SDK surfaces wrappers under `src/britecore_sdk/api/api_calls/v2/`.
Endpoints without a `v2` equivalent are available in
`src/britecore_sdk/api/api_calls/v1/`.

For known wrapper/spec drift currently tracked in tests, see
`tests/unit/test_api_spec_alignment.py` (`KNOWN_SPEC_GAPS`).

See also:

- [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md) for async cache-aware wrapper usage

---

## Quick import pattern

```python
from britecore_sdk.api.api_calls import get_api_client
# Import the domain module (recommended)
from britecore_sdk.api.api_calls.v2 import policies, contacts, quotes

# Recommended: Use the lazy-initialized client (auto-loads config on first use)
client = get_api_client()
result = policies.retrieve_policy(policy_number="POL-001")
```

### Fluent one-liner + context manager (v1.1+)

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies

# init_client() returns Self, so construction + init can be one line
with BritecoreAPIClient("your_site").init_client() as client:
    result = policies.retrieve_policy(policy_number="POL-001")
# PoolManager closed automatically

# Inspect the client at any time
print(repr(client))
# BritecoreAPIClient(site='your_site', base_url='https://...', auth='oauth', initialized=True)
```

Domain modules are importable from `britecore_sdk.api.api_calls.v2`.
The API client initializes lazily on first request; use `get_api_client()` for explicit control when needed. Use `init_api_client()` only for advanced/manual re-initialization scenarios.

---

## Authentication

All API calls require authentication (automatic):

```python
# API Key Authentication (if client_id/client_secret blank)
headers = {"Authorization": "ApiKey <api_key>"}

# OAuth2 Authentication (if client_id/client_secret provided)
headers = {"Authorization": "Bearer <access_token>"}
```

---

## Request/Response Pattern

### Standard Request

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

client = get_api_client()
response = policies.retrieve_policy(
    policy_number="POL001",
    request_timeout=5,        # seconds
    request_retries=3,        # number of retries
    # ... endpoint-specific params ...
)
```

### Standard Response

For wrappers that call `process_result(...)` (the standard `v2` pattern), responses are normalized to:

```python
{
    "success": True,
    "data": {
        "id": "uuid",
        "policy_number": "POL001",
        # ... policy fields ...
    },
    "message": "Success"  # or "messages": ["msg1", "msg2"]
}
```

Some wrappers may return payloads shaped by `v1` API behavior where no `v2` equivalent exists.

---

## Async Cached Wrappers (v2)

Canonical guide: [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md)

Async wrappers are exported from `src/britecore_sdk/api/api_calls/v2/__init__.py`.
These wrappers call `AsyncBritecoreAPIClient.ado_request(...)` and use in-memory TTL caching
from `src/britecore_sdk/api/request_cache.py`.

- Use this section as a quick pointer; implementation-level async cache behavior is documented in [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md).
- Read wrappers in async `v2` are cache-aware by default, and mutation wrappers invalidate related cache namespaces on successful requests.
- Per-call cache tuning is available through `RequestParameters` (`cache_enabled`, `cache_ttl_seconds`, `cache_bypass`, `cache_invalidate_on_success`, `dedupe_in_flight`, etc.).

---

## Implemented Endpoints

Use module-level wrappers under `britecore_sdk.api.api_calls.v2`.
Current domains include:

- `accounting`, `attachments`, `billing`, `claims`, `commissions`, `contacts`
- `dashboards`, `data`, `deliverables`, `errors`, `inspections`, `insured`
- `intacct`, `lines`, `nightly_jobs`, `notes`, `notifications`, `payments`
- `policies`, `quotes`, `reports`, `return_premium`, `search`, `settings`
- `signatures`, `uploads`, `utils`, `vendors`

`v1`-only endpoint modules (import from `britecore_sdk.api.api_calls.v1`):

- `custom_ui`
- `printing`
- `payments.makemanualpolicypayment` / `payments.make_manual_policy_payment`

### Representative examples

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import (
    policies,
    contacts,
    quotes,
    reports,
    payments,
    lines,
)

init_api_client("your_site")
policy = policies.retrieve_policy(policy_number="POL001")
policy_terms = policies.retrieve_policy_terms(policy_number="POL001")

contact_data, contact_id = contacts.new_contact(
    name="Jane Doe",
    address=[{"address_line1": "123 Main", "address_city": "Madison", "address_state": "WI", "address_zip": "53703"}],
)

quote_data, quote_id = quotes.create_full_quote(quote_json={"policy_number": "POL001"})
report = reports.retrieve_report(report_id="report_uuid")

payment_methods = payments.retrieve_payment_methods(contact_ids=[contact_id])
policy_types = lines.list_policy_types(location_id="loc_uuid", effective_date_id="eff_uuid")
```

---

## Common Request Parameters

Most `v2` endpoint wrappers accept optional request override parameters:

```python
from urllib3 import Timeout, Retry

endpoint(
    # ... required and optional endpoint-specific parameters ...
    request_timeout=Timeout(total=5),      # Custom timeout (seconds)
    request_retries=Retry(total=3),        # Custom retries
)
```

Retry and timeout defaults come from config keys loaded by
`BritecoreAPIClient.init_client()`:

- `web_timeout`
- `web_timeout_long`
- `web_retry` (urllib3 retry configuration)

See `src/britecore_sdk/settings/settings.toml` for current shipped defaults.

`request_retries` should be used for idempotent/retry-safe operations only.

---

## Error Handling

### Using nested exception classes (original pattern)

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.api.api_calls.v2 import policies

client = get_api_client()
try:
    policy = policies.retrieve_policy(policy_number="INVALID")
except BritecoreError.NotFoundError as e:
    print(f"Not found: {e}")
except BritecoreError.AuthenticationError as e:
    print(f"Auth error: {e}")
except BritecoreError.RateLimitError as e:
    print(f"Rate limit hit: {e}")
except BritecoreError.Base as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Using flat exception aliases (v1.1+ — shorter imports)

```python
from britecore_sdk import NotFoundError, AuthenticationError, RateLimitError
from britecore_sdk.api.api_calls.v2 import policies

try:
    policy = policies.retrieve_policy(policy_number="INVALID")
except NotFoundError as e:
    print(f"Not found: {e}")
except AuthenticationError as e:
    print(f"Auth error: {e}")
except RateLimitError as e:
    print(f"Rate limit hit: {e}")
```

Available top-level aliases: `AuthenticationError`, `ConfigurationError`,
`NotFoundError`, `RateLimitError`, `RequestTimeoutError`, `ServerError`,
`ValidationError`. The full set (including `NoDataReturned`, `NoTokenReturned`,
`BritecoreKeyError`, etc.) is available from `britecore_sdk.exceptions`.

---

## Debug / Dry-Run Mode (v1.1+)

Pass `dry_run=True` to `do_request` (or any endpoint wrapper that forwards `**kwargs`) to
log the full request details — URL, method, headers, body — **without** sending anything to
the server. The call returns a synthetic successful payload that flows through
`process_result(...)` like a normal response.

```python
import logging
logging.basicConfig(level=logging.INFO)

from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

client = get_api_client()
# Inspect what would be sent — no network call made
preview = policies.retrieve_policy(policy_number="POL001", dry_run=True)
print(preview["dry_run"])
print(preview["headers"])
# INFO [abc12345] DRY-RUN POST https://...  body={"policy_number": "POL001"}  headers={...}
```

Client-level default dry-run is also supported:

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

init_api_client(client_dry_run=True)

# Inherits dry-run from the initialized client.
preview = policies.retrieve_policy(policy_number="POL001")

# Override for one request if needed.
live_result = policies.retrieve_policy(policy_number="POL001", dry_run=False)
```

Notes:

- `dry_run` is part of `RequestParameters` so it is accepted by every v2 endpoint wrapper.
- Dry-run responses include `dry_run`, `request_id`, `method`, `path`, `url`, `body`, `headers`,
  `auth_mode`, `auth_skipped`, and `authorization_header_source`.
- Headers are redacted by default. Pass `dry_run_include_sensitive_headers=True` only when you
  explicitly need raw header values.
- Sensitive request-body fields are always redacted in dry-run output (for example `api_key`,
  token/secret/password-like keys), even if header sensitivity overrides are enabled.
- For OAuth clients, dry-run skips token acquisition unless you explicitly pass headers.
- Async wrappers support the same behavior via `init_async_api_client(client_dry_run=True)` or
  per-call `dry_run=True`; async dry-run also bypasses cache and in-flight dedupe.

---

## Rate Limiting

The API implements rate limiting. If you receive 429 status:

```python
import time
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.api.api_calls.v2 import policies

client = get_api_client()
max_retries = 3
retry_delay = 5  # seconds

for attempt in range(max_retries):
    try:
        policy = policies.retrieve_policy(policy_number="POL001")
        break
    except BritecoreError.RateLimitError as e:
        if attempt < max_retries - 1:
            time.sleep(e.retry_after or retry_delay)
        else:
            raise
```

---

## Pagination

Some endpoints expose explicit pagination fields:

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import accounting

client = get_api_client()
page_1 = accounting.get_invoices(policy_id="uuid", page_number=1, page_size=25)
page_2 = accounting.get_invoices(policy_id="uuid", page_number=2, page_size=25)
```

---

## Filtering and Sorting

Many wrappers support optional filters and ordering fields:

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk import logger

client = get_api_client()
risks = policies.retrieve_risks(
    revision_id="revision_uuid",
    page=0,
    page_size=25,
    order_by="name",
    retrieve_remaining=False,
)
```

---

## Batch Operations

For bulk operations, use loops rather than batch endpoints (most don't exist):

```python
from britecore_sdk import logger
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

client = get_api_client()
policy_numbers = ["POL001", "POL002", "POL003"]

for policy_number in policy_numbers:
    try:
        policy = policies.retrieve_policy(policy_number=policy_number)
        # Replace with your workflow handler.
        print(policy["id"])
    except Exception as e:
        logger.error(f"Failed for {policy_number}: {e}")
```

---

## Using with Models

```python
from datetime import datetime

from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.models import BritecorePolicy
from britecore_sdk.api.api_calls.v2 import policies

client = get_api_client()
policy_model = BritecorePolicy(policy_number="POL001", effective_date=datetime.now(), policy_type_id="type_1")
api_payload = policy_model.to_dict()

response, revision_id = policies.create_policy(
    policy_number=api_payload.get("policy_number", "POL001"),
    policy_type_id=api_payload.get("policy_type_id"),
    inception_date=api_payload.get("effective_date"),
)
```

---

## Using with Validators

```python
from britecore_sdk.validators import EmailValidator, PhoneValidator
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import contacts

client = get_api_client()
email = EmailValidator.normalize_email("test@example.com")
phone = PhoneValidator.normalize_phone("5551234567")

if phone is None:
    raise ValueError("Phone number did not normalize")

contact_data, contact_id = contacts.new_contact(
    name="John Doe",
    address=[{"address_line1": "123 Main", "address_city": "Madison", "address_state": "WI", "address_zip": "53703"}],
    email=[{"email": email, "type": "home"}],
    phone=[{"phone": phone, "type": "mobile"}],
)
```

---

## Long-Running Pattern

For workflows that return progress/status fields, poll retrieval endpoints:

```python
import time
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import reports

client = get_api_client()
report_id = "report_uuid"
for _ in range(60):
    status = reports.retrieve_report(report_id=report_id)
    if status.get("status") in {"completed", "failed"}:
        break
    time.sleep(5)

---

## Examples by Use Case

For maintained runnable examples, see `examples/README.md` and
`examples/basic_api_usage.py`.

---


### About API Client Initialization

The `api_client` proxy (from `api.api_calls`) initializes lazily on first use, avoiding import-time failures if config is missing. Use `get_api_client()` for explicit initialization or to force config reload. Use `init_api_client()` only for advanced/manual re-initialization scenarios.

See [README.md](README.md) for more examples and [CONTRIBUTING.md](CONTRIBUTING.md) for adding new endpoints.

---

## Documentation Freshness

- Last verified: `2026-04-22`
- Verified against: `api_specs/current/britecore.json`, `src/britecore_sdk/api/api_calls/v1/`, and `src/britecore_sdk/api/api_calls/v2/`
- Known wrapper/spec drift is tracked in `tests/unit/test_api_spec_alignment.py` (`KNOWN_SPEC_GAPS`).
- Use module-level docs in `src/britecore_sdk/api/api_calls/v1/` and `src/britecore_sdk/api/api_calls/v2/` as the source of truth for current wrapper names.
