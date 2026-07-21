# Configuration Guide

*Last updated: July 21, 2026*
*Document type: Living guide*

This guide explains how to configure `britecore_sdk` for your environment.

Minimum supported Python version: `3.11`.

## Overview

Configuration uses **Dynaconf**, a hierarchical settings manager that supports:

- TOML files (primary)
- Environment variables
- Default values
- Per-site overrides

## Config Files

### Canonical precedence table

Configuration is layered (lowest to highest priority):

| Priority | Location | File(s) |
|---|---|---|
| 1 (lowest) | SDK package defaults | `src/britecore_sdk/settings/settings.toml`, `src/britecore_sdk/settings/.secrets.toml` |
| 2 | User-level config | `~/.britecore/settings.toml`, `~/.britecore/.secrets.toml` |
| 3 | Project-local config | `./britecore.toml`, `./.britecore_secrets.toml` |
| 4 | Explicit file override | Path from `BRITECORE_SDK_SETTINGS_FILE` |
| 5 (highest) | Environment variables | `BRITECORE_SDK_*` |

Environment variables override all file-based values.

### SDK package default files (mainly for source clones)

```text
src/britecore_sdk/settings/
|-- sample/
|   |-- settings.toml  # Sample/template for public settings (tracked in git)
|   `-- .secrets.toml  # Sample/template for secrets (tracked in git, no real values)
|-- settings.toml      # Your public settings (tracked in git)
|-- .secrets.toml      # Your secrets (gitignored — never commit)
`-- config.py          # Dynaconf loader
```

> **Tip:** For pip-installed usage, prefer user-level files (`~/.britecore/...`) or
> project-local files (`./britecore.toml`, `./.britecore_secrets.toml`) instead of
> editing files under `src/`.

### `settings.toml` (Public)

Contains default non-secret runtime settings (no credentials):

```toml
# Default runtime configuration (applies to all sites unless overridden)
[default]
web_timeout = 30        # API request timeout in seconds
web_retry = 10          # Number of retries for API requests
web_timeout_long = 60   # Long-running API request timeout in seconds

# Optionally set target_site here to avoid passing it in code or as an env var.
# target_site = "example_site"

# Site section definitions (no base_url or credentials — those go in .secrets.toml)
[example_site]
# Leave empty or add only non-sensitive configuration

[example_site_test]
# Leave empty or add only non-sensitive configuration
```

**When to edit:**

- Add new site section headers (credentials go in .secrets.toml)
- Override default API request settings (`web_timeout`, `web_retry`, `web_timeout_long`)
- Set `target_site` under `[default]` to avoid passing it in code or as an environment variable

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

**How to create (source clone workflow):**

1. Copy `src/britecore_sdk/settings/sample/.secrets.toml` to `src/britecore_sdk/settings/.secrets.toml`
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
from britecore_sdk.api.api_calls import get_api_client

client = get_api_client()
```

**What happens:**

1. `target_site` selects the site section (for example `[example_site]`)
2. Dynaconf resolves layered files (SDK defaults, user-level, project-local, explicit file)
3. `BRITECORE_SDK_*` environment variables override file values

### Via `get_api_client()` (Lazy, Recommended)

```python
from britecore_sdk.api.api_calls import get_api_client

# Lazy initialization -- config is loaded on first use
client = get_api_client()
```

Requires `target_site` to be set in `settings.toml`, as an environment variable, or passed
explicitly to `init_api_client()` before calling `get_api_client()`.

## Environment Variables

You can set `target_site` and override config values with environment variables:

```powershell
# Set the active site (alternative: set target_site in settings.toml [default])
$env:target_site = "example_site"

# Override a specific setting (BRITECORE_SDK_* env vars take precedence over .secrets.toml)
$env:BRITECORE_SDK_BASE_URL = "custom.britecore.com"

# System selection (for regex maps, if applicable)
$env:system = "example_site"
```

**`target_site` resolution order (first non-empty value wins):**

1. Explicit argument passed to `init_api_client(target_site=...)`
2. `target_site` key in `settings.toml` under `[default]`
3. `target_site` environment variable

**Role of `target_site`:** `target_site` selects which section of `.secrets.toml` (and
`settings.toml`) is used to load credentials. When **all** required credentials are supplied via
`BRITECORE_SDK_*` environment variables, the specific `target_site` value does not affect
which credentials are loaded — env vars take precedence over TOML values regardless of the
section name. However, `target_site` is still required for client initialization. If any required
credential is missing from env vars, the client will fall back to the `.secrets.toml` section
matching the `target_site` value, so the name must correspond to a real section in that case.

**Priority order for other config values (highest to lowest):**

1. Environment variables (for example `BRITECORE_SDK_*`)
2. Explicit file path from `BRITECORE_SDK_SETTINGS_FILE`
3. Project-local files (`./britecore.toml`, `./.britecore_secrets.toml`)
4. User-level files (`~/.britecore/settings.toml`, `~/.britecore/.secrets.toml`)
5. SDK package defaults (`src/britecore_sdk/settings/settings.toml`, `src/britecore_sdk/settings/.secrets.toml`)

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
python -m britecore_sdk.utils.check_site_configs
```

