"""v2.0.0 Deprecation Notice: britecore_sdk.classes module.

This module has been removed as part of v2.0.0 refactoring. The classes
that were here have been moved to more appropriate locations:

**Migration Guide:**

BEFORE (v1.x - Deprecated):
    from britecore_sdk.classes import Quote
    from britecore_sdk.classes import Contact

AFTER (v2.0.0 - Recommended):
    from britecore_sdk.models import Quote
    from britecore_sdk.models import Contact
    from britecore_sdk.validators import validate_contact
    from britecore_sdk.api.responses import QuoteResponse, ContactResponse

**Key Changes:**
- Domain models moved to `britecore_sdk.models`
- Input validators moved to `britecore_sdk.validators`
- API response models moved to `britecore_sdk.api.responses` (NEW)
- Legacy compatibility helpers available in `britecore_sdk.api._compat`

**Resources:**
- Migration guide: docs/migrations/PHASES2-5-FEATURES.md
- v2.0.0 roadmap: V2_ROADMAP.md
- Deprecation policy: DEPRECATION.md

See these resources for detailed examples and migration patterns.
This module will be removed entirely in v3.0.0.
"""

# Provide helpful error message
import sys
from typing import Any

class _DeprecatedModuleError:
    """Raise helpful error when trying to import from removed module."""

    def __getattr__(self, name: str) -> Any:
        raise ImportError(
            f"britecore_sdk.classes.{name} has been removed.\n\n"
            f"Migration paths:\n"
            f"  - Domain models: from britecore_sdk.models import {name}\n"
            f"  - API responses: from britecore_sdk.api.responses import {name}Response\n"
            f"  - Validators: from britecore_sdk.validators import validate_*\n\n"
            f"See docs/migrations/PHASES2-5-FEATURES.md for full migration guide."
        )

# Replace this module with error raiser
sys.modules[__name__] = _DeprecatedModuleError()  # type: ignore[assignment]

