# System Architecture

*Last updated: April 8, 2026*
*Document type: Living design reference*

**BriteCore Libraries** - Technical design and component overview

---

## High-Level Architecture

```text

┌─────────────────────────────────────────────────────────┐
│                    Application Layer                    │
│          (Your code using BriteCore Libraries)          │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                       │
│   • Models         (Contact, Policy, Quote)             │
│   • Validators     (Email, Phone, Address, Name)        │
│   • Maps           (Regex patterns, Field mappings)     │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                        API Layer                        │
│   • Endpoints        (current API + async wrappers)     │
│   • Sync Client      (Request/Response handling)        │
│   • Async Client     (TTL cache, in-flight dedup)       │
│   • Auth             (API Key or OAuth2)                │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                   │
│   • Config         (Dynaconf, settings + secrets)       │
│   • Utilities      (ODBC, Selenium, Menus)              │
│   • Transport      (urllib3, OAuth token)               │
└─────────────────────────────────────────────────────────┘

```

---

## Component Breakdown

### 1. Domain Layer

**Purpose:** Type-safe domain models and data validation

**Components:**

```text

src/britecore_libraries/
├── models/
│   ├── contact.py     # BritecoreContact class
│   ├── policy.py      # BritecorePolicy class
│   ├── quote.py       # BritecoreQuote class
│   └── __init__.py    # Exports
├── validators/
│   ├── address_validator.py    # Address validation
│   ├── email_validator.py      # Email validation
│   ├── name_validator.py       # Name normalization
│   ├── phone_validator.py      # Phone validation
│   └── __init__.py             # Exports
├── maps/
│   ├── britecore_agency_map.py         # Agency regex patterns
│   ├── britecore_field_map.py          # Field mappings
│   ├── britecore_policy_map.py         # Policy regex patterns
│   └── __init__.py                     # Map exports + regex loader
├── resources/
│   └── zip_codes.csv           # Bundled ZIP code reference data
└── constants.py                # Shared constants

```

**Flow:**

```python

# Raw data
data = {"name": "john doe", "email": "JOHN@EXAMPLE.COM"}

# Validation & Normalization
contact = BritecoreContact(name=data["name"], ...)
validated = contact.process_contact()

# Output ready for API
{"name": "John Doe", "email": "john@example.com", ...}

```

> **Note:** Map files (`britecore_agency_map.py`, `britecore_field_map.py`,
> `britecore_policy_map.py`) contain site-specific regex data and are gitignored.
> See [docs/MAP_FILES.md](docs/MAP_FILES.md) for map module layout and expected format.

---

### 2. API Layer

**Purpose:** Unified interface to BriteCore REST API

**Components:**

```text

src/britecore_libraries/api/
├── britecore_api_client.py              # Main sync API client
├── britecore_async_api_client.py        # Async facade with TTL cache
├── britecore_oauth_token_manager.py     # OAuth2 token handling
├── request_cache.py                     # Thread-safe TTL response cache
├── types.py                             # Shared type definitions
├── api_calls/
│   ├── __init__.py                      # Lazy init + exports
│   └── v2/                              # v2 API endpoints
│       ├── accounting.py
│       ├── async_contacts.py            # Async + cached contact wrappers
│       ├── async_policies.py            # Async + cached policy wrappers
│       ├── async_quotes.py              # Async + cached quote wrappers
│       ├── attachments.py
│       ├── billing.py
│       ├── claims.py
│       ├── commissions.py
│       ├── contacts.py
│       ├── custom_ui.py
│       ├── dashboards.py
│       ├── data.py
│       ├── deliverables.py
│       ├── errors.py
│       ├── inspections.py
│       ├── insured.py
│       ├── intacct.py
│       ├── lines.py
│       ├── nightly_jobs.py
│       ├── notes.py
│       ├── notifications.py
│       ├── payments.py
│       ├── policies.py
│       ├── printing.py
│       ├── quotes.py
│       ├── reports.py
│       ├── return_premium.py
│       ├── search.py
│       ├── settings.py
│       ├── signatures.py
│       ├── uploads.py
│       ├── utils.py
│       ├── vendors.py
│       └── __init__.py
└── __init__.py

```

**Request/Response Flow:**

```python

# 1. Build request
request = {"policy_number": "POL001"}

# 2. API Client processes
response = API_CLIENT.do_request(
    path="/api/v2/policies/retrieve_policy",
    json=request,
    request_timeout=5,
    request_retries=3
)

# 3. Process response
data = API_CLIENT.process_result(response)
# Returns normalized payload from `data` (not the full envelope)

```

`do_request(...)` defaults:

