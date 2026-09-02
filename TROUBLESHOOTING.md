# Troubleshooting Guide

*Last updated: September 2, 2026*
*Document type: Living troubleshooting guide*

For SDK users: diagnose and resolve common issues, understand error messages, and find workarounds.

## Quick Reference: Common Errors

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| `ModuleNotFoundError: No module named 'britecore_sdk'` | SDK not installed | `pip install -e .` |
| `No target_site assigned` | Configuration missing | Set `target_site` in `~/.britecore/settings.toml` |
| `AuthenticationError: Invalid API key` | Wrong/expired credentials | Verify API key in `~/.britecore/.secrets.toml` |
| `NotFoundError: Policy not found` | Policy doesn't exist | Check policy number is correct |
| `RateLimitError: Too many requests (429)` | Rate limit exceeded | Implement backoff, see Pattern 3 in docs/COMMON_PATTERNS.md |
| `ConnectionError: Connection refused` | API unreachable | Check `base_url` and network connectivity |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Certificate issue | Update CA bundle or use self-signed for dev |
| `Sphinx build failed` (warnings as errors) | Documentation syntax error | See [`docs/DOCUMENTATION_BUILD_TROUBLESHOOTING.md`](docs/DOCUMENTATION_BUILD_TROUBLESHOOTING.md) |

> **📚 Developers:** For documentation build errors, see [`docs/DOCUMENTATION_BUILD_TROUBLESHOOTING.md`](docs/DOCUMENTATION_BUILD_TROUBLESHOOTING.md)

## Diagnosis Quick Checks

```bash
# 1. Check SDK installed correctly
python -c "import britecore_sdk; print(britecore_sdk.__version__)"

# 2. Verify configuration
britecore-check-config

# 3. Test connectivity
britecore-healthcheck

# 4. Check environment variables
echo $target_site
echo $BRITECORE_SDK_API_KEY
```

---

## Installation Issues

### "ModuleNotFoundError: No module named 'britecore_sdk'"

**Cause:** Package not installed in current environment

**Solution:**

```sh
# Install in editable mode
pip install -e .

# Or with dev tools
pip install -e ".[dev]"

# Verify installation
python -c "import britecore_sdk; print(britecore_sdk.__version__)"
```

---

### "pip install" hangs or is very slow

**Cause:** Network issues or large dependency tree

**Solution:**

```sh
# Try with timeout
pip install -e . --default-timeout=100

# Or use uv (faster)
pip install uv
uv pip install -e .

# Check Python version

python --version  # Should be 3.11+
```

---

### "Permission denied" during install

**Cause:** Insufficient permissions

**Solution:**

```sh
# Use --user flag
pip install --user -e .
```

Or use a virtual environment:

**Linux/macOS (bash):**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

---

## Configuration Issues

### "No target_site assigned"

**Cause:** `target_site` has not been provided through any of the supported mechanisms.

**Solution (choose one):**

**Option 1 — `settings.toml` (recommended for persistent setup):**

Add `target_site` under the `[default]` section of `src/britecore_sdk/settings/settings.toml`:

```toml
[default]
target_site = "your_site"
```

**Option 2 — Environment variable:**

```powershell
# Set environment variable
$env:target_site = "your_site"

# Verify
python -c "import os; print(os.environ.get('target_site'))"
```

```bash
# Set environment variable
export target_site="your_site"

# Verify
python -c "import os; print(os.environ.get('target_site'))"
```

**Option 3 — Explicit argument in code:**

```python
from britecore_sdk.api.api_calls import init_api_client

client = init_api_client(target_site="your_site")
```

---

### "Configuration validation failed"

**Cause:** Missing required settings in config file

**Solution:**

Check `src/britecore_sdk/settings/.secrets.toml`:

```toml
[production]
base_url = "https://..."          # Required
api_key = "..."                   # Required (if no OAuth)
client_id = ""                    # Leave blank for API key
client_secret = ""                # Leave blank for API key

[staging]
base_url = "https://..."          # Required
client_id = "..."                 # Required (if no API key)
client_secret = "..."             # Required (if no API key)
```

**Or use environment variables:**

