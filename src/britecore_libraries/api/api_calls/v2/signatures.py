"""BriteCore v2 Signatures API endpoint wrappers.

This module provides wrappers for DocuSign authentication, configuration,
signature retrieval, envelope recreation, and envelope status updates.
"""

from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a signatures request and normalize the response."""
    LOGGER.debug("Calling signatures endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def docusign_auth(
    action: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Perform a DocuSign authentication action.

    This wrapper sends ``action`` to ``/api/v2/signatures/docusign_auth`` and
    returns the normalized ``process_result(...)`` payload for the DocuSign
    authentication workflow. ``**kwargs`` accepts ``RequestParameters``
    overrides.
    """
    return _post(
        "/api/v2/signatures/docusign_auth",
        _build_payload(action=action),
        **kwargs,
    )


def docusign_config(
    data: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve or update DocuSign configuration.

    This wrapper sends the optional ``data`` payload to
    ``/api/v2/signatures/docusign_config`` and returns the normalized
    ``process_result(...)`` payload for the DocuSign configuration record.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/signatures/docusign_config",
        _build_payload(data=data),
        **kwargs,
    )


def get_signatures(
    revision_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve signature records for a revision.

    This wrapper sends ``revision_id`` to ``/api/v2/signatures/get_signatures``
    and returns the normalized ``process_result(...)`` payload for the matching
    signature records. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/signatures/get_signatures",
        _build_payload(revision_id=revision_id),
        **kwargs,
    )


def recreate_envelope(
    revision_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Recreate a DocuSign envelope for a revision.

    This wrapper sends ``revision_id`` to
    ``/api/v2/signatures/recreate_envelope`` and returns the normalized
    ``process_result(...)`` payload for the recreated envelope.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/signatures/recreate_envelope",
        _build_payload(revision_id=revision_id),
        **kwargs,
    )


def update_signatures(
    envelope_id: str | None = None,
    signers: str | None = None,
    status: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update signature records for an envelope.

    This wrapper sends ``envelope_id``, ``signers``, and ``status`` to
    ``/api/v2/signatures/update_signatures`` and returns the normalized
    ``process_result(...)`` payload for the update request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/signatures/update_signatures",
        _build_payload(envelope_id=envelope_id, signers=signers, status=status),
        **kwargs,
    )


def void_envelope(
    envelope_id: Any | None = None,
    revision_id: Any | None = None,
    void_reason: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Void a DocuSign envelope.

    This wrapper sends the envelope identifier, optional revision identifier,
    and optional ``void_reason`` to ``/api/v2/signatures/void_envelope`` and
    returns the normalized ``process_result(...)`` payload for the void
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    payload: dict[str, Any] = {}
    if envelope_id is not None:
        payload["envelopeId"] = envelope_id
    if revision_id is not None:
        payload["revisionId"] = revision_id
    if void_reason is not None:
        payload["voidReason"] = void_reason
    return _post("/api/v2/signatures/void_envelope", payload, **kwargs)


__all__ = [
    "docusign_auth",
    "docusign_config",
    "get_signatures",
    "recreate_envelope",
    "update_signatures",
    "void_envelope",
]