- timeout: `web_timeout` (default 5s)
- retries: `web_retry` (default 3 with urllib3 backoff)
- authentication: API key injected into request payload for API-key mode,
  bearer token header for OAuth mode

### HTTP Transport Choice

This SDK intentionally uses `urllib3` as the primary HTTP transport instead of `requests`.

- SDK-level control: direct access to retries, pooling, and timeout behavior.
- Fewer abstraction layers: `requests` is built on top of `urllib3`.
- Operational consistency: easier to keep transport behavior explicit in a reusable library.

`requests` remains a good choice for application scripts and one-off integrations where
concise syntax is the main priority.

---

### 3. Infrastructure Layer

**Purpose:** Configuration, utilities, and external integrations

**Components:**

```text

src/britecore_libraries/
├── config/
│   ├── config.py            # Dynaconf settings loader + LoadClientSettings
│   ├── settings.toml        # Default runtime settings (timeouts/retries/browser)
│   ├── .secrets.toml        # All credentials: base_url, api_key, client_id,
│   │                        # client_secret; optional utility keys:
│   │                        # db_conn_string/db_conn_options,
│   │                        # web_user/web_pass/web_browser
│   │                        # — gitignored, never committed
│   └── __init__.py
├── utils/
│   ├── britecore_odbc.py    # Database connections (optional: pyodbc)
│   ├── britecore_selenium.py # Browser automation (optional: selenium)
│   ├── interactive_menu.py  # CLI menu helpers (optional: questionary)
│   ├── zip_code_lookup.py   # ZIP code CSV lookup
│   └── __init__.py
├── base_logger.py           # Package-level logger setup
└── exceptions.py            # Custom exception hierarchy

```

**Configuration Loading:**

```python

# Dynaconf loads from multiple sources (highest to lowest priority)
# 1. Environment variables (BRITECORE_LIBRARIES_*)
# 2. .secrets.toml (base_url, api_key, client_id, client_secret)
# 3. settings.toml (default runtime keys like web_timeout/web_retry/web_timeout_long/web_browser)
# 4. Built-in defaults

from britecore_libraries.config.config import LoadClientSettings

loader = LoadClientSettings("my_site")
site_config = loader.load_config()

site_config.base_url          # From .secrets.toml or env var
site_config.api_key           # From .secrets.toml or env var
site_config.web_timeout       # From settings.toml
site_config.web_retry         # From settings.toml
site_config.db_conn_string    # Optional ODBC connection string (site-scoped)
site_config.db_conn_options   # Optional ODBC connection options (site-scoped)
site_config.web_browser       # Optional Selenium default browser (site-scoped)

```

Utility-specific validation boundaries:

- API client initialization validates auth/base_url keys for API usage.
- ODBC utility validates `db_conn_string` and `db_conn_options` only when
  `get_cursor(..., target_site="...")` performs config-backed DB resolution.
- Selenium utility validates browser names in `get_driver(...)` (explicit
  argument overrides configured `web_browser`).

---

## Authentication Flow

### API Key Authentication

```text

1. Check environment/config for api_key
2. Set header: "Authorization: ApiKey <api_key>"
3. Send request to endpoint
4. Receive response

```

### OAuth2 Authentication

```text

1. Check for client_id and client_secret
2. Request token from /api/auth/oauth2/token
   {
     "grant_type": "client_credentials",
     "client_id": "...",
     "client_secret": "...",
     "scope": "..."
   }
3. Store token + expiry time
4. On each request:
   - Check if token expired (with safety buffer)
   - If expired, request new token
   - Set header: "Authorization: Bearer <token>"
5. Send request to endpoint

```

**Auto-Selection:**

```python

if client_id and client_secret:
    use_oauth2()
else:
    use_api_key()

```

---

## Lazy Initialization Pattern

**Problem:** Import-time failures if config missing

**Solution:** Lazy proxy pattern

```python

# Old approach (BROKEN)
api_client = init_api_client()  # Fails if no config

# New approach (FIXED)
class _LazyAPIClient:
    def __getattr__(self, name):
        return getattr(get_api_client(), name)

api_client = _LazyAPIClient()
# Now safe to import without config
# Initializes on first method call

```

---

## Async & Caching

`AsyncBritecoreAPIClient` wraps the sync client with:

- **TTL cache:** Thread-safe in-memory cache keyed by canonicalized request
  (auth headers excluded from key)
- **Namespace invalidation:** Mutation wrappers invalidate related read caches
  (e.g., `update_contact` invalidates the `contacts` namespace)
- **In-flight deduplication:** Concurrent identical requests share a single
  in-flight `asyncio.Task` rather than issuing duplicate HTTP calls
