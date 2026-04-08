# Configuration Guide

This guide explains how to configure `britecore_libraries` for your environment.

## Overview

Configuration uses **Dynaconf**, a hierarchical settings manager that supports:

- TOML files (primary)
- Environment variables
- Fallback defaults
- Per-site overrides

## Config Files

### Location

```text
src/britecore_libraries/config/
|-- settings.toml      # Public settings (tracked in git)
|-- .secrets.toml      # Secrets (gitignored)
`-- config.py          # Dynaconf loader
```

### `settings.toml` (Public)

Contains default non-secret runtime settings (no credentials):

```toml
# Default runtime configuration (applies to all sites unless overridden)
[default]
web_timeout = 30
web_retry = 10
web_timeout_long = 60
web_browser = "Edge"

# Site section definitions (no base_url or credentials — those go in .secrets.toml)
[example_site]
# Leave empty or add only non-sensitive configuration

[example_site_test]
# Leave empty or add only non-sensitive configuration
```

**When to edit:**

- Adjust default runtime settings (timeouts, retries, browser)
- Add new site section headers (credentials go in .secrets.toml)

**Never commit:**

- Any base_url, API keys, client IDs, client secrets, or credentials

### `.secrets.toml` (Private)

Contains **all sensitive credentials and site configuration**. **This file is gitignored.**

```toml
# Default (fallback) credentials
[default]
base_url = ""
client_id = ""
client_secret = ""
api_key = ""

# Example: Site-specific credentials
[example_site]
base_url = "https://api.example.com"
client_id = "your_real_client_id"
client_secret = "your_real_client_secret"

[example_site_test]
base_url = "https://api-test.example.com"
api_key = "your_real_api_key"

# Optional utility settings (site-scoped)
db_conn_string = "Driver={ODBC Driver 17 for SQL Server};Server=...;Database=...;"
db_conn_options = { autocommit = true, timeout = 30 }
web_user = "selenium_user"
web_pass = "selenium_password"
web_browser = "Edge"
```

**How to create:**

1. Create `.secrets.toml` in `src/britecore_libraries/config/`
2. Add base_url and credentials for each site
3. **Never commit** `.secrets.toml` (it's already gitignored)

**File format:**

- All site credentials and base URLs go here
- Values in `.secrets.toml` override `settings.toml`
- All sections are optional

## Loading Configuration

### Automatic (Recommended)

```python
from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

# Loads from settings.toml + .secrets.toml automatically
client = BritecoreAPIClient(target_site="example_site")
client.init_client()
```

**What happens:**

1. `target_site` argument specifies which config section to load (e.g., `[example_site]`)
2. Dynaconf merges `settings.toml` + `.secrets.toml` + environment variables
3. Secrets override public settings

### Via `get_api_client()` (Lazy)

```python
from britecore_libraries import get_api_client

# Lazy initialization -- config is loaded on first use
client = get_api_client()
```

Requires `target_site` environment variable (see below).

## Environment Variables

You can override config values with environment variables:

```powershell
# Set the active site
$env:target_site = "example_site"

# Override a specific setting
$env:BRITECORE_LIBRARIES_BASE_URL = "custom.britecore.com"

# System selection (for regex maps, if applicable)
$env:system = "example_site"
```

**Priority order (highest to lowest):**

1. Environment variables (e.g., `BRITECORE_LIBRARIES_*`)
2. `.secrets.toml` values (all base_url and credentials)
3. `settings.toml` values (urllib3 defaults and site definitions)
4. Built-in defaults

## Required Keys by Auth Mode

### API Key Auth

Required keys:

- `base_url` -- API base URL
- `api_key` -- API key value

Optional:

- `client_id` (leave blank to skip OAuth)
- `client_secret` (leave blank to skip OAuth)

### OAuth Auth

Required keys:

- `base_url` -- API base URL
- `client_id` -- OAuth client ID
- `client_secret` -- OAuth client secret

Optional:

- `api_key` (will be ignored if `client_id` + `client_secret` are set)

**Auth mode selection:**

```python
if client_id and client_secret:
    # Use OAuth
else:
    # Use API key
```

## Optional Utility Keys

These keys are optional and only used when importing/calling the related utilities.

### ODBC (`britecore_odbc`)

- `db_conn_string` (required for config-based ODBC usage)
- `db_conn_options` (required for config-based ODBC usage; must be a dict)

```python
from britecore_libraries.utils.britecore_odbc import get_cursor

# Requires explicit target_site when loading DB config from Dynaconf
cursor = get_cursor(target_site="example_site")

