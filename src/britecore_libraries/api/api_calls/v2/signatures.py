"""BriteCore v2 Signatures API endpoint wrappers.

Provides:
    docusign_auth       -- Perform a DocuSign authentication action.
    docusign_config     -- Retrieve or set DocuSign configuration.
    get_signatures      -- Retrieve signatures for a revision.
    recreate_envelope   -- Recreate a DocuSign envelope for a revision.
    update_signatures   -- Update signature records for an envelope.
    void_envelope       -- Void a DocuSign envelope.
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

    Parameters
    ----------
    action : Any, optional
        The authentication action to perform (e.g. ``"login"``).
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing auth result or redirect URL.
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
    """Retrieve or update the DocuSign integration configuration.

    Parameters
    ----------
    data : Any, optional
        Configuration data object to set. Omit to retrieve current config.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing DocuSign configuration.
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
    """Retrieve signature records for a policy revision.

    Parameters
    ----------
    revision_id : Any, optional
        UUID of the policy revision whose signatures to retrieve.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the signature records.
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
    """Recreate a DocuSign envelope for a policy revision.

    Parameters
    ----------
    revision_id : Any, optional
        UUID of the policy revision for which to recreate the envelope.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the new envelope details.
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
    """Update signature records for a DocuSign envelope.

    Parameters
    ----------
    envelope_id : str, optional
        ID of the DocuSign envelope to update.
    signers : str, optional
        Serialized signer information to apply.
    status : str, optional
        New status value for the signature records.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the update.
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

    Parameters
    ----------
    envelope_id : Any, optional
        ID of the DocuSign envelope to void.
    revision_id : Any, optional
        UUID of the associated policy revision.
    void_reason : Any, optional
        Reason for voiding the envelope.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the void operation.
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
