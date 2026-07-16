"""v2.0.0 Migration Support for Legacy v1 Patterns.

This module provides compatibility helpers and migration tools for users
transitioning from v1.x to v2.0.0. All functionality here is DEPRECATED
and will be removed in v3.0.0.

Use this module ONLY for gradual migration. Prefer v2.0.0 patterns for
all new code.

**Migration Path:**

v1.x (Legacy):
    from britecore_sdk.api.api_calls import init_api_client
    from britecore_sdk.api.api_calls.v2.contacts import get_contact

    init_api_client(target_site="production")
    contact = get_contact(contact_id="123")  # Implicit client

v2.0.0 (Recommended):
    from britecore_sdk import BritecoreAPIClient
    from britecore_sdk.api.api_calls.v2 import contacts

    client = BritecoreAPIClient("production").init_client()
    contact = contacts.get_contact(contact_id="123", client=client)

See PHASES2-5-FEATURES.md and PHASE1-CLIENT-LIFECYCLE.md for migration guides.
"""

import warnings
from typing import Any, Optional

from britecore_sdk import logger

LOGGER = logger


def _warn_deprecated(old_pattern: str, new_pattern: str, version_removed: str = "v3.0.0"):
    """Log deprecation warning for legacy pattern.

    Args:
        old_pattern: v1.x pattern (e.g., "britecore_sdk.classes.Quote")
        new_pattern: v2.0.0 pattern (e.g., "britecore_sdk.models.Quote")
        version_removed: Version when this will be removed
    """
    warnings.warn(
        f"{old_pattern} is deprecated and will be removed in {version_removed}.\n"
        f"Use {new_pattern} instead.\n"
        f"See docs/migrations/PHASES2-5-FEATURES.md for migration guide.",
        DeprecationWarning,
        stacklevel=3,
    )
    LOGGER.warning(
        f"Deprecated v1.x pattern: {old_pattern} → {new_pattern} (removal: {version_removed})"
    )


# ============================================================================
# v1 ENDPOINT ROUTE MAPPING
# ============================================================================

V1_TO_V2_ROUTING = {
    # v1.x endpoint import paths → v2.0.0 replacement
    "britecore_sdk.api.api_calls.v1.contacts.get_contact":
        "britecore_sdk.api.api_calls.v2.contacts.get_contact",
    "britecore_sdk.api.api_calls.v1.policies.retrieve_policy":
        "britecore_sdk.api.api_calls.v2.policies.retrieve_policy",
    "britecore_sdk.api.api_calls.v1.quotes.create_quote":
        "britecore_sdk.api.api_calls.v2.quotes.create_full_quote",
    # Add more mappings as needed
}


def get_v2_path(v1_path: str) -> Optional[str]:
    """Get v2.0.0 import path for v1.x endpoint.

    Args:
        v1_path: v1.x import path (e.g., "britecore_sdk.api.api_calls.v1.contacts.get_contact")

    Returns:
        v2.0.0 import path, or None if no direct replacement

    Example:
        >>> get_v2_path("britecore_sdk.api.api_calls.v1.contacts.get_contact")
        "britecore_sdk.api.api_calls.v2.contacts.get_contact"
    """
    return V1_TO_V2_ROUTING.get(v1_path)


# ============================================================================
# LEGACY IMPORT COMPATIBILITY
# ============================================================================

def import_v1_class_with_warning(class_name: str, module_path: str) -> type:
    """Dynamically import v1.x class with deprecation warning.

    Args:
        class_name: Name of class (e.g., "Quote")
        module_path: v2.0.0 module path (e.g., "britecore_sdk.models")

    Returns:
        The imported class

    Raises:
        ImportError: If class not found in module
    """
    old_path = f"britecore_sdk.classes.{class_name}"
    new_path = f"{module_path}.{class_name}"

    _warn_deprecated(old_path, new_path, version_removed="v3.0.0")

    # Import from v2.0.0 location
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


# ============================================================================
# IMPLICIT CLIENT HELPER (v1.x pattern)
# ============================================================================

def use_implicit_client_with_warning():
    """Helper for v1.x implicit client usage.

    v1.x code often relies on module-level client initialized via init_api_client().
    This warns users to migrate to explicit client parameter pattern.
    """
    _warn_deprecated(
        "Implicit module-level client (v1.x pattern)",
        "Explicit client= parameter (v2.0.0 pattern)",
        version_removed="v3.0.0"
    )


__all__ = [
    "get_v2_path",
    "import_v1_class_with_warning",
    "use_implicit_client_with_warning",
    "_warn_deprecated",
    "V1_TO_V2_ROUTING",
]

