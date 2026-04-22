# Configuration Management Guide

## Overview

The BriteCore SDK provides utilities to safely manage site configurations stored in `.secrets.toml`. This guide covers:

- **Shared validation** (`_config_common.py`) — Constants, validation, and file I/O shared by all tools
- **Diagnostic** (`check_site_configs.py`) — View all sites and their validation status
- **CRUD operations** (`config_manager.py`) — Add, update, delete, and export sites
- **Interactive workflows** (`interactive_menu.py`) — Integrated menu access to all operations

---

## Initial Setup

### 1. Copy Example Files

Two example files are provided to help you get started:

**PowerShell:**

```powershell
Copy-Item src\britecore_sdk\settings\.secrets.toml.example src\britecore_sdk\settings\.secrets.toml
Copy-Item src\britecore_sdk\settings\settings.toml.example src\britecore_sdk\settings\settings.toml
```

**Bash:**

```bash
cp src/britecore_sdk/settings/.secrets.toml.example src/britecore_sdk/settings/.secrets.toml
cp src/britecore_sdk/settings/settings.toml.example src/britecore_sdk/settings/settings.toml
```

### 2. Fill in Your Credentials

Edit `.secrets.toml` and add your actual API credentials:

```toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your-actual-client-id"
client_secret = "your-actual-client-secret"
```

### 3. Customize Settings (Optional)

Edit `settings.toml` to override any default timeouts or site selection:

```toml
[default]
web_timeout = 10          # Increase from default 5 seconds
web_retry = 3             # Decrease from default 5 retries
target_site = 'production'
```

### 4. Verify Your Configuration

```bash
python -m britecore_sdk.utils.check_site_configs
```

---

## Quick Start

### Check your current sites

```bash
python -m britecore_sdk.utils.check_site_configs
```

Output:

```text
Checking API config for 2 site(s) in .../settings/.secrets.toml...

Site                 Status      Auth      URL                                       Missing Keys
----------------------------------------------------------------------------------------------------
production           OK          OAuth     https://api.example.com
staging              INCOMPLETE  -         https://staging-api.example.com           client_id, client_secret, api_key
```

### Open the interactive configuration manager

**PowerShell:**

```powershell
python -c "from britecore_sdk.utils.config_manager import interactive_config_menu; interactive_config_menu()"
```

**Bash:**

```bash
python -c "from britecore_sdk.utils.config_manager import interactive_config_menu; interactive_config_menu()"
```

Or integrate it into your own menu system:

```python
from britecore_sdk.utils.interactive_menu import config_menu
config_menu()
```

---

## Programmatic Usage

### ConfigManager API

```python
from britecore_sdk.utils.config_manager import ConfigManager

# Initialize
manager = ConfigManager()

# List all sites
sites = manager.list_sites(mask_secrets=True)
for site in sites:
    print(f"{site['name']}: {site['status']}")

# Add a new OAuth site
success, msg = manager.add_site(
    "my_prod",
    "https://api.example.com",
    "oauth",
    client_id="abc123",
    client_secret="secret456"
)
print(msg)

# Add an API Key site
success, msg = manager.add_site(
    "my_staging",
    "https://staging.example.com",
    "api_key",
    api_key="key789"
)

# Update an existing site
success, msg = manager.update_site(
    "my_prod",
    base_url="https://new-api.example.com"
)

# Delete a site
success, msg = manager.delete_site("my_prod")

# Export a backup
success, msg = manager.export_backup("/tmp/config.backup.toml")
```

---

## Architecture

### Shared Validation Module (`_config_common.py`)

Provides common constants and functions used across all tools:

```python
from britecore_sdk.utils._config_common import (
    CONFIG_PATH,                      # Path to .secrets.toml
    SETTINGS_PATH,                    # Path to settings.toml
    REQUIRED_KEYS,                    # ["base_url"]
    OAUTH_KEYS,                       # ["client_id", "client_secret"]
    API_KEY,                          # "api_key"
    get_auth_mode(config),            # Determines OAuth vs API Key
    validate_site(site_name, config), # Returns (is_valid, missing_keys)
    load_secrets(path),               # Load TOML with error handling
    save_secrets(path, config),       # Save TOML with backup
    mask_secret(value),               # Mask for display
)
```

**Benefits:**

- Validation logic lives in one place
- Both diagnostic and CRUD tools use the same rules
- Reduces maintenance burden

### Check Site Configs (`check_site_configs.py`)

**Read-only diagnostic tool** — Views all sites and reports missing/incomplete configurations.

**PowerShell:**

```powershell
python -m britecore_sdk.utils.check_site_configs
```

**Bash:**