**Linux/macOS (bash):**

```bash
export BRITECORE_SDK_BASE_URL="https://..."
export BRITECORE_SDK_API_KEY="..."
export BRITECORE_SDK_CLIENT_ID="..."
export BRITECORE_SDK_CLIENT_SECRET="..."
```

**Windows (PowerShell):**

```powershell
$env:BRITECORE_SDK_BASE_URL="https://..."
$env:BRITECORE_SDK_API_KEY="..."
$env:BRITECORE_SDK_CLIENT_ID="..."
$env:BRITECORE_SDK_CLIENT_SECRET="..."
```

Validate site sections and key combinations quickly:

```sh
# Installed CLI — works in bash and PowerShell:
britecore-check-config

# Or via python -m:
python -m britecore_sdk.utils.check_site_configs
```

Check local API spec freshness and upstream version drift:

```sh
python -m britecore_sdk.utils.check_api_spec_sync
```

Interpretation:

- `OK`: site has `base_url` and valid auth (`client_id` + `client_secret`, or `api_key`)
- `INCORRECT`: one or more required keys are missing (listed in `Missing Keys`)
- Warning about `settings.toml`: sensitive keys were found in `settings.toml` and should be moved to `.secrets.toml`

---

### "File not found: .secrets.toml"

**Cause:** No secrets file created

**Solution:**

Create `src/britecore_sdk/settings/.secrets.toml`:

```toml
[production]
base_url = "<SET_VIA_ENV_OR_SECRETS_FILE>"
api_key = "<SET_VIA_ENV_OR_SECRETS_FILE>"
client_id = ""
client_secret = ""

[staging]
base_url = "<SET_VIA_ENV_OR_SECRETS_FILE>"
api_key = "<SET_VIA_ENV_OR_SECRETS_FILE>"
```

Or just use environment variables (they override file settings).

---

## Runtime Issues

### "No Windows console found" from `questionary` in PyCharm

**Cause:** Some IDE run consoles on Windows do not expose a native Win32
console buffer to `prompt_toolkit`/`questionary`.

**Solution:**

`utils.interactive_menu.line_menu()` now falls back automatically to a plain
numbered `input()` menu when rich prompts cannot be initialized.

If you still want the richer interactive prompt UI, run the same script from a
native terminal (PowerShell, Windows Terminal, or `cmd.exe`) instead of the IDE
run console.

---

### "Failed to retrieve OAuth token"

**Cause:** Invalid OAuth credentials or token endpoint unreachable

**Solution:**

```python
# Check credentials in config
from britecore_sdk.settings import settings
print(f"Client ID: {settings.client_id}")
print(f"Base URL: {settings.base_url}")
print(f"Token endpoint: {settings.base_url}/api/auth/oauth2/token")

# Verify network connectivity
import urllib3
http = urllib3.PoolManager()
try:
    response = http.request('GET', settings.base_url)
    print(f"Connected: {response.status}")
except Exception as e:
    print(f"Connection error: {e}")
```

---

### "No data returned" from API

**Cause:** API returned success=false or HTTP error

**Solution:**

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk.exceptions import BritecoreError

client = get_api_client()
try:
    policy = policies.retrieve_policy(policy_number="INVALID")
except BritecoreError.NotFoundError as e:
    print(f"Not found: {e}")
except BritecoreError.ValidationError as e:
    print(f"Validation error: {e}")
except BritecoreError.NoDataReturned as e:
    print(f"API Error: {e}")
    # Check if:
    # 1. Policy number is correct
    # 2. User has permission to access policy
    # 3. API endpoint is working
```

SDK exceptions can be caught via the common base class:

```python
from britecore_sdk.exceptions import BritecoreError

try:
    ...
except BritecoreError.Base as exc:
    print(f"SDK failure: {exc}")
```

Or using the flat aliases (shorter imports):

```python
from britecore_sdk import NotFoundError, AuthenticationError, ConfigurationError
from britecore_sdk.exceptions import RateLimitError  # full set available here

try:
    ...
except NotFoundError as exc:
    print(f"Not found: {exc}")
except AuthenticationError as exc:
    print(f"Auth error: {exc}")