```powershell
python -m britecore_sdk.utils.check_site_configs
```

Then run an end-to-end readiness check for a specific site:

```bash
python -m britecore_sdk.utils.healthcheck --site example_site
```

```powershell
python -m britecore_sdk.utils.healthcheck --site example_site
```

`check_site_configs` validates each site section in
`src/britecore_sdk/settings/.secrets.toml` using this rule:

- `base_url` is required
- auth must be either:
  - OAuth pair (`client_id` and `client_secret` together), or
  - API key (`api_key`)

The utility also warns when sensitive keys (`api_key`, `client_id`,
`client_secret`) are present in `settings.toml`.

**Common errors:**

| Error | Cause | Fix |
| ----- | ----- | --- |
| `BritecoreKeyError` | Missing `base_url` | Add `base_url` to `.secrets.toml` site section or set `BRITECORE_SDK_BASE_URL` |
| `BritecoreKeyError` | Missing `client_id`/`client_secret` | Add both for OAuth, or add `api_key` for API key auth |
| `BritecoreKeyError` | Missing `api_key` | Add `api_key` to `.secrets.toml` |
| Config not loading | `target_site` not set | Set `target_site` in `settings.toml` `[default]`, set `$env:target_site`, or pass to `init_api_client(target_site="site_name")` |
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
  BRITECORE_SDK_BASE_URL: ${{ secrets.BRITECORE_BASE_URL }}
  BRITECORE_SDK_API_KEY: ${{ secrets.BRITECORE_API_KEY }}
  target_site: example_site_test  # required; selects .secrets.toml section (any name works when all creds are in env vars)
```

### Production

Use environment variables or a secrets management system (e.g., AWS Secrets Manager, HashiCorp Vault):

```powershell
# Before app startup
$env:BRITECORE_SDK_BASE_URL = "prod.britecore.com"
$env:BRITECORE_SDK_CLIENT_ID = "prod_client_id"
$env:BRITECORE_SDK_CLIENT_SECRET = "prod_client_secret"
$env:target_site = "example_site"  # required; value only matters if .secrets.toml is also used

# Then start your application
python app.py
```

#### API-only deployment checklist

- Install base package only (`pip install -e .`); do not install optional extras unless needed.
- Set `target_site` to a configured site section in `settings.toml`/`.secrets.toml`, or any non-empty string when all credentials are supplied via `BRITECORE_SDK_*` env vars.
- Set `BRITECORE_SDK_BASE_URL` for the target BriteCore instance.
- Choose one auth mode: either set `BRITECORE_SDK_API_KEY`, or set both `BRITECORE_SDK_CLIENT_ID` and `BRITECORE_SDK_CLIENT_SECRET`.
- Store production secrets in a secrets manager (Vault, AWS Secrets Manager, etc.), not in committed files.
- Verify startup with a minimal init check (`get_api_client()`) before serving traffic. Use `BritecoreAPIClient(...).init_client()` only for advanced/manual scenarios.

## Troubleshooting

### "Config not loading" or "Key not found"

1. Verify `target_site` is set via one of these methods:

   - **`settings.toml`** (recommended for persistent setup):

     ```toml
     [default]
     target_site = "example_site"
     ```

   - **Environment variable**:

     ```powershell
     $env:target_site
     ```

     Should output your site name (e.g., `example_site`)

   - **Explicit argument** in code:

     ```python
     init_api_client(target_site="example_site")
     ```

2. Check `.secrets.toml` has the site section with required auth keys:

   ```powershell
   Select-String -Path "src/britecore_sdk/settings/.secrets.toml" -Pattern "\[example_site\]"
   ```

3. Check `.secrets.toml` exists and has values:

   ```powershell
   Get-Content "src/britecore_sdk/settings/.secrets.toml"
   ```

4. Test config loading directly:

   ```python
   from britecore_sdk.settings.config import LoadClientSettings

   settings = LoadClientSettings("example_site")
   print(settings)  # Should show loaded config
   ```

### Auth failures

1. Verify credentials in `.secrets.toml`:
   - For API key: `api_key` is set
   - For OAuth: both `client_id` and `client_secret` are set

2. Verify `base_url` matches the BriteCore instance:

   ```python
   from britecore_sdk import get_api_client
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

## See Also

- [GETTING_STARTED.md](../GETTING_STARTED.md) -- Quick setup guide
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) -- Common errors
- [AGENTS.md](../AGENTS.md) -- Maintainer source-of-truth policies
- [src/britecore_sdk/settings/config.py](../src/britecore_sdk/settings/config.py) -- Config loader implementation
