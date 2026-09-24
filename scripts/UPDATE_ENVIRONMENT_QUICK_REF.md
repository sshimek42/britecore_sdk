# Update Environment Script - Quick Reference

## For Windows (PowerShell)

```powershell
# Simple mode - recommended for daily use
.\scripts\update_environment.ps1

# With specific options
.\scripts\update_environment.ps1 -SkipTests          # Faster, no test run
.\scripts\update_environment.ps1 -Advanced           # Full update + audit
.\scripts\update_environment.ps1 -Advanced -DryRun   # Preview without changes
```

---

## For macOS/Linux (Bash)

```bash
# Simple mode - recommended for daily use
./scripts/update_environment.sh

# With specific options
./scripts/update_environment.sh --skip-tests        # Faster, no test run
./scripts/update_environment.sh --advanced          # Full update + audit
./scripts/update_environment.sh --advanced --dry-run # Preview without changes
```

---

## What Each Option Does

| Option | Purpose | When to Use |
|--------|---------|------------|
| (none) | Sync deps + run tests | Daily development |
| `-SkipTests` / `--skip-tests` | Skip test suite | Quick checks, debugging |
| `-Advanced` / `--advanced` | Update uv, upgrade deps, security audit | Weekly maintenance |
| `-SecurityAudit` / `--security-audit` | Force security scan | After major updates |
| `-DryRun` / `--dry-run` | Show what would happen | Before committing to changes |

---

## Common Workflows

### Morning - Quick Check
```powershell
# Make sure everything still works
.\scripts\update_environment.ps1 -SkipTests
```

### Before Committing
```powershell
# Full validation
.\scripts\update_environment.ps1
```

### Weekly Maintenance
```powershell
# Comprehensive update
.\scripts\update_environment.ps1 -Advanced
```

### Planning Upgrades
```powershell
# See what would change
.\scripts\update_environment.ps1 -Advanced -DryRun
```

### Emergency - Rebuild from Scratch
```powershell
# Use this if update script fails
.\scripts\rebuild_uv_env.ps1
```

---

## Troubleshooting

**"uv is not installed"**
→ Install uv: https://docs.astral.sh/uv/

**"Python version too old"**
→ Update Python to 3.11+

**"Test failures after update"**
→ Revert with: `.\scripts\rebuild_uv_env.ps1`

**"Access denied" errors**
→ Make sure you're not in the `.venv` directory. Exit and try again.

---

## Full Documentation

See `scripts/UPDATE_ENVIRONMENT.md` for complete reference.

