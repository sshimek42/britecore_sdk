# System Architecture

*Last updated: April 7, 2026*
*Document type: Living design reference*

**BriteCore Libraries** - Technical design and component overview

---

## High-Level Architecture

```text

┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  (Your code using BriteCore Libraries)                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Domain Layer                            │
│  • Models (Contact, Policy, Quote)                      │
│  • Validators (Email, Phone, Address, Name)            │
│  • Mappers (Regex patterns, Field mappings)            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   API Layer                              │
│  • API Endpoints (v1, v2)                              │
│  • API Client (Request/Response handling)              │
│  • Authentication (API Key, OAuth2)                    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Infrastructure Layer                      │
│  • Configuration (Dynaconf)                            │
│  • Utilities (ODBC, Selenium, Logging)                 │
│  • External Services (OAuth, HTTP)                     │
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
│   ├── email_validator.py      # Email validation
│   ├── phone_validator.py      # Phone validation
│   ├── address_validator.py    # Address validation
│   ├── name_validator.py       # Name normalization
│   └── __init__.py             # Exports
├── maps/
│   ├── britecore_policy_name_map.py    # Regex patterns
│   ├── britecore_field_map.py          # Field mappings
│   └── __init__.py                     # Exports
└── constants.py         # Shared constants

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

---

### 2. API Layer

**Purpose:** Unified interface to BriteCore REST API

**Components:**

```text

src/britecore_libraries/api/
├── britecore_api_client.py              # Main API client
├── britecore_oauth_token_manager.py     # OAuth2 token handling
├── api_calls/
│   ├── __init__.py                      # Lazy init + exports
│   ├── v1/                              # Legacy endpoints
│   │   ├── contacts.py
│   │   ├── printing.py
│   │   └── __init__.py
│   └── v2/                              # Current endpoints
│       ├── policies.py                  # Policy-related endpoints
│       ├── contacts.py                  # Contact endpoints
│       ├── quotes.py                    # Quote endpoints
│       ├── deliverables.py              # Deliverable endpoints
│       ├── utils.py                     # Utility/admin endpoints
│       ├── claims.py, insured.py, lines.py, etc.
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
- retries: `web_retry` (default 5 with urllib3 backoff)
- authentication: API key injected into request payload for API-key mode,
  bearer token header for OAuth mode

### HTTP Transport Choice

This SDK intentionally uses `urllib3` as the primary HTTP transport instead of `requests`.

- SDK-level control: direct access to retries, pooling, and timeout behavior.
- Fewer abstraction layers: `requests` is built on top of `urllib3`.
- Operational consistency: easier to keep transport behavior explicit in a reusable library.

`requests` remains a good choice for application scripts and one-off integrations where concise syntax is the main priority.

---

### 3. Infrastructure Layer

**Purpose:** Configuration, utilities, and external integrations

**Components:**

```text

src/britecore_libraries/
├── config/
│   ├── config.py            # Dynaconf settings loader
│   ├── settings.toml        # Default configuration
│   ├── .secrets.toml        # Environment secrets (git-ignored)
│   └── __init__.py
├── utils/
│   ├── britecore_odbc.py    # Database connections (pyodbc)
│   ├── britecore_selenium.py # Browser automation (Selenium)
│   ├── zip_code_lookup.py   # ZIP code CSV lookup
│   └── __init__.py
├── base_logger.py           # Singleton logger
└── exceptions.py            # Custom exceptions

```

**Configuration Loading:**

```python

# Dynaconf loads from multiple sources
from britecore_libraries.config import settings

# 1. Load settings.toml (defaults)
# 2. Load .secrets.toml (secrets)
# 3. Override with environment variables
# 4. Validate required keys

# Access configuration
settings.base_url           # From environment or config file
settings.web_timeout        # From config
settings.web_retry          # From config

```

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
   - Check if token expired
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

## Error Handling

### Exception Hierarchy

