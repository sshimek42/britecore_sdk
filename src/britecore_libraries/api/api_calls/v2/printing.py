"""Compatibility wrappers for v1 Printing endpoints.

Canonical implementations for ``/api/v1/printing/*`` live in
``britecore_libraries.api.api_calls.v1.printing``.
"""

from typing import Any, Unpack

from britecore_libraries.api.api_calls import RequestParameters
from britecore_libraries.api.api_calls.v1 import printing as _v1_printing


def getattachment(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/printing/getAttachment``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_printing.getattachment(json_dict=json_dict, **kwargs)


def gettobeprinted(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/printing/getToBePrinted``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_printing.gettobeprinted(json_dict=json_dict, **kwargs)


def markasprinted(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/printing/markAsPrinted``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_printing.markasprinted(json_dict=json_dict, **kwargs)


def sendprinthawk(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/printing/sendPrinthawk``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_printing.sendprinthawk(json_dict=json_dict, **kwargs)


def sendprinthawkemail(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/printing/sendPrinthawkEmail``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_printing.sendprinthawkemail(**kwargs)


__all__ = [
    "getattachment",
    "gettobeprinted",
    "markasprinted",
    "sendprinthawk",
    "sendprinthawkemail",
]
