# BriteCore SDK Improvement Roadmap

*Created: July 20, 2026*
*Status: Strategic Planning Document*
*Audience: Development team and maintainers*

## Executive Summary

The BriteCore SDK is mature and production-ready with comprehensive docstrings (560+ functions), robust error handling, and full API coverage. This document outlines strategic improvements to enhance developer experience, observability, and maintainability.

---

## Priority 1: Quick Wins (1-2 hours each)

### 1.1 Type Hint Resolution ⭐

**Current State:** 9 `type: ignore` comments scattered across the codebase
**Impact:** Improve type safety and IDE auto-completion
**Effort:** Medium (2-3 hours)

**Files to Review:**
- `src/britecore_sdk/classes/__init__.py:53` - Module replacement type issue
- `src/britecore_sdk/api/api_calls/__init__.py:142,212` - Client arg-type suppressions
- `src/britecore_sdk/api/workflows/async_batch_*.py` - asyncio.gather return type
- `src/britecore_sdk/settings/defaults.py:52` - Dictionary default resolution

**Recommended Actions:**
1. Use `@overload` decorators where needed
2. Create stricter TypedDict definitions for kwargs
3. Use `TypeVar` for generic return types in async utilities
4. Consider updating mypy configuration to be stricter

**Expected Outcome:** 100% type-safe codebase, better IDE support

---

### 1.2 Enhanced Error Messages with Hints ⭐

**Current State:** Good error structure, but limited contextual hints
**Impact:** Faster troubleshooting for SDK users
**Effort:** 2-3 hours

**Improvements:**

```python
# Before:
raise ConfigurationError("base_url is required")

# After:
raise ConfigurationError(
    "base_url is required for site 'production'",
    hint="Set via: ~/.britecore/.secrets.toml[production] or BRITECORE_SDK_BASE_URL env var"
)
```

**Files to Update:**
- `src/britecore_sdk/exceptions.py` - Add `hint` field to all Base exceptions
- `src/britecore_sdk/api/britecore_api_client.py` - Enhance error messages in init flows
- `src/britecore_sdk/settings/config.py` - Add config resolution hints

**Expected Outcome:** Self-service troubleshooting for common issues

---

### 1.3 Structured Logging Levels ⭐

**Current State:** Basic logging with info/debug/error
**Impact:** Better observability in production
**Effort:** 1-2 hours

**Add Logging Categories:**
```python
# In britecore_sdk/base_logger.py
class LogCategory:
    AUTH = "auth"           # OAuth token, credential validation
    HTTP = "http"           # Raw request/response (redacted)
    RATE_LIMIT = "rate_limit"  # Rate limit state changes
    CACHE = "cache"         # Cache hits/misses
    PERF = "perf"          # Timing measurements
    CONFIG = "config"       # Configuration resolution
```

**Example:**
```python
LOGGER.info("Token refresh successful", extra={"category": LogCategory.AUTH})
LOGGER.debug(f"Request {req_id} took {elapsed_ms}ms", extra={"category": LogCategory.PERF})
```

**Expected Outcome:** Easier filtering and monitoring in production environments

---

## Priority 2: Developer Experience (2-4 hours each)

### 2.1 CLI Tool: `britecore-quick-check` ⭐⭐

**Current State:** `britecore-check-config` and `britecore-healthcheck` exist; missing quick verification
**Impact:** One-command environment verification
**Effort:** 2-3 hours

**Features:**
```bash
# Quick syntax check (no API call)
$ britecore-quick-check --syntax
✓ Configuration syntax valid
✓ No credentials in .toml files
✓ Settings files accessible

# Minimal connectivity test
$ britecore-quick-check --connectivity
✓ base_url reachable
✓ SSL certificate valid
✓ API endpoint responds

# Full health check
$ britecore-quick-check --full
✓ Config valid
✓ Credentials work
✓ API responds
✓ Database accessible
Status: Ready for production use
```

**Implementation:**
1. Create `src/britecore_sdk/cli/quick_check.py`
2. Register entry point in `pyproject.toml`
3. Add unit tests in `tests/unit/test_cli_quick_check.py`

---

### 2.2 API Response Helpers and Utilities ⭐⭐

**Current State:** `process_result()` handles response normalization
**Impact:** Cleaner user code
**Effort:** 2-3 hours