```

---

### "Invalid phone number" validation error

**Cause:** Phone number format not recognized

**Solution:**

```python
from britecore_sdk.validators import PhoneValidator

# Valid formats (will be normalized to 10 digits)
valid_phones = [
    {"phone": "5551234567", "type": "Home"},
    {"phone": "(555) 123-4567", "type": "Work"},
    {"phone": "555-123-4567", "type": "Mobile"},
]

result = PhoneValidator(valid_phones).process()
print(result)  # Normalized to: 5551234567
```

---

### "Invalid email address" validation error

**Cause:** Email format invalid

**Solution:**

```python
from britecore_sdk.validators import EmailValidator

# Must be valid email format
valid_emails = [
    {"email": "user@example.com", "type": "Home"},
    {"email": "john.doe+tag@company.co.uk", "type": "Work"},
]

result = EmailValidator(valid_emails).process()
print(result)  # Returns normalized emails
```

---

## Import Issues

### "Circular import" error

**Cause:** Module imports create cycle

**Solution:**

```python
# Don't do this (circular):
# In models.py: from validators import EmailValidator
# In validators.py: from models import BritecoreContact

# Instead use string forward references:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .validators import EmailValidator
```

---

### "Cannot import name 'X' from 'britecore_sdk'"

**Cause:** Module or function doesn't exist or not exported

**Solution:**

```python
# Check what's available
import britecore_sdk
print(dir(britecore_sdk))

# Check __all__ in module
from britecore_sdk.models import __all__
print(__all__)

# Look at actual exports
from britecore_sdk.models import *
```

---

## Testing Issues

### "ModuleNotFoundError" in tests

**Cause:** Test dependencies not installed

**Solution:**

```sh
pip install -e ".[dev]"
python -m pytest tests/ -v
```

---

### "Tests failing with mocking errors"

**Cause:** Mock setup incorrect

**Solution:**

```python
# Check import path matches actual location
from unittest.mock import patch, MagicMock

# Use correct patch target
with patch("britecore_sdk.api.api_calls.API_CLIENT") as mock:
    # Now use the mock
    mock.do_request.return_value = ...
```

---

### "Coverage report shows 0%"

**Cause:** Coverage tool not configured

**Solution:**

```sh
# Make sure pytest-cov installed
pip install -e ".[dev]"

# Run with coverage
python -m pytest tests/ --cov=src/britecore_sdk --cov-report=html
```

Open the HTML report:

**Linux/macOS (bash):**

```bash
open htmlcov/index.html
```

**Windows (PowerShell):**

```powershell
Invoke-Item htmlcov/index.html
```

---

### "Cannot find conftest.py"

**Cause:** Running pytest from wrong directory

**Solution:**

```sh
# Run from project root
cd britecore_sdk
python -m pytest tests/ -v

# NOT from tests/ directory
```

---

## API Client Issues

### "Timeout error" on slow API

**Cause:** Default timeout too short

**Solution:**

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies
from urllib3 import Timeout

client = get_api_client()
# Use longer timeout
policy = policies.retrieve_policy(
    policy_number="POL001",
    request_timeout=Timeout(total=30)  # 30 seconds
)
```

---

### "Too many retries" errors

**Cause:** Server temporarily unavailable

**Solution:**

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies
from urllib3 import Retry

client = get_api_client()
# Configure retries
policy = policies.retrieve_policy(
    policy_number="POL001",
    request_retries=Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
)
```

---

### "SSL certificate error"

**Cause:** HTTPS certificate validation issue

**Solution:**

```python
# Check certificate validity
import ssl
import socket

hostname = "api.britecore.com"
context = ssl.create_default_context()
try:
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"Certificate valid for: {ssock.getpeercert()}")
except ssl.SSLError as e:
    print(f"SSL Error: {e}")
    # May need to update CA certificates or disable verification
    # (not recommended for production)
```

---

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

# Now all debug messages will print, including [req_id] → METHOD /path traces
# and init-time auth-mode selection (oauth vs api_key).
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

client = get_api_client()
policy = policies.retrieve_policy(policy_number="POL001")
# Check console for debug output including X-SDK-Request-ID correlation IDs
```

