# Troubleshooting Guide

*Last updated: April 7, 2026*
*Document type: Living troubleshooting guide*

**BriteCore Libraries** - Common issues and solutions

---

## Installation Issues

### "ModuleNotFoundError: No module named 'britecore_libraries'"

**Cause:** Package not installed in current environment

**Solution:**

```powershell
# Install in editable mode
pip install -e .

# Or with dev tools
pip install -e ".[dev]"

# Verify installation
python -c "import britecore_libraries; print(britecore_libraries.__version__)"
```

---

### "pip install" hangs or is very slow

**Cause:** Network issues or large dependency tree

**Solution:**

```powershell
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

```powershell
# Use --user flag
pip install --user -e .

# Or use virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

---

## Configuration Issues

### "No target_site assigned"

**Cause:** Missing environment variable

**Solution:**

```powershell
# Set environment variable
$env:target_site = "your_site"

# Verify
python -c "import os; print(os.environ.get('target_site'))"
```

---

### "Configuration validation failed"

**Cause:** Missing required settings in config file

**Solution:**

Check `src/britecore_libraries/config/settings.toml`:

```toml
[production]
base_url = "https://..."          # Required
api_key = "..."                   # Required (if no OAuth)
client_id = ""                    # Leave blank for API key
client_secret = ""                # Leave blank for API key
web_timeout = 5                   # Required
web_retry = 3                     # Required
```

**Or use environment variables:**

```powershell
$env:BRITECORE_BASE_URL="https://..."
$env:BRITECORE_API_KEY="..."
$env:BRITECORE_WEB_TIMEOUT="5"
```

---

### "File not found: .secrets.toml"

**Cause:** No secrets file created

**Solution:**

Create `src/britecore_libraries/config/.secrets.toml`:

```toml
[production]
api_key = "your_api_key_here"
client_secret = ""

[staging]
api_key = "your_test_api_key_here"
```

Or just use environment variables (they override file settings).

---

## Runtime Issues

### "Failed to retrieve OAuth token"

**Cause:** Invalid OAuth credentials or token endpoint unreachable

**Solution:**

```python
# Check credentials in config
from britecore_libraries.config import settings
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
from britecore_libraries.api.api_calls.v2 import policies
from britecore_libraries.exceptions import BritecoreError

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
from britecore_libraries.exceptions import BritecoreError

try:
    ...
except BritecoreError.Base as exc:
    print(f"SDK failure: {exc}")
```

---

### "Invalid phone number" validation error

**Cause:** Phone number format not recognized

**Solution:**

```python
from britecore_libraries.validators import PhoneValidator

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
from britecore_libraries.validators import EmailValidator

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

### "Cannot import name 'X' from 'britecore_libraries'"

**Cause:** Module or function doesn't exist or not exported

**Solution:**

```python
# Check what's available
import britecore_libraries
print(dir(britecore_libraries))

# Check __all__ in module
from britecore_libraries.models import __all__
print(__all__)

# Look at actual exports
from britecore_libraries.models import *
```

---

## Testing Issues

### "ModuleNotFoundError" in tests

**Cause:** Test dependencies not installed

**Solution:**

```powershell
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
with patch("britecore_libraries.api.api_calls.API_CLIENT") as mock:
    # Now use the mock
    mock.do_request.return_value = ...
```

---

### "Coverage report shows 0%"

**Cause:** Coverage tool not configured

**Solution:**

```powershell
# Make sure pytest-cov installed
pip install -e ".[dev]"

# Run with coverage
python -m pytest tests/ --cov=src/britecore_libraries --cov-report=html

# View report
Invoke-Item htmlcov/index.html
```

---

### "Cannot find conftest.py"

**Cause:** Running pytest from wrong directory

**Solution:**

```powershell
# Run from project root
cd britecore_libraries
python -m pytest tests/ -v

# NOT from tests/ directory
```

---

## API Client Issues

### "Timeout error" on slow API

**Cause:** Default timeout too short

**Solution:**

```python
from britecore_libraries.api.api_calls.v2 import policies
from urllib3 import Timeout

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
from britecore_libraries.api.api_calls.v2 import policies
from urllib3 import Retry

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

# Now all debug messages will print
from britecore_libraries.api.api_calls.v2 import policies
policy = policies.retrieve_policy(policy_number="POL001")
# Check console for debug output
```

---

### Inspect Request/Response

```python
from britecore_libraries.api.api_calls import API_CLIENT
from unittest.mock import patch

with patch.object(API_CLIENT, 'do_request', wraps=API_CLIENT.do_request) as mock:
    policy = retrieve_policy(policy_number="POL001")
    
    # Check what was sent
    call_args = mock.call_args
    print(f"Path: {call_args[1]['path']}")
    print(f"Payload: {call_args[1]['json']}")
```

---

### Check API Response Format

```python
import json
from britecore_libraries.api.api_calls import API_CLIENT

response = API_CLIENT.do_request(
    path="/api/v2/policies/retrieve_policy",
    json={"policy_number": "POL001"}
)

# Raw response
print(f"Status: {response.status}")
print(f"Data: {response.data.decode('utf-8')}")

# Parsed response
data = json.loads(response.data)
print(json.dumps(data, indent=2))
```

---

## Performance Issues

### Slow API responses

**Solution:**

```python
import time

start = time.time()
policy = retrieve_policy(policy_number="POL001")
elapsed = time.time() - start

print(f"Request took {elapsed:.2f}s")

# If too slow:
# 1. Check network latency: ping api.britecore.com
# 2. Increase timeout
# 3. Check server status
# 4. Use connection pooling (automatic with urllib3)
```

---

### High memory usage

**Solution:**

```python
# Don't store large result sets
# Process in batches instead

# Bad:
all_policies = [retrieve_policy(f"POL{i}") for i in range(10000)]

# Good:
for i in range(10000):
    policy = retrieve_policy(f"POL{i}")
    process_policy(policy)
    # Memory freed after each iteration
```

---

## Still Having Issues?

### Check These First

1. **Environment Variables:** `echo $env:target_site`
2. **Config File:** `Get-Content src/britecore_libraries/config/settings.toml`
3. **Python Version:** `python --version` (should be 3.11+)
4. **Package Installation:** `pip show britecore-libraries`
5. **Test Suite:** `python -m pytest tests/unit/test_maps.py -v`

### Get Help

1. Check [README.md](README.md) for overview
2. Review [AGENTS.md](AGENTS.md) for patterns
3. Look at test examples in `tests/`
4. See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
5. Check [CONTRIBUTING.md](CONTRIBUTING.md) for development

---
