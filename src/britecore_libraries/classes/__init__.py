
"""
Deprecated: Classes module.

This module is maintained for backward compatibility.
New code should import from britecore_libraries.models and britecore_libraries.validators.
"""

import warnings

# Import from new locations
from britecore_libraries.models import BritecoreContact, BritecorePolicy
from britecore_libraries.validators import (
    AddressValidator as BritecoreAddress,
    EmailValidator as BritecoreEmail,
    PhoneValidator as BritecorePhone,
)
from britecore_libraries.exceptions import BritecoreError

warnings.warn(
    "Importing from britecore_libraries.classes is deprecated. "
    "Use britecore_libraries.models and britecore_libraries.validators instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "BritecoreContact",
    "BritecorePolicy",
    "BritecoreAddress",
    "BritecoreEmail",
    "BritecorePhone",
    "BritecoreError",
]