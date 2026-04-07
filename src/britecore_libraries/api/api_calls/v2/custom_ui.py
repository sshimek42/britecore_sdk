"""Compatibility exports for v1 Custom UI endpoints.

Canonical implementations for /api/v1/custom_ui/* live in
`britecore_libraries.api.api_calls.v1.custom_ui`.
"""

from britecore_libraries.api.api_calls.v1.custom_ui import (
    createurloverride,
    deleteurloverride,
    retrieveurloverrides,
    updateurloverride,
)

__all__ = [
    "createurloverride",
    "deleteurloverride",
    "retrieveurloverrides",
    "updateurloverride",
]