---

### Inspect a request without sending it (dry-run)

```python
import logging
logging.basicConfig(level=logging.INFO)

from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Set client-level dry-run once for a scratch script / test flow.
# For OAuth sites, this skips token acquisition unless you pass headers explicitly.
init_api_client(client_dry_run=True)

# Logs full URL, headers, and body; no network call made.
preview = policies.retrieve_policy(policy_number="POL001")
print(preview["auth_skipped"])

# Sensitive request-body fields (for example api_key/token/secret/password-like keys)
# are always redacted in dry-run output.
print(preview["body"])
```

---

### Reset the API client between tests or sites

```python
from britecore_sdk.api.api_calls import init_api_client, reset_api_client

init_api_client("site_a")
# ... use site_a ...

reset_api_client()  # clears both sync and async module-level clients

init_api_client("site_b")
# ... use site_b ...
```

---

## Still Having Issues?

### Check These First

1. **Environment Variables:**
   - bash: `echo $target_site`
   - PowerShell: `echo $env:target_site`
2. **Config File:**
   - bash: `cat src/britecore_sdk/settings/settings.toml`
   - PowerShell: `Get-Content src/britecore_sdk/settings/settings.toml`
3. **Python Version:** `python --version` (should be 3.11+)
4. **Package Installation:** `pip show britecore_sdk`
5. **Test Suite:** `python -m pytest tests/unit/test_maps.py -v`

### Get Help

1. Check [README.md](./README.md) for overview
2. Review [AGENTS.md](./AGENTS.md) for patterns
3. Look at test examples in `tests/`
4. See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
5. Check [CONTRIBUTING.md](CONTRIBUTING.md) for development

---

## Private Maps Behavior

Some features in britecore_sdk rely on map files (such as policy, field, or agency maps) located in `src/britecore_sdk/maps/`. These files provide environment-specific mappings and are selected at runtime based on environment variables.

- **Map file selection:**
  - The environment variable `system` determines which map file is loaded (e.g., `britecore_policy_name_map.py`).
  - If `system` is not set, the SDK may fall back to a default map or raise an error, depending on the utility.
  - If the required map file is missing, a `BritecoreError.KeyError` or similar will be raised.

- **Required environment variables:**
  - `system` (selects the map variant)
  - `target_site` (for config loading, may also affect map selection)

- **Fallback behavior:**
  - If a map file for the specified `system` is not found, the SDK may:
    - Use a default map (if implemented)
    - Raise a configuration or key error
  - Always check logs for details if a map is missing or an env var is unset.

- **Troubleshooting:**
  - Ensure the correct `system` value is set in your environment.
  - Verify that the corresponding map file exists in `src/britecore_sdk/maps/`.
  - If you see errors about missing maps or unset variables, set the required env vars and restart your process.

---

## Rate Limiting Issues

### "RateLimitError: Too many requests" (HTTP 429)

**Cause:** API rate limit exceeded

**Solution:**

```python
import time
from britecore_sdk.exceptions import RateLimitError
from britecore_sdk.api.api_calls.v2 import policies

# Option 1: Automatic retry with exponential backoff
for attempt in range(3):
    try:
        policy = policies.retrieve_policy(policy_number="POL-123")
        break
    except RateLimitError:
        wait_time = 2 ** attempt
        print(f"Rate limited, waiting {wait_time}s...")
        time.sleep(wait_time)

# Option 2: Enable client-side rate limiting
from britecore_sdk.api.api_calls import init_api_client
client = init_api_client(
    "production",
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5,
)

# Option 3: Check rate limit status before making requests
if client.rate_limiter:
    # Don't make request if rate limited
    pass
```

**Prevention:**

- Reduce request frequency
- Use batch operations when possible
- Implement request queuing
- Monitor rate limit headers in responses

---

## Performance Issues

### "Requests are very slow" / "High latency"

**Cause:** Network issues, API performance, or inefficient code

**Solution:**

