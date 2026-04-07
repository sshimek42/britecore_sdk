"""Compatibility exports for v1 Printing endpoints.

Canonical implementations for /api/v1/printing/* live in
`britecore_libraries.api.api_calls.v1.printing`.
"""

from britecore_libraries.api.api_calls.v1.printing import (
    getattachment,
    gettobeprinted,
    markasprinted,
    sendprinthawk,
    sendprinthawkemail,
)

__all__ = [
    "getattachment",
    "gettobeprinted",
    "markasprinted",
    "sendprinthawk",
    "sendprinthawkemail",
]
