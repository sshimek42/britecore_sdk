"""BriteCore v2 Deliverables API endpoint wrappers.

This module provides wrappers for deliverable attachment lookups and
e-deliverable retrieval in the BriteCore v2 deliverables API.
"""

from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.exceptions import BritecoreError

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client



def list_attachments(
    policy_id: str | None = None,
    revision_id: str | None = None,
    contact_id: str | None = None,
    print_date_from: str | None = None,
    print_date_to: str | None = None,
    print_state_ne: str | None = None,
    print_state: str | None = None,
    order_by: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List deliverable attachments for a policy, contact, or revision.

    This wrapper uses the supplied identifiers and optional print-state/date
    filters to call ``/api/v2/deliverables/list_attachments``. It returns the
    normalized ``process_result(...)`` payload for the attachment query and
    accepts ``RequestParameters`` overrides via ``**kwargs``.
    """
    local_env: dict[str, str | None] = {**locals()}
    if not policy_id and not contact_id and not revision_id:
        BritecoreError.MissingParameter("policy_id, contact_id or revision_id required")

    parameter_list: list[dict[str, str | None]] = [
        {"policy_id": policy_id},
        {"contact_id": contact_id},
        {"revision_id": revision_id},
    ]
    parameter_priority: list[str] = ["revision_id", "contact_id", "policy_id"]

    attachments_search: dict[str, str | None] = (
        api_client.multiple_parameter_verification(parameter_list, parameter_priority)
    )

    for _, (k, v) in enumerate(local_env.items()):
        if v and k not in parameter_priority:
            attachments_search.update({k: v})

    logger.debug("Getting attachments")

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/deliverables/list_attachments",
        json=attachments_search,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/deliverables/list_attachments"
    )


def get_attachment(file_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a deliverable attachment by file identifier.

    This wrapper sends ``file_id`` to ``/api/v2/deliverables/get_attachment``
    and returns the normalized ``process_result(...)`` payload for the matching
    attachment record. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Getting attachment '%s'", file_id)
    file_search: dict[str, str] = {"file_id": file_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/deliverables/get_attachment", json=file_search, **kwargs
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/deliverables/get_attachment"
    )


def get_edeliverables(
    date_from: str,
    date_to: str,
    unprocessed_only: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve e-deliverables for a date range.

    This wrapper sends ``date_from``, ``date_to``, and ``unprocessed_only`` to
    ``/api/v2/deliverables/get_edeliverables`` and returns the normalized
    ``process_result(...)`` payload for the e-deliverable query.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    required_json: dict[str, str | bool | None] = {
        "date_from": date_from,
        "date_to": date_to,
        "unprocessed_only": unprocessed_only,
    }

    LOGGER.debug("Getting E-Deliverables\n%s", required_json)

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/deliverables/get_edeliverables",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)