```python
from britecore_sdk import configure_logging, LogCategory
import logging

# 1. Enable performance logging
configure_logging(level=logging.DEBUG)

# 2. Use async for concurrent operations
import asyncio
from britecore_sdk.api.workflows.async_batch_policies import acreate_policies_batch

result = asyncio.run(acreate_policies_batch(policies, max_concurrent=5))

# 3. Use response caching for repeated lookups
from britecore_sdk.api.api_calls import get_async_api_client
client = get_async_api_client()
# Cache TTL can be set per request via cache_ttl parameter

# 4. Batch operations instead of individual requests
from britecore_sdk.api.response_helpers import batch_items
for batch in batch_items(large_list, batch_size=100):
    process_batch(batch)
```

**Diagnosis:**

**Windows (PowerShell):**

```powershell
# Check network connectivity
ping api.britecore.example.com

# Test DNS resolution
Resolve-DnsName api.britecore.example.com

# Check SSL/TLS handshake time
curl.exe -w "@curl_format.txt" -o NUL -s https://api.britecore.example.com
```

**Linux/macOS (bash):**

```bash
# Check network connectivity
ping api.britecore.example.com

# Test DNS resolution
nslookup api.britecore.example.com

# Check SSL/TLS handshake time
curl -w "@curl_format.txt" -o /dev/null -s https://api.britecore.example.com
```

---

## Type Checking and IDE Issues

### "Type hints not working in IDE"

**Cause:** The IDE may be indexing stale interpreter metadata, or you may be using an older wrapper path that exposes fewer typed helpers for that specific endpoint.

**Solution:**

```python
# Prefer wrappers with the richest typed support for the endpoint you need
from britecore_sdk.api.api_calls.v2 import policies  # Often the richest typed path when available

# Supported v1 wrappers are still valid when the upstream API remains v1-only
# or the SDK has no v2 equivalent for that endpoint yet.

# Ensure pyright/mypy is configured
# In pyproject.toml:
[tool.mypy]
python_version = "3.11"
```

Run type checking:

**Windows (PowerShell):**

```powershell
mypy src/britecore_sdk --strict
```

**Linux/macOS (bash):**

```bash
mypy src/britecore_sdk --strict
```

---

## Async Operation Issues

### "asyncio.gather return type error"

**Cause:** Type checker doesn't understand gather with return_exceptions=True

**Solution:** Already fixed in SDK - use cast:

```python
import asyncio
from typing import cast

results = cast(
    list,
    await asyncio.gather(*tasks, return_exceptions=True)
)
```

### "RuntimeError: no running event loop"

**Cause:** Trying to use async functions outside an event loop

**Solution:**

```python
import asyncio
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

# Option 1: Use asyncio.run()
async def main():
    policy = await aretrieve_policy(policy_number="POL-123")
    return policy

result = asyncio.run(main())

# Option 2: Run in existing event loop context
if asyncio.get_event_loop().is_running():
    # Already in event loop, use await directly
    policy = await aretrieve_policy(policy_number="POL-123")
else:
    # Not in event loop, use asyncio.run()
    result = asyncio.run(main())
```

---

## Validation and Data Issues

### "ValidationError: Invalid email format"

**Cause:** Email validation failed

**Solution:**

```python
from britecore_sdk.validators import EmailValidator

validator = EmailValidator()
try:
    valid_email = validator.validate("user@example.com")
except ValidationError as e:
    print(f"Invalid email: {e}")
    # Fix the email format
```

### "ValidationError: Invalid phone format"

**Cause:** Phone number validation failed

**Solution:**

```python
from britecore_sdk.validators import PhoneValidator

validator = PhoneValidator()
try:
    valid_phone = validator.validate("555-1234")
except ValidationError as e:
    # Try different format: (555) 123-4567, +1-555-123-4567, etc
    pass
```

### "Model initialization fails with missing fields"

**Cause:** Required fields are missing from input data

**Solution:**

```python
from britecore_sdk.models import BritecoreContact

# Check required fields before initialization
required = ["name", "address"]
for field in required:
    if field not in contact_data:
        print(f"Missing required field: {field}")
        contact_data[field] = get_default_for_field(field)

contact = BritecoreContact(**contact_data)
```

---

## Credential and Authentication Issues

