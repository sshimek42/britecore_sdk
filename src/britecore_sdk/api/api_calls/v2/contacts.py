"""BriteCore v2 Contacts API endpoint wrappers.

This module provides wrappers for contact creation, updates, role assignment,
lookup by identifier, and filtered contact search.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from logging import Logger
from typing import Any, Literal, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.models.contact import ROLETYPES

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def new_contact(
    name: str,
    address: list[dict[str, str]],
    phone: list[dict[str, str] | None] | None = None,
    email: list[dict[str, str] | None] | None = None,
    contact_type: Literal["individual", "organization"] | None = "individual",
    **kwargs: Unpack[RequestParameters],
) -> tuple[str | None, str | None]:
    """Create a contact record.

    This wrapper sends the contact name, addresses, optional phone and email
    lists, and ``contact_type`` to ``/api/v2/contacts/new_contact``. It returns
    the normalized ``process_result(...)`` payload together with the extracted
    ``contact_id`` as an SDK-specific convenience tuple of
    ``(contact_data, contact_id)``. ``**kwargs`` accepts ``RequestParameters``
    overrides.

    Raises:
        BritecoreError.MissingParameter: If name or address is missing.
    """
    # Validate required parameters
    if not name or not name.strip():
        raise BritecoreError.MissingParameter("contact name is required")
    if not address or len(address) == 0:
        raise BritecoreError.MissingParameter("contact address list is required")

    LOGGER.debug("Creating contact '%s'", name)
    if not phone:
        phone = [{}]
    if not email:
        email = [{}]
    contact_request_json: dict[str, Any] = {
        "name": name,
        "addresses": address,
    }
    if email[0] != {}:
        contact_request_json.update({"emails": email})
    if phone[0] != {}:
        contact_request_json.update({"phones": phone})

    contact_request_json.update({"type": contact_type})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/new_contact", json=contact_request_json, **kwargs
    )

    contact_json: Any = API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/new_contact"
    )

    try:
        new_id = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id = "Fail"

    if new_id == "Fail":
        LOGGER.error("Failed to add contact - '%s'", name)
        return None, None

    LOGGER.debug("Added '%s'", name)
    return contact_json, new_id


def add_contact_to_role(
    contact_id: str,
    role: ROLETYPES | None = "Named Insured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Assign an existing contact to a role.

    This wrapper sends ``contact_id`` and ``role`` to
    ``/api/v2/contacts/add_contact_to_role`` and returns the normalized
    ``process_result(...)`` payload for the role-assignment request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.

    Raises:
        BritecoreError.MissingParameter: If contact_id is missing.
    """
    # Validate required parameters
    if not contact_id or not contact_id.strip():
        raise BritecoreError.MissingParameter("contact_id is required")

    LOGGER.debug("Adding role '%s' to '%s'", role, contact_id)
    role_request_json: dict[str, str | ROLETYPES | None] = {
        "contact_id": contact_id,
        "role_name": role,
    }
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/add_contact_to_role"
    )


def update_contact(
    contact: dict[str, str | list[dict[str, str]]], **kwargs: Unpack[RequestParameters]
) -> Any:
    """Update an existing contact record.

    This wrapper sends ``contact`` inside the request body to
    ``/api/v2/contacts/update_contact`` and returns the normalized
    ``process_result(...)`` payload for the update request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Updating contact information\n%s", contact)
    update_request_json: dict[str, dict] = {"contact": contact}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/update_contact"
    )


def get_contact(contact_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a contact by identifier.

    This wrapper sends ``contact_id`` to ``/api/v2/contacts/get_contact`` and
    returns the normalized ``process_result(...)`` payload for the matching
    contact record. ``**kwargs`` accepts ``RequestParameters`` overrides.

    Raises:
        BritecoreError.MissingParameter: If contact_id is missing.
    """
    # Validate required parameters
    if not contact_id or not contact_id.strip():
        raise BritecoreError.MissingParameter("contact_id is required")

    LOGGER.debug("Retrieving contact id '%s'", contact_id)
    contact_retrieve_json: dict[str, str] = {"contact_id": contact_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact"
    )