```bash
python -m britecore_sdk.utils.check_site_configs
```

**Output:**

- Table format showing site name, status, auth mode, URL, and missing keys
- Warnings if sensitive keys are found in `settings.toml` instead of `.secrets.toml`

### Config Manager (`config_manager.py`)

**CRUD tool** — Adds, updates, deletes, and exports site configurations.

**Features:**

- Safe file I/O with automatic timestamped backups
- Validation before persist (catches errors early)
- Masking of secrets in display output
- Reload on error (reverts partial changes)
- Interactive prompts for add/update/delete workflows

**Key methods:**

| Method | Purpose |
|--------|---------|
| `add_site(name, url, auth_type, **creds)` | Add a new site with validation |
| `update_site(name, **updates)` | Merge changes into existing site |
| `delete_site(name)` | Remove a site from config |
| `list_sites(mask_secrets=True)` | List all sites with optional masking |
| `get_site(name)` | Retrieve one site's config |
| `export_backup(path)` | Save config to a new file |

**Interactive menu:**

```python
from britecore_sdk.utils.config_manager import interactive_config_menu
interactive_config_menu()
```

Presents a loop with options to:

1. List sites
2. Add new site (prompts for name, URL, auth type, credentials)
3. Update site (prompts for which fields to change)
4. Delete site (confirms deletion)
5. Export backup
6. Exit

### Interactive Menu Integration (`interactive_menu.py`)

New `config_menu()` function integrates ConfigManager into the main menu system:

```python
from britecore_sdk.utils.interactive_menu import config_menu
config_menu()
```

Can be extended to a larger menu system:

```python
def main_menu():
    while True:
        print("\nMain Menu")
        print("1. Line Selection")
        print("2. Policy Selection")
        print("3. Configuration Management")
        print("4. Exit")

        choice = input("Select: ").strip()
        if choice == "1":
            from britecore_sdk.utils.interactive_menu import line_menu
            line_menu()
        elif choice == "2":
            from britecore_sdk.utils.interactive_menu import policy_menu
            policy_menu()
        elif choice == "3":
            from britecore_sdk.utils.interactive_menu import config_menu
            config_menu()
        elif choice == "4":
            break
        else:
            print("Invalid option")
```

---

## Configuration File Format

The `.secrets.toml` file uses TOML sections, one per site:

```toml
[production]
base_url = "https://api.example.com"
client_id = "your-client-id"
client_secret = "your-client-secret"

[staging]
base_url = "https://staging.example.com"
api_key = "your-api-key"
```

**Required fields per site:**

- `base_url` — API endpoint URL

**Authentication (choose one):**

- OAuth: `client_id` + `client_secret`
- API Key: `api_key`

---

## Validation Rules

Validation checks the following:

1. **Required fields present:**
   - `base_url` must exist and not be empty

2. **Authentication configured (one of):**
   - Both `client_id` AND `client_secret` present (OAuth), OR
   - `api_key` present (API Key)

3. **No incomplete OAuth:**
   - If only one of `client_id` / `client_secret` is provided, the site is invalid

4. **No sensitive data in settings.toml:**
   - A warning is displayed if `api_key`, `client_id`, or `client_secret` appear in `settings.toml`

---

## Configuration Defaults

### Overview

The SDK provides sensible defaults for optional configuration settings. These defaults are applied automatically when a setting is **not** present in `settings.toml` or environment variables.

**Key principle:** Defaults are hard-coded but overridable. You can customize any default by adding it to `settings.toml`.

### Built-in Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `web_timeout` | 5 seconds | Standard HTTP request timeout |
| `web_retry` | 5 retries | Number of retries for failed requests (500, 502, 503, 504) |
| `web_timeout_long` | 50 seconds | Timeout for long-running operations (calculated as 10x `web_timeout`) |

### Overriding Defaults

To override a default, add the setting to `settings.toml` under the `[default]` section:

```toml
[default]
# Override the standard timeout
web_timeout = 10

# Override the retry count
web_retry = 3
```

**Note:** If you set `web_timeout`, `web_timeout_long` is automatically calculated as `web_timeout * 10` (unless you also override `web_timeout_long`).

### Where Defaults Are Applied

Defaults are applied during API client initialization in `BritecoreAPIClient.init_client()`:

```python
from britecore_sdk.api.api_calls import init_api_client

# Initialize with your configured site
client = init_api_client("production")

# If settings.toml doesn't have web_timeout, the default (5 seconds) is used
print(client.web_timeout)  # Output: 5 (or your custom value from settings.toml)
```

### Viewing Available Defaults Interactively

Open the configuration manager and select "View available defaults":