```text

Exception
├── BritecoreError (our custom exceptions)
│   ├── NoDataReturned       # API returned success=false
│   ├── NoTokenReturned      # OAuth token request failed
│   ├── InvalidPhoneNumber   # Phone validation failed
│   ├── InvalidEmailAddress  # Email validation failed
│   ├── InvalidAddress       # Address validation failed
│   ├── NoSiteError          # target_site not configured
│   ├── MissingParameter     # Required param missing
│   └── ConflictingParameters # Multiple exclusive params
└── ... (urllib3, pyodbc, etc.)

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

# Caller handles:
try:
    policy = get_policy("POL001")
except BritecoreError.NoDataReturned as e:
    logger.error(f"Failed: {e}")

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
    │   └─► Validate state, ZIP, etc.
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

### Implemented Endpoint Example

```python

# In api/api_calls/v2/policies.py

def retrieve_policy(
    policy_number: Optional[str] = None,
    policy_id: Optional[str] = None,
    revision_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> dict:
    """
    Retrieve a policy by number, ID, or revision ID.
    
    Parameters:
        policy_number: Policy number (e.g., "POL001")
        policy_id: Policy UUID
        revision_id: Revision UUID
        **kwargs: Timeout, retry settings
    
    Returns:
        Dictionary with policy data
    """
    
    # 1. Resolve which parameter to use
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
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_config.py       # Config loading
│   ├── test_api_client.py   # API client
│   ├── test_oauth_token_manager.py
│   ├── test_maps.py         # Regex fallback
│   ├── test_validators.py   # Data validation
│   ├── test_models.py       # Domain models
│   └── test_exceptions.py   # Error handling
└── integration/             # Integration tests
    └── test_endpoints.py    # Endpoint wrappers

```

**Fixture Pattern:**

```python

# conftest.py
@pytest.fixture
def mock_http_response():
    """Mock successful HTTP response."""
    response = MagicMock()
    response.status = 200
    response.data = b'{"success": true, "data": {...}}'
    return response

# test_api_client.py
def test_process_result(mock_http_response):
    result = API_CLIENT.process_result(mock_http_response)
    assert result is not None

```

---

## Dependency Management

### Internal Dependencies

```text

api/api_calls/          # Uses
    ├─→ britecore_api_client.py
    ├─→ config/settings
    └─→ exceptions.py

models/                 # Uses
    ├─→ validators/
    └─→ logger

validators/             # Uses
    ├─→ maps/regex_patterns
    ├─→ exceptions.py
    └─→ logger

```

### External Dependencies

```text

urllib3          # HTTP requests
pyodbc          # Database access
selenium        # Browser automation
dynaconf        # Configuration
csv (stdlib)    # ZIP code CSV parsing
sclogging       # Logging

```

---

## Performance Considerations

### API Client Optimizations

1. **Connection Pooling:** urllib3 PoolManager with configurable pool size
2. **Timeouts:** Configurable per-request (default 5s, long 50s)
3. **Retries:** Exponential backoff for transient failures (502, 503, 504)
4. **Token Caching:** OAuth tokens cached until expiration

### Lazy Initialization

- No import-time work
- Client initializes only on first use
- Thread-safe with double-check locking

### Validation Caching

- Regex patterns compiled once at module load
- Reused for all subsequent validations

---

## Deployment Considerations

### Configuration in Production

```bash

# Never commit secrets
.gitignore:
    src/britecore_libraries/config/.secrets.toml

# Use environment variables
export target_site=your_site
export BRITECORE_BASE_URL=...
export BRITECORE_API_KEY=...

```

### Logging

```python

from britecore_libraries import logger

logger.debug("Detailed info")
logger.info("Important events")
logger.error("Errors with context")

```

### Monitoring

- Track token refresh rate (indicates expiry issues)
- Monitor request latency (timeout tuning)
- Alert on validation failures (data quality)

---

## Future Enhancements

1. **Complete API Coverage** - Continue implementing uncovered endpoint groups from `britecore_api.json`
2. **Async Support** - Add async/await patterns
3. **Caching Layer** - Cache policy/quote lookups
4. **Metrics** - Built-in instrumentation
5. **API Documentation** - Generate from docstrings

---

## Documentation Freshness

- Last verified: `2026-03-26`
- Verified against: `src/britecore_libraries/api/api_calls/` and `API.md`

---

See [AGENTS.md](AGENTS.md) for developer patterns and best practices.