# Explicit values bypass config lookup
cursor = get_cursor(
    conn_string="Driver={ODBC Driver 17 for SQL Server};Server=...;Database=...;",
    conn_options={"autocommit": True},
)
```

If config lookup is used without `target_site`, the utility raises
`BritecoreError.ConfigurationError`.

### Selenium (`britecore_selenium`)

- `web_browser` (optional default browser)
- `web_user` (optional login default for `bc_login`)
- `web_pass` (optional login default for `bc_login`)

Browser precedence in `get_driver(...)`:

1. Explicit `browser` argument
2. Config value `web_browser`
3. Fallback default `Edge`

Invalid browser names raise `BritecoreError.Base`.

## Validation

When you call `client.init_client()`, Dynaconf validates required keys:

```python
client = BritecoreAPIClient("example_site")
client.init_client()
# Raises BritecoreError if base_url or auth credentials are missing
```

**Common errors:**

| Error | Cause | Fix |
| ----- | ----- | --- |
| `BritecoreKeyError` | Missing `base_url` | Add `base_url` to `.secrets.toml` site section or set `BRITECORE_LIBRARIES_BASE_URL` |
| `BritecoreKeyError` | Missing `client_id`/`client_secret` | Add both for OAuth, or add `api_key` for API key auth |
| `BritecoreKeyError` | Missing `api_key` | Add `api_key` to `.secrets.toml` |
| Config not loading | `target_site` not set | Set `$env:target_site` or pass to `BritecoreAPIClient("site_name")` |

## Per-Environment Setup

### Development

```powershell
# Set environment for local testing
$env:target_site = "example_site_test"

# Create .secrets.toml with test credentials
# [example_site_test]
# api_key = "your_test_key"
```

### CI/CD Pipelines

Store credentials as **GitHub repository secrets**:

1. Go to **Settings -> Secrets and variables -> Actions**
2. Create secrets:
   - `BRITECORE_CLIENT_ID`
   - `BRITECORE_CLIENT_SECRET`
   - `BRITECORE_API_KEY`
   - `BRITECORE_BASE_URL`
   - (any others needed)

3. Reference in workflow:

```yaml
env:
  BRITECORE_LIBRARIES_BASE_URL: ${{ secrets.BRITECORE_BASE_URL }}
  BRITECORE_LIBRARIES_API_KEY: ${{ secrets.BRITECORE_API_KEY }}
  target_site: example_site_test
```

### Production

Use environment variables or a secrets management system (e.g., AWS Secrets Manager, HashiCorp Vault):

```powershell
# Before app startup
$env:BRITECORE_LIBRARIES_BASE_URL = "prod.britecore.com"
$env:BRITECORE_LIBRARIES_CLIENT_ID = "prod_client_id"
$env:BRITECORE_LIBRARIES_CLIENT_SECRET = "prod_client_secret"
$env:target_site = "example_site"

# Then start your application
python app.py
```

#### API-only deployment checklist

- Install base package only (`pip install -e .`); do not install optional browser/database extras unless needed.
- Set `target_site` to a configured site section in `settings.toml`/`.secrets.toml`.
- Set `BRITECORE_LIBRARIES_BASE_URL` for the target BriteCore instance.
- Choose one auth mode: either set `BRITECORE_LIBRARIES_API_KEY`, or set both `BRITECORE_LIBRARIES_CLIENT_ID` and `BRITECORE_LIBRARIES_CLIENT_SECRET`.
- Store production secrets in a secrets manager (Vault, AWS Secrets Manager, etc.), not in committed files.
- Verify startup with a minimal init check (`get_api_client()` or `BritecoreAPIClient(...).init_client()`) before serving traffic.

## Troubleshooting

### "Config not loading" or "Key not found"

1. Verify `target_site` is set:

   ```powershell
   $env:target_site
   ```

   Should output your site name (e.g., `example_site`)

2. Check `.secrets.toml` has the site section with required auth keys:

   ```powershell
   Select-String -Path "src/britecore_libraries/config/.secrets.toml" -Pattern "\[example_site\]"
   ```

3. Check `.secrets.toml` exists and has values:

   ```powershell
   Get-Content "src/britecore_libraries/config/.secrets.toml"
   ```

4. Test config loading directly:

   ```python
   from britecore_libraries.config.config import LoadClientSettings

   settings = LoadClientSettings("example_site")
   print(settings)  # Should show loaded config
   ```

### Auth failures

1. Verify credentials in `.secrets.toml`:
   - For API key: `api_key` is set
   - For OAuth: both `client_id` and `client_secret` are set

2. Verify `base_url` matches the BriteCore instance:

   ```python
   from britecore_libraries import get_api_client
   client = get_api_client()
   print(client.base_url)  # Should be your BriteCore instance
   ```

3. For OAuth failures, check token endpoint is accessible:

   ```powershell
   # Verify endpoint format
   # Should be: https://{base_url}/api/auth/oauth2/token
   ```

## Adding New Sites

1. Edit `settings.toml` to add a site section (if needed):

    ```toml
    [mysite]
    # Optional: add non-sensitive configuration here
    ```

2. Edit `.secrets.toml` to add credentials and base_url:

    ```toml
    [mysite]
    base_url = "https://mysite.britecore.com"
    client_id = "..."
    client_secret = "..."
    # or
    api_key = "..."
    ```

3. Use:

    ```python
    client = BritecoreAPIClient("mysite")
    client.init_client()
    ```

## See Also

- [GETTING_STARTED.md](../GETTING_STARTED.md) -- Quick setup guide
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) -- Common errors
- [src/britecore_libraries/config/config.py](../src/britecore_libraries/config/config.py) -- Config loader implementation