**Add Helper Module:** `src/britecore_sdk/api/response_helpers.py`

```python
# New utilities
def extract_data(response: Any) -> Any:
    """Get 'data' field, raise if missing."""
    if isinstance(response, dict) and "data" in response:
        return response["data"]
    raise BritecoreError.NoDataReturned(...)

def get_paginated(client, endpoint, params, page_size=50):
    """Helper for paginated API responses."""
    # Iterate through pages automatically
    for page in iterate_pages(endpoint, params, page_size):
        yield from page["data"]

def batch_operations(operations: list, client, timeout=300):
    """Run multiple operations with progress tracking."""
    # Progress bar, error aggregation, etc.
```

**Expected Outcome:** Reduced boilerplate in user code

---

### 2.3 Interactive Configuration Wizard ⭐

**Current State:** Documentation-driven config
**Impact:** Faster onboarding
**Effort:** 2-3 hours

**Implementation:**
```bash
$ britecore-config-wizard
? Target environment: [sandbox/production] > production
? Auth method: [API Key / OAuth] > API Key
? Base URL: > https://britecore.example.com
? API Key: > [hidden input]
? Save to: [~/.britecore/secrets.toml / ./britecore.toml] >
✓ Configuration saved and validated
```

**Files:**
- `src/britecore_sdk/cli/config_wizard.py` (uses `questionary`)
- Update `pyproject.toml` with entry point

---

## Priority 3: Testing & Quality (3-5 hours each)

### 3.1 Comprehensive Test Fixtures Library ⭐⭐

**Current State:** Basic test structure
**Impact:** Faster test development, consistent mocking
**Effort:** 3-4 hours

**Create:** `tests/fixtures/api_fixtures.py`

```python
@pytest.fixture
def mock_policy_response():
    """Standard policy response for testing."""
    return {
        "success": True,
        "data": {
            "policy_number": "POL-123",
            "status": "active",
            # ... full policy structure
        }
    }

@pytest.fixture
def api_client_mock(monkeypatch):
    """Pre-configured mock API client."""
    # Automatically mock common endpoints

@pytest.fixture
def rate_limit_scenario():
    """Simulate rate limit conditions."""
    # Return mock that triggers rate limit errors
```

**Expected Outcome:** Faster test writing, fewer duplicated mocks

---

### 3.2 Integration Test Template Suite ⭐⭐

**Current State:** Primarily unit tests
**Impact:** Catch integration issues early
**Effort:** 3-4 hours

**Create:** `tests/integration/test_workflows_*.py`

```python
# Test realistic workflows:
# - Create policy → Add coverage → Submit
# - New contact → Add to policy → Activate
# - Batch operations with rate limiting
```

**Setup:**
- Pytest markers: `@pytest.mark.integration`
- Docker compose for local testing if needed
- Documented in `TESTING.md`

---

### 3.3 Property-Based Testing with Hypothesis ⭐

**Current State:** Manual test cases
**Impact:** Catch edge cases in validation
**Effort:** 2-3 hours

**Example:**
```python
from hypothesis import given, strategies as st

@given(
    email=st.emails(),
    phone=st.text().filter(lambda x: x.isdigit())
)
def test_contact_validators_accept_valid_inputs(email, phone):
    contact = BritecoreContact(email=[{"email": email}], ...)
    assert contact.process_contact()["email"][0]["email"] == email.lower()
```

**Files:**
- `tests/unit/test_validators_hypothesis.py`
- `tests/unit/test_models_hypothesis.py`

---

## Priority 4: Performance & Monitoring (2-4 hours each)

### 4.1 Request Timing Middleware ⭐⭐

**Current State:** No built-in performance tracking
**Impact:** Identify slow endpoints
**Effort:** 2-3 hours

**Add to:** `src/britecore_sdk/api/middleware.py`

```python
class TimingMiddleware:
    """Track and log request timing."""

    def on_request_start(self, req_id, path, method):
        self._timings[req_id] = time.time()

    def on_request_end(self, req_id, status_code):
        elapsed = time.time() - self._timings.pop(req_id)
        LOGGER.info(
            f"[{req_id}] {method} {path}: {elapsed*1000:.1f}ms",
            extra={"category": "perf", "elapsed_ms": elapsed*1000}
        )
        self.slowlog(req_id, elapsed)  # Alert if > threshold
```

