# Configuration Guide

This guide explains how to configure `britecore_libraries` for your environment.

## Overview

Configuration uses **Dynaconf**, a hierarchical settings manager that supports:

- TOML files (primary)
- Environment variables
- Default values
- Per-site overrides

## Config Files

### Location

```text
src/britecore_libraries/config/
|-- sample/
|   |-- settings.toml  # Sample/template for public settings (tracked in git)
|   `-- .secrets.toml  # Sample/template for secrets (tracked in git, no real values)
|-- settings.toml      # Your public settings (tracked in git)
|-- .secrets.toml      # Your secrets (gitignored — never commit)
`-- config.py          # Dynaconf loader
```

> **Tip:** Copy the files from `config/sample/` to `config/` as a starting point,
> then fill in your real values.

### `settings.toml` (Public)

Contains default non-secret runtime settings (no credentials):

```toml
# Default runtime configuration (applies to all sites unless overridden)
[default]
web_timeout = 30        # API request timeout in seconds
web_retry = 10          # Number of retries for API requests
web_timeout_long = 60   # Long-running API request timeout in seconds

# Site section definitions (no base_url or credentials — those go in .secrets.toml)
[example_site]
# Leave empty or add only non-sensitive configuration

[example_site_test]
# Leave empty or add only non-sensitive configuration
```

**When to edit:**

- Add new site section headers (credentials go in .secrets.toml)
- Override default API request settings (`web_timeout`, `web_retry`, `web_timeout_long`)

**Never commit:**

- Any base_url, API keys, client IDs, client secrets, or credentials

### `.secrets.toml` (Private)

Contains **all sensitive credentials and site configuration**. **This file is gitignored.**

```toml
# Default credentials template
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
```

**How to create:**

1. Copy `src/britecore_libraries/config/sample/.secrets.toml` to `src/britecore_libraries/config/.secrets.toml`
2. Replace placeholder values with your real base_url and credentials for each site
3. **Never commit** `.secrets.toml` (it's already gitignored)

**File format:**

- All site credentials and base URLs go here
- Values in `.secrets.toml` override `settings.toml`
- All sections are optional

## Loading Configuration

### Automatic (Recommended)

```python
# Recommended: Use the lazy-initialized client (auto-loads config on first use)
from britecore_libraries.api.api_calls import get_api_client

client = get_api_client()
```

**What happens:**

1. `target_site` argument specifies which config section to load (e.g., `[example_site]`)
2. Dynaconf merges `settings.toml` + `.secrets.toml` + environment variables
3. Secrets override public settings

### Via `get_api_client()` (Lazy, Recommended)

```python
from britecore_libraries.api.api_calls import get_api_client

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

### Interactive menu behavior in IDE consoles

`utils.interactive_menu.line_menu()` uses `questionary` for richer prompts when a
native console is available. In some IDE run consoles on Windows (including
PyCharm), `questionary`/`prompt_toolkit` may not have a Win32 console buffer.
When that occurs, the SDK automatically falls back to a plain numbered `input()`
menu so line/date/state selection still works.

## Validation

When you call `client.init_client()`, Dynaconf validates required keys. This is only needed for advanced/manual scenarios. For most use cases, prefer `get_api_client()`.

You can also validate all configured site sections directly:

```bash
python -m britecore_libraries.utils.check_site_configs
```

```powershell
python -m britecore_libraries.utils.check_site_configs
```

Then run an end-to-end readiness check for a specific site:

```bash
python -m britecore_libraries.utils.healthcheck --site example_site
```

```powershell
python -m britecore_libraries.utils.healthcheck --site example_site
```

`check_site_configs` validates each site section in
`src/britecore_libraries/config/.secrets.toml` using this rule:

- `base_url` is required
- auth must be either:
  - OAuth pair (`client_id` and `client_secret` together), or
  - API key (`api_key`)

The utility also warns when sensitive keys (`api_key`, `client_id`,
`client_secret`) are present in `settings.toml`.

**Common errors:**

| Error | Cause | Fix |
| ----- | ----- | --- |
| `BritecoreKeyError` | Missing `base_url` | Add `base_url` to `.secrets.toml` site section or set `BRITECORE_LIBRARIES_BASE_URL` |
| `BritecoreKeyError` | Missing `client_id`/`client_secret` | Add both for OAuth, or add `api_key` for API key auth |
| `BritecoreKeyError` | Missing `api_key` | Add `api_key` to `.secrets.toml` |
| Config not loading | `target_site` not set | Set `$env:target_site` or pass to `BritecoreAPIClient("site_name")` |
| `INCORRECT` in `check_site_configs` output | Missing required site keys in `.secrets.toml` | Add missing keys shown in `Missing Keys` column |

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

- Install base package only (`pip install -e .`); do not install optional extras unless needed.
- Set `target_site` to a configured site section in `settings.toml`/`.secrets.toml`.
- Set `BRITECORE_LIBRARIES_BASE_URL` for the target BriteCore instance.
- Choose one auth mode: either set `BRITECORE_LIBRARIES_API_KEY`, or set both `BRITECORE_LIBRARIES_CLIENT_ID` and `BRITECORE_LIBRARIES_CLIENT_SECRET`.
- Store production secrets in a secrets manager (Vault, AWS Secrets Manager, etc.), not in committed files.
- Verify startup with a minimal init check (`get_api_client()`) before serving traffic. Use `BritecoreAPIClient(...).init_client()` only for advanced/manual scenarios.

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

## Private Maps Behavior

Some features in britecore_libraries rely on map files (such as policy, field, or agency maps) located in `src/britecore_libraries/maps/`. These files provide environment-specific mappings and are selected at runtime based on environment variables.

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
  - Verify that the corresponding map file exists in `src/britecore_libraries/maps/`.
  - If you see errors about missing maps or unset variables, set the required env vars and restart your process.

## See Also

- [GETTING_STARTED.md](../GETTING_STARTED.md) -- Quick setup guide
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) -- Common errors
- [src/britecore_libraries/config/config.py](../src/britecore_libraries/config/config.py) -- Config loader implementation