### "AuthenticationError: Invalid API key"

**Cause:** API key is incorrect, expired, or missing

**Solution:**

**Windows (PowerShell):**

```powershell
# 1. Verify API key is set
echo $env:BRITECORE_SDK_API_KEY

# 2. Check settings file
Get-Content $env:USERPROFILE\.britecore\.secrets.toml

# 3. Verify key is in correct format
# Keys usually start with specific prefix depending on environment

# 4. Regenerate key if necessary
britecore-config-wizard
```

**Linux/macOS (bash):**

```bash
# 1. Verify API key is set
echo $BRITECORE_SDK_API_KEY

# 2. Check settings file
cat ~/.britecore/.secrets.toml

# 3. Verify key is in correct format
# Keys usually start with specific prefix depending on environment

# 4. Regenerate key if necessary
britecore-config-wizard
```

### "AuthenticationError: OAuth token expired"

**Cause:** OAuth token refresh failed

**Solution:**

```python
from britecore_sdk.api.api_calls import init_api_client

# Reinitialize to refresh token
client = init_api_client("production").init_client()

# Or enable debug logging to see token refresh attempts
from britecore_sdk import configure_logging
configure_logging(level="DEBUG")
```

### "ConfigurationError: base_url is required"

**Cause:** Base URL not configured

**Solution:**

**Windows (PowerShell):**

```powershell
# Quick setup wizard
britecore-config-wizard

# OR manually configure settings.toml
@'
[production]
base_url = "https://api.example.com"
api_key = "your_api_key"
'@ | Set-Content "$env:USERPROFILE\.britecore\settings.toml"
```

**Linux/macOS (bash):**

```bash
# Quick setup wizard
britecore-config-wizard

# OR manually configure settings.toml
cat > ~/.britecore/settings.toml << EOF
[production]
base_url = "https://api.example.com"
api_key = "your_api_key"
EOF
```

---

## Logging and Debugging

### "Debug output not showing"

**Cause:** Logging not configured

**Solution:**

```python
from britecore_sdk import configure_logging

# Enable debug logging with console output
logger = configure_logging(level="DEBUG")

# Or to file
logger = configure_logging(level="DEBUG", log_to_file=True)

# Or filter by category
from britecore_sdk.base_logger import LogCategory
# Logs include 'category' field for filtering
```

### "How to get request/response details"

**Solution:**

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk import configure_logging

# Enable debug logging first
configure_logging(level="DEBUG")

client = get_api_client()

# Make request with dry_run to see details without sending
from britecore_sdk.api.api_calls.v2 import policies
policy = policies.retrieve_policy(policy_number="POL-123", dry_run=True)
# This logs request details without sending
```

---

## Multi-Environment and Multi-Site Issues

### "Using multiple sites/environments"

**Solution:**

```python
from britecore_sdk.api.api_calls import init_api_client, use_api_client

# Initialize clients for each site
prod_client = init_api_client("production").init_client()
sandbox_client = init_api_client("sandbox").init_client()

# Use in context managers
with use_api_client(prod_client):
    from britecore_sdk.api.api_calls.v2 import policies
    prod_policy = policies.retrieve_policy(policy_number="POL-123")

with use_api_client(sandbox_client):
    sandbox_policy = policies.retrieve_policy(policy_number="TEST-POL-123")
```

---

## SSL/TLS Certificate Issues

### "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause:** SSL certificate verification failed (usually self-signed certs)

**Solution:**

```python
import urllib3

