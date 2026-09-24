# Environment Update Script

**Filename:** `scripts/update_environment.ps1`

A comprehensive PowerShell script for keeping your development environment, Python, `uv`, and project dependencies up to date.

## Quick Start

### Simple Mode (Recommended for most users)
```powershell
.\scripts\update_environment.ps1
```

This will:
- Verify `uv` and Python are installed
- Sync dependencies from `pyproject.toml`
- Run the test suite to validate the update
- Show a summary report

### Advanced Mode (For maintenance and audits)
```powershell
.\scripts\update_environment.ps1 -Advanced
```

This will additionally:
- Update `uv` to the latest version (`uv self update`)
- Upgrade all dependencies to latest compatible versions (`uv sync --upgrade`)
- Run security audit (`pip-audit`) to check for CVEs
- Run full test suite
- Generate detailed compatibility report

## Usage Examples

### Most Common: Just update and test
```powershell
.\scripts\update_environment.ps1
```

### Skip tests (faster, for quick checks)
```powershell
.\scripts\update_environment.ps1 -SkipTests
```

### Full maintenance mode with security audit
```powershell
.\scripts\update_environment.ps1 -Advanced -SecurityAudit
```

### Dry run (see what would happen without making changes)
```powershell
.\scripts\update_environment.ps1 -Advanced -DryRun
```

### Advanced mode without security audit
```powershell
.\scripts\update_environment.ps1 -Advanced
```

## All Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-Advanced` | switch | Enable advanced mode: update `uv`, upgrade dependencies, run security audit |
| `-SkipTests` | switch | Skip running pytest suite (faster but less safe) |
| `-SecurityAudit` | switch | Force security audit even in simple mode |
| `-DryRun` | switch | Show what would happen without making changes |
| `-PythonVersion` | string | (reserved for future use) Specify Python version |

## What It Checks

### Prerequisites
✓ `uv` is installed and accessible  
✓ `python` is installed and accessible  

### Python Version
✓ Python 3.11 or higher (required by the project)  
✓ Warns if using unsupported versions (not in 3.11-3.14)  

### Dependencies
- Syncs `pyproject.toml` dependencies into virtual environment
- In advanced mode: upgrades to latest compatible versions

### Security (Advanced Mode)
- Runs `pip-audit` to detect known CVEs
- Reports vulnerable packages and available fixes

### Tests
- Runs full pytest suite to validate environment
- Skippable with `-SkipTests` for quick checks

## Output Format

The script provides:
- **Colored output** for easy scanning (Green ✓, Yellow ⚠, Red ✗)
- **Progress indicators** showing each step
- **Summary report** at the end with versions and timing
- **Next steps** suggestions for additional maintenance

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - environment is up to date and tests pass |
| 1 | Error - prerequisites missing, update failed, or tests failed |

## Workflow Examples

### Daily Development
```powershell
# Quick check (skip tests for speed)
.\scripts\update_environment.ps1 -SkipTests
```

### Before Committing
```powershell
# Full validation
.\scripts\update_environment.ps1
```

### Weekly Maintenance
```powershell
# Comprehensive update with security check
.\scripts\update_environment.ps1 -Advanced
```

### Monthly Security Audit
```powershell
# Full update + security scan
.\scripts\update_environment.ps1 -Advanced -SecurityAudit
```

### Planning Upgrades
```powershell
# See what would change without applying
.\scripts\update_environment.ps1 -Advanced -DryRun
```

## Troubleshooting

### "uv is not installed"
Install `uv`: https://docs.astral.sh/uv/
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### "python is not installed"
Install Python 3.11+: https://www.python.org/downloads/

### Tests fail after update
This usually means a dependency update introduced a breaking change:
```powershell
# Revert to last known good state
.\scripts\rebuild_uv_env.ps1
```

### "pip-audit not found"
Ensure you have the dev dependencies installed:
```powershell
uv sync --extra dev
```

## Related Scripts

- **`rebuild_uv_env.ps1`** — Completely rebuild virtual environment from scratch
- **`clean.ps1`** — Clean build artifacts and cache files

## See Also

- [GETTING_STARTED.md](../GETTING_STARTED.md) — Initial setup
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) — Common issues
- [PYTHON_COMPATIBILITY.md](../PYTHON_COMPATIBILITY.md) — Supported versions