- **Per-call overrides:** `cache_enabled`, `cache_ttl_seconds`, `cache_bypass`,
  `cache_invalidate_on_success`, `dedupe_in_flight` via `RequestParameters`

See [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md) for full behavior documentation.

---

## Error Handling

### Exception Hierarchy

```text

BritecoreError (namespace class)
└── Base(Exception)
    ├── NoDataReturned          # API returned success=false or no data
    │   ├── ValidationError     # HTTP 400 / 422 validation failure
    │   ├── NotFoundError       # HTTP 404 resource not found
    │   └── ConflictError       # HTTP 409 conflict
    ├── NoTokenReturned         # OAuth token request failed
    ├── AuthenticationError     # HTTP 401 / 403 auth failure
    ├── RateLimitError          # HTTP 429 rate limit exceeded
    ├── ServerError             # HTTP 5xx server error
    ├── RequestTimeoutError     # Request exceeded configured timeout
    ├── ConfigurationError      # Missing base_url, api_key, etc.
    ├── InvalidPhoneNumber      # Phone validation failed
    ├── InvalidEmailAddress     # Email validation failed
    ├── InvalidAddress          # Address validation failed
    ├── BritecoreKeyError       # Required config key missing
    ├── NoSiteError             # target_site not configured
    ├── MissingParameter        # Required API parameter missing
    ├── ConflictingParameters   # Mutually exclusive params supplied
    └── DatabaseConnectionError # pyodbc connection failure

```

### Error Response Handling

```python

# API returns:
{
    "success": false,
    "message": "Policy not found",
    "data": {}
}

# process_result() raises:
BritecoreError.NoDataReturned("Policy not found")

# Caller handles specific types:
try:
    policy = policies.retrieve_policy(policy_number="POL001")
except BritecoreError.NotFoundError:
    logger.warning("Policy not found")
except BritecoreError.AuthenticationError:
    logger.error("Auth failed — check credentials")
except BritecoreError.Base as e:
    logger.error("SDK failure: %s", e)

```

---

## Data Validation Pipeline

```text

Raw Input
    │
    ├─► NameValidator.normalize_business_name()
    │   └─► "llc" → "LLC"
    │
    ├─► PhoneValidator([...]).process()
    │   └─► "(555) 123-4567" → "5551234567"
    │
    ├─► EmailValidator([...]).process()
    │   └─► "JOHN@EXAMPLE.COM" → "john@example.com"
    │
    ├─► AddressValidator({...}).process()
    │   └─► Validate state, ZIP, normalize components
    │
    └─► Output (Ready for API)
        {
            "name": "Company LLC",
            "phones": [{...}],
            "emails": [{...}],
            "addresses": [{...}]
        }

```

---

## API Endpoint Pattern

### Standard v2 Endpoint Example

```python

# In api/api_calls/v2/policies.py

def retrieve_policy(
    policy_number: str | None = None,
    policy_id: str | None = None,
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> dict:
    """
    Retrieve a policy by number, ID, or revision ID.

    Parameters:
        policy_number: Policy number (e.g., "POL001")
        policy_id: Policy UUID
        revision_id: Revision UUID
        **kwargs: Timeout, retry, header overrides (RequestParameters)

    Returns:
        Normalized process_result() payload for the matching policy.
    """

    # 1. Resolve which identifier to use (mutually exclusive)
    params = [
        {"policy_id": policy_id},
        {"revision_id": revision_id},
        {"policy_number": policy_number},
    ]
    payload = API_CLIENT.multiple_parameter_verification(
        params,
        priority=["revision_id", "policy_id", "policy_number"]
    )

    # 2. Make request
    response = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy",
        json=payload,
        **kwargs
    )

    # 3. Process and return
    return API_CLIENT.process_result(response)

```

---

## Test Architecture

```text

tests/
├── conftest.py                         # Shared fixtures (env_api_key, mock_settings, etc.)
├── unit/
│   ├── test_api_client.py              # BritecoreAPIClient unit tests
│   ├── test_api_spec_alignment.py      # Verify wrappers align with api_specs/current/britecore.json
│   ├── test_async_api_client.py        # AsyncBritecoreAPIClient unit tests
│   ├── test_async_v2_api_calls.py      # Async endpoint wrapper tests
│   ├── test_concurrency.py             # Multi-instance + thread-safety tests
│   ├── test_config.py                  # Config loading tests
│   ├── test_core_client_coverage.py    # do_request / process_result coverage
│   ├── test_exceptions.py              # Exception hierarchy tests
│   ├── test_logging_tokens.py          # Verify no SCLogging tokens remain
│   ├── test_maps.py                    # Regex map behavior
│   ├── test_models.py                  # Domain model tests
│   ├── test_oauth_token_manager.py     # OAuth token lifecycle tests
│   ├── test_v1_endpoint_routing.py     # endpoint routing + docstring tests
│   ├── test_v2_endpoints.py            # v2 endpoint wrapper tests
│   ├── test_v2_new_endpoints.py        # v2 newer endpoint tests
│   ├── test_validators.py              # Validator tests
│   └── test_zip_code_lookup.py         # ZIP code lookup tests
└── integration/
    └── test_endpoints.py               # Full endpoint integration + sandbox tests

```

