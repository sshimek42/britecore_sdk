"""BriteCore v2 Return Premium API endpoint wrappers.

Provides:
    exportreturnpremium  -- Export a return premium record by ID.
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
    """Send a return_premium request and normalize the response."""
    LOGGER.debug("Calling return_premium endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def exportreturnpremium(
    return_premium_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Export a return premium record.

    Parameters
    ----------
    return_premium_id : str, optional
        UUID of the return premium record to export.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the exported return premium data.
    """
    payload: dict[str, Any] = {}
    if return_premium_id is not None:
        payload["returnPremiumId"] = return_premium_id
    return _post(
        "/api/v2/return_premium/exportReturnPremium",
        payload,
        **kwargs,
    )


__all__ = [
    "exportreturnpremium",
]
