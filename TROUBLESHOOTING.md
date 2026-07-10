# Troubleshooting Guide

*Last updated: July 10, 2026*
*Document type: Living troubleshooting guide*

**BriteCore Libraries** - Common issues and solutions

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
# Installed CLI (v1.1+) — works in bash and PowerShell:
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

Or using the flat aliases introduced in v1.1 (shorter imports):

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

### Inspect a request without sending it (dry-run, v1.1+)

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

### Reset the API client between tests or sites (v1.1+)

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

1. Check [README.md](README.md) for overview
2. Review [AGENTS.md](AGENTS.md) for patterns
3. Look at test examples in `tests/`
4. See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
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

## Troubleshooting Summary

- **API client initialization failures** usually indicate missing `target_site` or site config. The `api_client` proxy initializes lazily on first use. Use `get_api_client()` for explicit initialization or to force config reload. Use `init_api_client()` only for advanced/manual re-initialization scenarios.
- **To swap sites or isolate tests,** call `reset_api_client()` before calling `init_api_client("new_site")`.
- **To debug without sending a real request,** pass `dry_run=True` to any endpoint wrapper call, or initialize once with `init_api_client(client_dry_run=True)` for a whole scratch script/test flow.
- **CLI commands** (`britecore-healthcheck`, `britecore-check-config`, `britecore-run-checks`) are available after `pip install`; fall back to `python -m britecore_sdk.utils.<module>` otherwise.
