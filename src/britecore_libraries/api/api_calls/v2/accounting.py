"""BriteCore v2 Accounting API endpoint wrappers.

Provides:
    get_accounting_deliverable                            -- Retrieve values needed to generate account-history deliverables.
    get_invoices                                          -- Retrieve a paginated list of invoices, optionally filtered by policy and date range.
    run_rescind_underwriting_cancellation_pending_logic   -- Run the rescind underwriting cancellation-pending logic for a revision.
"""
from logging import Logger
from typing import Any, Optional, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def get_accounting_deliverable(
    account_history_id: str,
    deliverable_date: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve all values necessary to generate deliverables related to
    the account history in a policy term.

    Parameters
    ----------
    account_history_id : str
        Account history ID from which values are to be filtered.
    deliverable_date : str
        Process date of the deliverable in the format ``YYYY-MM-DD``.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides forwarded to the
        underlying HTTP request.

    Returns
    -------
    Any
        Processed API response.  On success the ``data`` key contains the
        queried values for the deliverable.
    """
    LOGGER.debug("Getting accounting deliverable for account_history_id=%s", account_history_id)

    request_json: dict[str, str] = {
        "account_history_id": account_history_id,
        "deliverable_date": deliverable_date,
    }

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/accounting/get_accounting_deliverable",
        json=request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(cast(Any, request_result))


def get_invoices(
    policy_id: Optional[str] = None,
    bill_from_date: Optional[str] = None,
    bill_to_date: Optional[str] = None,
    due_from_date: Optional[str] = None,
    due_to_date: Optional[str] = None,
    sorting_order: Optional[str] = None,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a paginated list of invoices related to a policy.

    Parameters
    ----------
    policy_id : str, optional
        Filter invoices by policy UUID.
    bill_from_date : str, optional
        Filter invoices with bill date > ``bill_from_date`` (``YYYY-MM-DD``).
    bill_to_date : str, optional
        Filter invoices with bill date < ``bill_to_date`` (``YYYY-MM-DD``).
    due_from_date : str, optional
        Filter invoices with due date > ``due_from_date`` (``YYYY-MM-DD``).
    due_to_date : str, optional
        Filter invoices with due date < ``due_to_date`` (``YYYY-MM-DD``).
    sorting_order : str, optional
        Ascending/descending order.  Choices: ``{'asc', 'desc'}``.
    page_number : int, optional
        Page number, starting from 1.
    page_size : int, optional
        Page size; must be > 0.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides forwarded to the
        underlying HTTP request.

    Returns
    -------
    Any
        Processed API response.  On success the ``data`` key contains the
        paginated invoice list along with filter and pagination metadata.
    """
    LOGGER.debug("Getting invoices for policy_id=%s", policy_id)

    request_json: dict[str, Any] = {}

    if policy_id is not None:
        request_json["policy_id"] = policy_id
    if bill_from_date is not None:
        request_json["bill_from_date"] = bill_from_date
    if bill_to_date is not None:
        request_json["bill_to_date"] = bill_to_date
    if due_from_date is not None:
        request_json["due_from_date"] = due_from_date
    if due_to_date is not None:
        request_json["due_to_date"] = due_to_date
    if sorting_order is not None:
        request_json["sorting_order"] = sorting_order
    if page_number is not None:
        request_json["page_number"] = page_number
    if page_size is not None:
        request_json["page_size"] = page_size

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/accounting/get_invoices",
        json=request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(cast(Any, request_result))


def run_rescind_underwriting_cancellation_pending_logic(
    revision_id: str,
    old_status: str,
    date_cursor: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Run the rescind-underwriting cancellation-pending logic for a revision.

    Parameters
    ----------
    revision_id : str
        UUID of the revision to process.
    old_status : str
        The previous status of the revision before the cancellation-pending
        state was entered.
    date_cursor : str, optional
        Optional date cursor used by the underlying logic (``YYYY-MM-DD``).
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides forwarded to the
        underlying HTTP request.

    Returns
    -------
    Any
        Processed API response indicating success or failure.
    """
    LOGGER.debug(
        "Running rescind underwriting cancellation pending logic for revision_id=%s",
        revision_id,
    )

    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "old_status": old_status,
    }

    if date_cursor is not None:
        request_json["date_cursor"] = date_cursor

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/accounting/run_rescind_underwriting_cancellation_pending_logic",
        json=request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(cast(Any, request_result))


__all__ = [
    "get_accounting_deliverable",
    "get_invoices",
    "run_rescind_underwriting_cancellation_pending_logic",
]
