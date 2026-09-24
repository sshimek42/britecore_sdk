# Available Scripts - Environment Management

## Overview

The `scripts/` directory includes maintenance and automation scripts. Here are the key ones for environment management:

## Scripts Summary

| Script | Platform | Purpose | Usage |
|--------|----------|---------|-------|
| **`update_environment.ps1`** | Windows | Automated dependency and environment updates | `.\scripts\update_environment.ps1` |
| **`update_environment.sh`** | macOS/Linux | Automated dependency and environment updates | `./scripts/update_environment.sh` |
| **`rebuild_uv_env.ps1`** | Windows | Complete venv rebuild from scratch | `.\scripts\rebuild_uv_env.ps1` |
| **`clean.ps1`** | Windows | Clean build artifacts and cache | `.\scripts\clean.ps1` |

## Update Environment Script

### Quick Commands

**Windows (PowerShell):**
```powershell
# Simple mode: sync deps + test
.\scripts\update_environment.ps1

# Advanced: update tools + upgrade deps + security audit
.\scripts\update_environment.ps1 -Advanced

# Preview without changes
.\scripts\update_environment.ps1 -Advanced -DryRun

# Skip tests (faster)
.\scripts\update_environment.ps1 -SkipTests
```

**macOS/Linux (Bash):**
```bash
# Simple mode: sync deps + test
./scripts/update_environment.sh

# Advanced: update tools + upgrade deps + security audit
./scripts/update_environment.sh --advanced

# Preview without changes
./scripts/update_environment.sh --advanced --dry-run

# Skip tests (faster)
./scripts/update_environment.sh --skip-tests
```

### What It Does

**Simple Mode** (Default)
- ✓ Verifies prerequisites (uv, Python)
- ✓ Validates Python 3.11+ compatibility
- ✓ Syncs dependencies from `pyproject.toml`
- ✓ Runs test suite
- ✓ Reports results

**Advanced Mode** (`-Advanced`)
- ✓ Everything in simple mode, plus:
- ✓ Updates uv to latest version
- ✓ Upgrades all dependencies
- ✓ Runs security audit (pip-audit)
- ✓ Detailed compatibility report

### Documentation

- **Full Reference:** `scripts/UPDATE_ENVIRONMENT.md`
- **Quick Reference:** `scripts/UPDATE_ENVIRONMENT_QUICK_REF.md`
- **Setup Complete:** `scripts/SETUP_COMPLETE.md`

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - environment updated and tests passed |
| 1 | Error - see output for details |

## Recommended Workflows

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

### Planning Major Updates
```powershell
# See what would change without applying
.\scripts\update_environment.ps1 -Advanced -DryRun
```

## Scheduling

To run updates automatically:

**Windows Task Scheduler:**
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -File path\to\update_environment.ps1 -Advanced"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 09:00
Register-ScheduledTask -TaskName "SDK-Weekly-Update" -Action $action -Trigger $trigger
```

**Linux/macOS Cron:**
```bash
# Run weekly on Monday at 9 AM
0 9 * * 1 /path/to/update_environment.sh --advanced
```

## Related Documentation

- [GETTING_STARTED.md](../GETTING_STARTED.md) - Initial setup
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Common issues
- [PYTHON_COMPATIBILITY.md](../PYTHON_COMPATIBILITY.md) - Supported versions
- [pyproject.toml](../pyproject.toml) - Dependency definitions