def find_contact_by_params(
    name: str,
    role_name: ROLETYPES | None = None,
    dob: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Search for contacts by name and optional filters.

    This wrapper sends ``name`` together with the optional ``role_name`` and
    ``dob`` filters to ``/api/v2/contacts/find_contact_by_params`` and returns
    the normalized ``process_result(...)`` payload for the contact search.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Finding contact '%s'", name)
    contact_retrieve_json: dict[str, str | ROLETYPES | None] = {
        "name": name,
        "role_name": role_name,
        "dob": dob,
    }
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/find_contact_by_params",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/find_contact_by_params"
    )


def get_contacts_by_ids(
    contact_id_list: list[str], **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve contacts by id.

    This wrapper sends a list of contact IDs to `/api/v2/contacts/get_contacts_by_ids` and returns the normalized
    `process_result(...)` payload for the matching contacts. `**kwargs` accepts `RequestParameters` overrides.

    Parameters
    ----------
    contact_id_list : list of str
        Required. List of Contact ids to retrieve.

    Returns
    -------
    success : bool
        True if successful, false if not
    messages : list of str
        List of human-readable error messages
    data : dict
        Contains contacts keyed by id.
    """
    if (
        not contact_id_list
        or not isinstance(contact_id_list, list)
        or not all(isinstance(x, str) for x in contact_id_list)
    ):
        raise BritecoreError.MissingParameter(
            "contact_id_list (list of str) is required"
        )
    LOGGER.debug("Retrieving contacts by ids: %s", contact_id_list)
    request_json: dict[str, str] = {"contact_id_list": ",".join(contact_id_list)}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contacts_by_ids",
        json=request_json,
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contacts_by_ids"
    )


def create_contacts_batch(
    contacts_json: list[dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many contacts concurrently and return per-item outcomes.

    This helper runs ``new_contact(...)`` in a bounded thread pool so
    high-volume contact creation jobs complete much faster than fully
    serial execution. Each payload dict must include ``name`` and
    ``address`` keys (matching ``new_contact`` parameters).

    Args:
        contacts_json: List of contact payload dicts.  Each dict must contain
            at minimum ``name`` (str) and ``address`` (list[dict]).  Optional
            keys ``phone``, ``email``, and ``contact_type`` are forwarded if
            present.
        max_workers: Maximum concurrent workers.  Defaults to ``5``.
        fail_fast: When ``True``, re-raises the first encountered exception
            and cancels pending futures.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each contact create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list of per-item outcome dicts with keys
              ``index``, ``success``, ``contact_data``, ``contact_id``, ``error``

    Raises:
        BritecoreError.MissingParameter: If ``contacts_json`` is missing/empty.
        ValueError: If ``max_workers`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not contacts_json or not isinstance(contacts_json, list):
        raise BritecoreError.MissingParameter(
            "contacts_json is required and must be a non-empty list"
        )
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    worker_count = min(max_workers, len(contacts_json))
    results: list[dict[str, Any] | None] = [None] * len(contacts_json)

    def _create_one(
        index: int, payload: dict[str, Any]
    ) -> tuple[int, Any, str | None]:
        contact_data, contact_id = new_contact(
            name=payload["name"],
            address=payload["address"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            contact_type=payload.get("contact_type", "individual"),
            **kwargs,
        )
        return index, contact_data, contact_id

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[tuple[int, Any, str | None]], int] = {
            executor.submit(_create_one, idx, payload): idx
            for idx, payload in enumerate(contacts_json)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                result_idx, contact_data, contact_id = future.result()
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "contact_data": contact_data,
                    "contact_id": contact_id,
                    "error": None,
                }
            except Exception as exc:
                if fail_fast:
                    for pending in future_map:
                        pending.cancel()
                    raise
                results[idx] = {
                    "index": idx,
                    "success": False,
                    "contact_data": None,
                    "contact_id": None,
                    "error": str(exc),
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(contacts_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = [
    "new_contact",
    "add_contact_to_role",
    "update_contact",
    "get_contact",
    "find_contact_by_params",
    "get_contacts_by_ids",
    "create_contacts_batch",
]