# ONLY for development/testing with self-signed certificates
# DO NOT USE IN PRODUCTION
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Then initialize client
from britecore_sdk.api.api_calls import init_api_client
client = init_api_client("production").init_client()
```

**Better Solution (Production):**

- Get valid SSL certificate
- Update CA bundle: `pip install --upgrade certifi`
- Or export cert: `export SSL_CERT_FILE=/path/to/cert.pem`

---

## Troubleshooting Summary

- **API client initialization failures** usually indicate missing `target_site` or site config. The `api_client` proxy initializes lazily on first use. Use `get_api_client()` for explicit initialization or to force config reload. Use `init_api_client()` only for advanced/manual re-initialization scenarios.
- **To swap sites or isolate tests,** call `reset_api_client()` before calling `init_api_client("new_site")`.
- **To debug without sending a real request,** pass `dry_run=True` to any endpoint wrapper call, or initialize once with `init_api_client(client_dry_run=True)` for a whole scratch script/test flow.
- **CLI commands** (`britecore-quick-check`, `britecore-config-wizard`, `britecore-check-config`, `britecore-healthcheck`, `britecore-normalize-json`) are available after `pip install`; fall back to `python -m britecore_sdk.cli.<module>` for CLI modules otherwise.

---

## Additional Resources

### Documentation

- **Getting Started:** [GETTING_STARTED.md](./GETTING_STARTED.md)
- **Common Patterns:** [docs/COMMON_PATTERNS.md](./docs/COMMON_PATTERNS.md)
- **Configuration Guide:** [docs/CONFIGURATION.md](./docs/CONFIGURATION.md)
- **API Reference:** [API.md](./API.md)
- **Architecture:** [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Migration v1→v2:** [docs/MIGRATION_v1_to_v2.md](./docs/MIGRATION_v1_to_v2.md)

### Code Examples

- **Complete Workflow:** `examples/complete_workflow.py`
- **Error Handling:** `examples/advanced_error_handling.py`
- **Async Operations:** `examples/async_operations.py`
- **Configuration Examples:** `examples/configuration_examples.py`
- **See all examples:** [examples/README.md](./examples/README.md)

### Support

- **GitHub Issues:** <https://github.com/sshimek42/britecore_sdk/issues>
- **Security Issues:** See [SECURITY.md](./SECURITY.md)
- **Discussion:** GitHub Discussions

---

## Reporting Issues

When reporting an issue, include:

1. **SDK Version:**

   ```bash
   python -c "import britecore_sdk; print(britecore_sdk.__version__)"
   ```

2. **Python Version:**

   ```bash
   python --version
   ```

3. **Error Message:** Full traceback

4. **Steps to Reproduce:** Minimal code example

5. **Configuration Status:**

   ```bash
   britecore-check-config
   # Don't include actual credentials!
   ```

6. **Environment:**
   - OS (Windows/macOS/Linux)
   - Virtual environment (venv/conda/etc)
   - Network/proxy issues (if any)

## Troubleshooting FAQ

### I'm brand new - where do I start?

**Follow these steps in order:**

1. **Install the SDK:**

   ```bash
   pip install -e .
   ```

2. **Create configuration files:**

   ```bash
   mkdir -p ~/.britecore
   # Add your settings to ~/.britecore/settings.toml and ~/.britecore/.secrets.toml
   # See GETTING_STARTED.md for templates
   ```

3. **Test the setup:**

   ```bash
   britecore-check-config
   britecore-healthcheck
   ```

4. **Run your first API call:**

   ```python
   from britecore_sdk.api.api_calls import get_api_client
   from britecore_sdk.api.api_calls.v2 import policies

   policy = policies.retrieve_policy(policy_number="POL-001")
   print(policy)
   ```

**Then read:** [GETTING_STARTED.md](./GETTING_STARTED.md)

---

### I'm getting permission errors during install

**Solution:**

Option A: Use a virtual environment (recommended):

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -e .
```

Option B: Use --user flag:

```bash
pip install --user -e .
```

---

### My API calls are failing - how do I debug?

**Step 1: Enable debug logging**

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)

# Now make your API call
from britecore_sdk.api.api_calls import get_api_client
client = get_api_client()
```

**Step 2: Check the request details without sending**

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

init_api_client(client_dry_run=True)
result = policies.retrieve_policy(policy_number="POL-123")
print(result["dry_run"])  # True
```

**Step 3: Check correlation ID**

Look for `[req_id: xxx]` in the log output - use this to trace requests in API logs.

---

### Configuration is confusing - what's the simplest setup?

**Minimal setup (recommended for most users):**

**File: `~/.britecore/settings.toml`**

```toml
[default]
target_site = "production"
```

**File: `~/.britecore/.secrets.toml`**

```toml
[production]
base_url = "https://api.britecore.example.com"
api_key = "your_api_key_here"
```