**Expected Outcome:** Visibility into API performance bottlenecks

---

### 4.2 Response Caching Strategy Documentation ⭐

**Current State:** `request_cache.py` exists but limited
**Impact:** Understand caching tradeoffs
**Effort:** 1-2 hours

**Create:** `docs/CACHING_STRATEGY.md`

```markdown
# Response Caching Strategy

## When to enable caching:
- Readonly operations (retrieve_policy, list_contacts)
- Stable reference data (policy types, rating factors)
- Batch operations with repeated lookups

## When to disable:
- Mutable operations (create, update, delete)
- Time-sensitive data (quote availability)
- Real-time integrations

## Configuration:
```python
# Per-request
result = retrieve_policy(..., cache_ttl=3600)

# Global
from britecore_sdk.api import request_cache
request_cache.enable_caching(ttl=3600, max_size=1000)
```
```

## Priority 5: Documentation & Examples (1-3 hours each)

## Priority 5: Documentation & Examples (1-3 hours each)

### 5.1 API Patterns & Recipes Documentation ⭐⭐

**Current State:** Endpoint docs exist; patterns are scattered
**Impact:** Faster learning curve for common tasks
**Effort:** 2-3 hours

**Create:** `docs/COMMON_PATTERNS.md`

```markdown
# Common BriteCore API Patterns

## Pattern 1: Policy Lookup with Fallback
```python
try:
    policy = policies.retrieve_policy(policy_number=pnumber)
except NotFoundError:
    policy = policies.retrieve_policy(policy_id=pid)
```

## Pattern 2: Batch Contact Import
```python
for contact_data in contacts_to_import:
    contact = BritecoreContact(**contact_data)
    validated = contact.process_contact()
    contacts.new_contact(contact=validated)
```

## Pattern 3: Rate Limit Aware Loops
...
```

---

### 5.2 Migration Guide: SDK v1 → v2 ⭐

**Current State:** Breaking changes documented separately
**Impact:** Smooth upgrades from v1
**Effort:** 2-3 hours

**Create:** `docs/MIGRATION_v1_to_v2.md`

```markdown
# Migrating from BriteCore SDK v1 to v2

## Key Changes
- API client initialization (lazy vs eager)
- Exception types (flat imports now preferred)
- Async patterns (new AsyncBritecoreAPIClient)

## Before (v1):
```python
from britecore_sdk.api.api_calls.v1 import policies
result = policies.retrieve_policy(...)
```

## After (v2):
```python
from britecore_sdk.api.api_calls.v2 import policies
client = get_api_client()
result = policies.retrieve_policy(...)
```

## Step-by-Step Migration
...
```

---

### 5.3 Troubleshooting Guide ⭐

**Current State:** Documentation scattered
**Impact:** Self-service problem resolution
**Effort:** 2-3 hours

**Expand:** `TROUBLESHOOTING.md` with sections:

```markdown
# Troubleshooting Guide

## "base_url is required"
...solution...

## "Authentication failed" (401/403)
...solution...

## "Rate limit exceeded" (429)
...solution with backoff example...

## "Connection refused" / timeouts
...solution...

## Performance issues
...debugging steps...
```

---

## Priority 6: Advanced Features (4+ hours each)

### 6.1 Bulk Operation Retry with Exponential Backoff ⭐⭐

**Current State:** Basic retry in urllib3
**Impact:** Reliable bulk operations
**Effort:** 3-4 hours

**Enhancement:**
```python
# New context manager
with BulkOperationManager(
    max_retries=3,
    backoff_factor=2,
    retry_on=[429, 503],
    on_retry=lambda e: print(f"Retry: {e}")
) as bulk:
    for policy in policies_to_create:
        bulk.add_operation(policies.create_policy, policy_data=policy)
    results = bulk.execute()
```

---

### 6.2 Webhook Event Handler Framework ⭐⭐

**Current State:** No built-in webhook support
**Impact:** Real-time event processing
**Effort:** 4-5 hours

**New Module:** `src/britecore_sdk/webhooks/`