**Fixture Pattern:**

```python

# conftest.py
@pytest.fixture
def mock_settings():
    """Provide a mock settings namespace for client initialization."""
    return SimpleNamespace(
        base_url="https://test.example.com",
        api_key="test_api_key",
        client_id="",
        client_secret="",
        web_timeout=5,
        web_retry=3,
        web_timeout_long=30,
    )

# test_v2_endpoints.py
def test_retrieve_policy(env_api_key, mock_settings):
    client = _get_initialized_client(mock_settings)
    with patch.object(client, "do_request", return_value=mock_response):
        with patch.object(client, "process_result", return_value={"policy_id": "123"}):
            result = policies.retrieve_policy(policy_number="POL001")
    assert result["policy_id"] == "123"

```

---

## Dependency Management

### Internal Dependencies

```text

api/api_calls/          # Uses
    ├─→ britecore_api_client.py
    ├─→ britecore_async_api_client.py  (async modules)
    ├─→ request_cache.py               (async modules)
    ├─→ config/settings
    └─→ exceptions.py

models/                 # Uses
    ├─→ validators/
    └─→ logger

validators/             # Uses
    ├─→ maps/ (lazy-loaded regexes)
    ├─→ exceptions.py
    └─→ logger

```

### External Dependencies

```text

Core (always installed):
  urllib3          # HTTP requests and connection pooling
  dynaconf         # Configuration management

Optional extras:
  pyodbc           # Database access ([database])
  selenium         # Browser automation ([browser])
  questionary      # Interactive CLI menus ([interactive])

```

---

## Performance Considerations

### API Client Optimizations

1. **Connection Pooling:** urllib3 PoolManager with configurable pool size
2. **Timeouts:** Configurable per-request (default 5s, long 30s)
3. **Retries:** Exponential backoff for transient failures (502, 503, 504)
4. **Token Caching:** OAuth tokens cached until expiration (with safety buffer)

### Async Client Optimizations

1. **TTL Cache:** In-memory response cache per request key, default TTL 60s
2. **In-flight Deduplication:** Concurrent identical requests share one `asyncio.Task`
3. **Namespace Invalidation:** Targeted cache invalidation on mutation success

### Validation Caching

- Regex patterns compiled once at module load
- Reused for all subsequent validations

---

## Deployment Considerations

### Configuration in Production

```bash

# Never commit secrets — .secrets.toml is gitignored
# settings.toml contains only urllib3 defaults (no credentials)

# Use environment variables for all credentials
export BRITECORE_LIBRARIES_BASE_URL="https://your-instance.com"
export BRITECORE_LIBRARIES_API_KEY="..."
# or OAuth:
export BRITECORE_LIBRARIES_CLIENT_ID="..."
export BRITECORE_LIBRARIES_CLIENT_SECRET="..."
export target_site="production"

```

### Logging

```python

import logging

# Module-level control
logging.getLogger("britecore_libraries").setLevel(logging.DEBUG)

# Standard Python logging — no custom formatting tokens
from britecore_libraries import logger
logger.debug("Detailed info")
logger.info("Important events")
logger.error("Errors with context")

```

### Monitoring

- Track token refresh rate (indicates expiry issues)
- Monitor request latency (timeout tuning)
- Alert on `BritecoreError.RateLimitError` (backoff needed)
- Alert on `BritecoreError.ServerError` (upstream BriteCore health)

---

## Future Enhancements

1. **Metrics / Tracing** - Built-in instrumentation hooks (request ID, latency, retry count)
2. **Retry Strategies** - Per-error-type retry configuration
3. **SDK Code Generation** - Regenerate endpoint wrappers from `api_specs/current/britecore.json`

---

## Documentation Freshness

- Last verified: `2026-04-07`
- Verified against: `src/britecore_libraries/` directory structure and `exceptions.py`

---

See [AGENTS.md](AGENTS.md) for developer patterns and best practices.