**PowerShell:**

```powershell
python -c "from britecore_sdk.utils.config_manager import interactive_config_menu; interactive_config_menu()"
```

**Bash:**

```bash
python -c "from britecore_sdk.utils.config_manager import interactive_config_menu; interactive_config_menu()"
```

Then select:

- **2. Manage Settings**
- **4. View available defaults**

### Programmatic Access

```python
from britecore_sdk.utils.config_manager import ConfigManager

manager = ConfigManager()
defaults = manager.get_available_defaults()
print(defaults)
# Output: {'web_timeout': 5, 'web_retry': 5, 'web_browser': ''}
```

### Source Code

Defaults are defined in `src/britecore_sdk/settings/defaults.py`:

```python
from britecore_sdk.settings.defaults import DEFAULTS

# {'web_timeout': 5, 'web_retry': 5, 'web_browser': ''}
```

---

## Error Handling

### ConfigManager Safety Features

1. **Validation before save** — All changes are validated before persisting
2. **Automatic backups** — Each save creates a timestamped backup of the old config
3. **Reload on failure** — If save fails, config is reloaded from disk (partial changes reverted)
4. **Masked secrets** — Secrets are masked in display output (only last 4 chars visible)
5. **File permissions** — Backups inherit file permissions from original config

### Example error flow

```python
manager = ConfigManager()

# This fails because OAuth keys are incomplete
success, msg = manager.update_site("prod", client_id="new-id")
print(msg)  # "Configuration invalid after update. Missing: ['client_secret']"

# Config is unchanged (reloaded from disk automatically)
site = manager.get_site("prod")
print(site)  # Still has old client_id, not "new-id"
```

---

## Use Cases

### 1. Add a new environment at deployment time

```python
from britecore_sdk.utils.config_manager import ConfigManager

manager = ConfigManager()
success, msg = manager.add_site(
    "production",
    os.environ["API_URL"],
    "oauth",
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"]
)
if success:
    print("Environment configured successfully")
else:
    print(f"Configuration failed: {msg}")
    exit(1)
```

### 2. Verify all environments before running integration tests

```python
from britecore_sdk.utils.check_site_configs import main
main()  # Prints status of all sites

# Or programmatically
from britecore_sdk.utils.config_manager import ConfigManager
manager = ConfigManager()
sites = manager.list_sites()
all_ok = all(site["status"] == "OK" for site in sites)
if not all_ok:
    print("Some sites are not fully configured")
    exit(1)
```

### 3. Interactive site setup for new users

```python
from britecore_sdk.utils.config_manager import interactive_config_menu
interactive_config_menu()
```

User can add their own environments without editing TOML manually.

### 4. Backup before CI/CD changes

```python
from britecore_sdk.utils.config_manager import ConfigManager
import os

manager = ConfigManager()
backup_path = f"/tmp/config.backup.{os.environ['BUILD_ID']}.toml"
success, msg = manager.export_backup(backup_path)
print(msg)  # "Configuration backed up to /tmp/config.backup.123.toml"
```

---

## Troubleshooting

### "Site not found"

The site doesn't exist in `.secrets.toml`. Check the spelling and list all sites:

**PowerShell:**

```powershell
python -m britecore_sdk.utils.check_site_configs
```

**Bash:**

```bash
python -m britecore_sdk.utils.check_site_configs
```

### "Configuration invalid. Missing: ..."

One or more required fields are missing. Example errors:

- `['base_url']` — Missing API endpoint URL
- `['client_id', 'client_secret']` — OAuth keys incomplete
- `['api_key']` — API Key not provided but OAuth keys also missing

Fix by providing the missing credentials:

```python
manager.update_site("my_site", client_secret="secret_value")
```

### "Failed to save configuration: Permission denied"

The `.secrets.toml` file or its directory is not writable. Check:

**PowerShell:**

```powershell
Get-Item -Path $env:USERPROFILE\.../settings\.secrets.toml | Select-Object FullName, Mode
```

**Bash:**

```bash
ls -la ~/.../settings/.secrets.toml
```

Ensure the file is writable by your user, or run with appropriate permissions.

### Secrets visible in logs

Secrets are masked in ConfigManager output by default. However:

- **Log files** — Ensure log level is not `DEBUG` in production
- **Backups** — Backups contain full credentials; store them securely
- **settings.toml** — NEVER put secrets here; always use `.secrets.toml`

---

## See Also

- `britecore_sdk.utils.check_site_configs` — Diagnostic tool documentation
- `britecore_sdk.settings.config` — Dynaconf configuration loading
- `britecore_sdk.api.britecore_api_client` — API client initialization
