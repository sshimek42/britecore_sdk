# v1.1.0 Migration: SCLogging → Built-in Python Logging

**Date:** April 6, 2026  
**Status:** ✅ Complete

## What Changed

### Removed Dependencies
- **Removed:** `sclogging==1.3.1` from `pyproject.toml`
- **Replaced with:** Python's built-in `logging` module (standard library)

### Files Modified

1. **`src/britecore_libraries/base_logger.py`**
   - Replaced `SCLogger` Singleton class with `get_logger()` function
   - Now returns a standard `logging.Logger` instance
   - Configures console + file handlers with sensible defaults
   - Log files written to `~/.britecore_logs/{package_name}.log`

2. **`src/britecore_libraries/__init__.py`**
   - Changed: `SCLogger` import → `get_logger` function
   - Updated logger initialization
   - Exposed logger as `logger` (unchanged API)

3. **`pyproject.toml`**
   - Version bumped: 1.0.0 → 1.1.0
   - Removed `sclogging==1.3.1` dependency

4. **`AGENTS.md`**
   - Added "Logging" section with best practices
   - Documented standard Python logging usage
   - Updated gotchas section

## API Compatibility

✅ **No breaking changes** — The exposed logger API is identical:

```python
from britecore_libraries import logger

# All of these work exactly as before:
logger.info("message")
logger.debug("debug info")
logger.error("error occurred")
logger.warning("warning message")
```

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Dependencies** | 1 external | 0 (stdlib only) |
| **Maintenance burden** | External library (minimal updates) | Python stdlib (battle-tested) |
| **Flexibility** | Limited (code-only config) | Excellent (files + code) |
| **Testing** | Can't use pytest.caplog | Can use pytest.caplog |
| **Ecosystem integration** | No (SCLogging is isolated) | Yes (standard logging hub) |
| **Library best practices** | No | Yes |

## Testing

✅ All 325 tests pass:
```
325 passed, 2 skipped in 8.51s
```

Coverage maintained at 75%.

## Future Work

**None required** — This migration is complete and stable. If future enhancements are needed:
- Can easily integrate with structured logging (structlog, python-json-logger)
- Can add observability tool support (Datadog, New Relic, etc.)
- Can implement log rotation or custom handlers without library changes

## Migration Notes for Users

Users do not need to update their code. The logger interface is unchanged:

### For library users:
```python
# Still works exactly the same
from britecore_libraries import logger
logger.info("Still works!")
```

### For custom logging configuration (optional):
Users can now configure logging via standard Python mechanisms:

```python
import logging

# Configure all britecore_libraries logs to DEBUG
logging.getLogger("britecore_libraries").setLevel(logging.DEBUG)

# Or configure globally
logging.basicConfig(level=logging.INFO, format='...')
```

### Log file location:
- Logs are written to: `~/.britecore_logs/britecore_libraries.log`
- This path can be customized by users via standard logging handlers

## See Also

- [LOGGING_STRATEGY_ANALYSIS.md](LOGGING_STRATEGY_ANALYSIS.md) — Detailed comparison
- [Python logging docs](https://docs.python.org/3/library/logging.html)
- [AGENTS.md](AGENTS.md) — Updated developer guidance