```python
from britecore_sdk.webhooks import WebhookListener

listener = WebhookListener(port=8000, secret="your-secret")

@listener.on("policy.updated")
def handle_policy_update(event):
    print(f"Policy {event.policy_id} was updated")

@listener.on("quote.created")
def handle_quote_creation(event):
    print(f"New quote: {event.quote_id}")

listener.start()
```

---

### 6.3 OpenAPI/Swagger UI Integration ⭐

**Current State:** No interactive API documentation
**Impact:** Interactive API exploration
**Effort:** 3-4 hours

**Features:**
- Auto-generate OpenAPI spec from docstrings and type hints
- Optional Swagger UI endpoint for testing
- Downloadable OpenAPI JSON

---

## Priority 7: Infrastructure & DevOps (2-3 hours each)

### 7.1 Pre-commit Hooks for SDK Development ⭐

**Current State:** General hooks exist
**Impact:** Prevent common mistakes
**Effort:** 1-2 hours

**Add Hooks:**
```yaml
- repo: local
  hooks:
    - id: docstring-check
      name: Docstring completeness
      entry: python scripts/check_docstrings.py
      language: python
      types: [python]
    - id: type-stub-check
      name: Check for unresolved type: ignore
      entry: python scripts/check_type_ignores.py
      language: python
      types: [python]
    - id: credential-check
      name: Check for hardcoded credentials
      entry: python scripts/check_credentials.py
      language: python
      types: [python]
```

---

### 7.2 CI Coverage Enforcement ⭐

**Current State:** Coverage tracked, not enforced
**Impact:** Maintain code quality
**Effort:** 1-2 hours

**Add to CI:**
```yaml
- name: Enforce coverage threshold
  run: |
    pytest --cov=britecore_sdk --cov-report=term --cov-fail-under=75
    # Fail if coverage drops below 75%
```

**Create:** `scripts/check_coverage_threshold.py`

---

## Implementation Priority Matrix

| Feature | Effort | Impact | Priority |
|---------|--------|--------|----------|
| Type Hint Resolution | 2-3h | High | P1 |
| Enhanced Error Messages | 2-3h | High | P1 |
| Structured Logging | 1-2h | Medium | P1 |
| CLI Quick Check | 2-3h | High | P2 |
| Response Helpers | 2-3h | Medium | P2 |
| Config Wizard | 2-3h | High | P2 |
| Test Fixtures | 3-4h | High | P3 |
| Integration Tests | 3-4h | Medium | P3 |
| Request Timing | 2-3h | Medium | P4 |
| Common Patterns Doc | 2-3h | High | P5 |
| Migration Guide | 2-3h | High | P5 |
| Bulk Retry Manager | 3-4h | Medium | P6 |
| Webhook Framework | 4-5h | Low | P6 |
| OpenAPI Integration | 3-4h | Medium | P6 |

---

## Quick Start for Developers

### Week 1 Focus (High-ROI tasks)
1. Resolve type hints (P1.1)
2. Enhance error messages (P1.2)
3. Add CLI quick-check (P2.1)
4. Document common patterns (P5.1)

### Week 2 Focus
5. Create test fixtures library (P3.1)
6. Add timing middleware (P4.1)
7. Write migration guide (P5.2)
8. Expand troubleshooting guide (P5.3)

### Week 3+ (As time permits)
- Advanced features
- Webhook framework
- OpenAPI integration
- Property-based testing

---

## Success Metrics

After implementing these improvements, track:

- **Developer Experience:**
  - Time to first successful API call (target: < 5 min)
  - Configuration validation time (target: < 30 sec)

- **Code Quality:**
  - Type-check success rate (target: 100%)
  - Test coverage (target: > 80%)

- **Production Readiness:**
  - Mean time to debug issue (target: < 10 min)
  - Configuration errors caught pre-deployment (target: 95%+)

---

## Next Steps

1. **Choose a Priority 1 item** to start (Type hints or Error Messages)
2. **Create a tracked issue** for each improvement
3. **Assign estimates** and owner
4. **Review and refine** this roadmap with the team
5. **Update README** once improvements ship

---

## Questions?

For feature requests or discussions, refer to:
- **Architecture questions:** `ARCHITECTURE.md`
- **Contributing setup:** `CONTRIBUTING.md`
- **API patterns:** `API.md`
- **Configuration help:** `README.md` (Configuration section)