**Then in code:**

```python
from britecore_sdk.api.api_calls import get_api_client
client = get_api_client()  # Auto-loads config
```

---

### I need to use multiple environments/sites

**Setup multiple site configs:**

**`~/.britecore/.secrets.toml`:**

```toml
[production]
base_url = "https://prod.example.com"
api_key = "prod_key"

[staging]
base_url = "https://staging.example.com"
api_key = "staging_key"

[development]
base_url = "http://localhost:8000"
api_key = "dev_key"
```

**Use in code:**

```python
from britecore_sdk.api.api_calls import init_api_client, use_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Prod context
with use_api_client(init_api_client("production").init_client()):
    prod_policy = policies.retrieve_policy(policy_number="POL-123")

# Staging context
with use_api_client(init_api_client("staging").init_client()):
    staging_policy = policies.retrieve_policy(policy_number="POL-456")
```

---

### I keep hitting rate limits - how do I fix it?

**Option 1: Implement backoff**

See: `examples/advanced_error_handling.py`

**Option 2: Enable client-side rate limiting**

```python
from britecore_sdk.api.api_calls import init_api_client

client = init_api_client(
    "production",
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5.0
)
```

**Option 3: Use async for concurrent requests**

```python
import asyncio
from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

async def fetch_many():
    init_async_api_client("production")
    tasks = [aretrieve_policy(policy_id=f"POL-{i}") for i in range(100)]
    return await asyncio.gather(*tasks)

results = asyncio.run(fetch_many())
```

**See also:** [docs/RATE_LIMITING.md](./docs/RATE_LIMITING.md)

---

### I want to validate data before sending to API

**Use SDK models and validators:**

```python
from britecore_sdk.models import BritecoreContact
from britecore_sdk.validators import EmailValidator

contact_data = {
    "name": "John Smith",
    "email": [{"email": "john@example.com", "type": "Work"}]
}

# This validates and processes the contact
contact = BritecoreContact(**contact_data)
validated = contact.process_contact()

# Now send to API
from britecore_sdk.api.api_calls.v2 import contacts
result = contacts.new_contact(contact=validated)
```

---

### Tests are failing - what should I do?

**Step 1: Check test setup**

```bash
# Run from project root
cd britecore_sdk
python -m pytest tests/ -v
```

**Step 2: Run specific test module**

```bash
python -m pytest tests/unit/test_models.py -v
```

**Step 3: Run with coverage**

```bash
python -m pytest tests/ --cov=src/britecore_sdk --cov-report=html
```

**Step 4: Check for missing dependencies**

```bash
pip install -e ".[dev]"
```

---

### I'm upgrading from v1 to v2 - what changed?

**See:** [docs/MIGRATION_v1_to_v2.md](./docs/MIGRATION_v1_to_v2.md)

**Quick checklist:**

- [ ] Update package: `pip install --upgrade britecore-sdk`
- [ ] Update imports: `v1` → `v2` endpoints
- [ ] Update exceptions: `BritecoreError.NotFoundError` → `NotFoundError`
- [ ] Use lazy client: `get_api_client()` instead of `API_CLIENT`
- [ ] Test configuration: Run `britecore-healthcheck`

---

### Performance is slow - how do I speed it up?

**1. Enable async:**

```python
# Instead of sequential loop:
for policy_id in policy_ids:
    policy = policies.retrieve_policy(policy_id=policy_id)

# Use async:
import asyncio
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy
results = asyncio.run(fetch_concurrent(policy_ids))
```

**2. Use caching:**

```python
from britecore_sdk.api.api_calls.v2 import policies

# Cache results for 1 hour
policy = policies.retrieve_policy(policy_number="POL-123", cache_ttl=3600)
```

**3. Batch operations:**

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

result = create_full_quotes_batch(quotes_data, max_workers=10)
```

---

### I need to test without making real API calls

**Use dry-run mode:**

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Enable dry-run
init_api_client("production", client_dry_run=True)

# All calls are logged but not sent
result = policies.retrieve_policy(policy_number="POL-123")
print(result["dry_run"])  # True
```
