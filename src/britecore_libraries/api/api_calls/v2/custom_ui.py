"""Compatibility wrappers for v1 Custom UI endpoints.

Canonical implementations for ``/api/v1/custom_ui/*`` live in
``britecore_libraries.api.api_calls.v1.custom_ui``.
"""

from typing import Any, Unpack

from britecore_libraries.api.api_calls import RequestParameters
from britecore_libraries.api.api_calls.v1 import custom_ui as _v1_custom_ui


def createurloverride(
    json_obj: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/custom_ui/createURLOverride``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_custom_ui.createurloverride(json_obj=json_obj, **kwargs)


def deleteurloverride(
    json_obj: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/custom_ui/deleteURLOverride``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_custom_ui.deleteurloverride(json_obj=json_obj, **kwargs)


def retrieveurloverrides(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/custom_ui/retrieveURLOverrides``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_custom_ui.retrieveurloverrides(**kwargs)


def updateurloverride(
    json_obj: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/custom_ui/updateURLOverride``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_custom_ui.updateurloverride(json_obj=json_obj, **kwargs)

__all__ = [
    "createurloverride",
    "deleteurloverride",
    "retrieveurloverrides",
    "updateurloverride",
]
