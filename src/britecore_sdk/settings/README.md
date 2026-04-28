# Configuration Files Guide

This directory contains the BriteCore SDK configuration files and examples.

## Files

### `settings.toml` (and `settings.toml.example`)

**Purpose:** Non-sensitive, site-specific configuration

**Should contain:**

- HTTP timeout settings (`web_timeout`, `web_timeout_long`, `web_retry`)
- Target site selection (`target_site`)
- Per-site timeout overrides

**Safe to commit:** ✅ YES (contains no secrets)

**Repository workflow note:** This repo uses `fileshare-settings` as a fileshare-only branch for `settings.toml` updates that should not be pushed to GitHub.

**Example:**

```toml
[default]
web_timeout = 10
target_site = 'production'

[production]
web_timeout = 30
```

### `.secrets.toml` (and `.secrets.toml.example`)

**Purpose:** Sensitive credentials for API authentication

**Should contain:**

- API base URLs (`base_url`)
- OAuth credentials (`client_id`, `client_secret`)
- API keys (`api_key`)

**Safe to commit:** ❌ NO (contains sensitive credentials)

**Note:** `.secrets.toml` is in `.gitignore` and will not be version controlled in standard branches. If you intentionally use the fileshare-only branch workflow, keep pushes scoped to `fileshare` only.

**Example:**

```toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your-client-id"
client_secret = "your-client-secret"
```

## Fileshare-Only Sync Workflow

Use these commands from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-git-hooks.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\sync-fileshare-settings.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File .\scripts\sync-fileshare-settings.ps1
```

- `.githooks/pre-push` blocks pushes of `fileshare-settings` to `origin`.
- `scripts/sync-fileshare-settings.ps1` force-adds `settings.toml` and `.secrets.toml` into `fileshare-settings` and pushes only to `fileshare`.

## Quick Setup

### 1. Create Your Configuration Files

**PowerShell:**

```powershell
Copy-Item settings.toml.example settings.toml
Copy-Item .secrets.toml.example .secrets.toml
```

**Bash:**

```bash
cp settings.toml.example settings.toml
cp .secrets.toml.example .secrets.toml
```

### 2. Edit `.secrets.toml`

Replace placeholder values with your actual BriteCore API credentials:

```toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your-actual-client-id"
client_secret = "your-actual-client-secret"
```

### 3. Customize `settings.toml` (Optional)

Override any default timeouts or site selection:

```toml
[default]
web_timeout = 15      # Override default 5 seconds
web_retry = 3         # Override default 5 retries
target_site = 'production'
```

### 4. Verify Your Configuration

**PowerShell:**

```powershell
python -m britecore_sdk.utils.check_site_configs
```

**Bash:**

```bash
python -m britecore_sdk.utils.check_site_configs
```

## Configuration Defaults

The SDK applies sensible defaults when settings are not provided:

| Setting | Default |
|---------|---------|
| `web_timeout` | 5 seconds |
| `web_retry` | 5 retries |
| `web_timeout_long` | 50 seconds (10x `web_timeout`) |

Override any of these by setting them in `settings.toml`.

## Authentication Modes

### OAuth Authentication

Requires both `client_id` and `client_secret`:

```toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your-client-id"
client_secret = "your-client-secret"
```

### API Key Authentication

Requires only `api_key`:

```toml
[staging]
base_url = "https://staging-api.britecore.example.com"
api_key = "your-api-key"
```

## Environment Variables

You can override any setting with an environment variable:

**PowerShell:**

```powershell
# Override target_site
$env:target_site = "production"

# Override HTTP timeout
$env:BRITECORE_SDK_WEB_TIMEOUT = "20"
```

**Bash:**

```bash
# Override target_site
export target_site="production"

# Override HTTP timeout
export BRITECORE_SDK_WEB_TIMEOUT=20
```

## Troubleshooting

### "Site not found"

Verify your site is defined in `.secrets.toml`:

**PowerShell:**

```powershell
python -m britecore_sdk.utils.check_site_configs
```

**Bash:**

```bash
python -m britecore_sdk.utils.check_site_configs
```

### "Configuration invalid. Missing: ..."

Ensure all required fields are present for your authentication mode:

- **OAuth:** `base_url`, `client_id`, `client_secret`
- **API Key:** `base_url`, `api_key`

### Secrets visible in logs

Keep log levels at INFO or WARNING in production. DEBUG mode may expose sensitive data.

## Best Practices

1. ✅ **Commit `settings.toml.example`** — Shows structure and non-secret defaults
2. ✅ **Commit `.secrets.toml.example`** — Shows structure with placeholder values
3. ❌ **Never commit `.secrets.toml`** — Contains actual credentials
4. ✅ **Use environment variables for CI/CD** — Inject credentials at runtime
5. ✅ **Use `.gitignore` for `.secrets.toml`** — Prevent accidental commits (already configured)

## More Information

- See [CONFIG_MANAGEMENT.md](../CONFIG_MANAGEMENT.md) for detailed configuration management
- See [GETTING_STARTED.md](../GETTING_STARTED.md) for first-time setup
- See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for common issues
