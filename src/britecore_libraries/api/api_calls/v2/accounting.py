"""BriteCore v2 Accounting API endpoint wrappers.

This module provides wrappers for accounting deliverables, invoice retrieval,
and rescind-cancellation workflow helpers in the BriteCore v2 accounting API.
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


def get_accounting_deliverable(
    account_history_id: str,
    deliverable_date: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve accounting deliverable values for an account history entry.

    This wrapper sends ``account_history_id`` and ``deliverable_date`` to
    ``/api/v2/accounting/get_accounting_deliverable`` and returns the
    normalized ``process_result(...)`` payload for the requested deliverable
    data. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug(
        "Getting accounting deliverable for account_history_id=%s", account_history_id
    )

    request_json: dict[str, str] = {
        "account_history_id": account_history_id,
        "deliverable_date": deliverable_date,
    }

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/accounting/get_accounting_deliverable",
        json=request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(cast(Any, request_result))


def get_invoices(
    policy_id: str | None = None,
    bill_from_date: str | None = None,
    bill_to_date: str | None = None,
    due_from_date: str | None = None,
    due_to_date: str | None = None,
    sorting_order: str | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve invoices with optional policy and date filters.

    This wrapper sends the supplied policy, bill-date, due-date, sorting, and
    pagination fields to ``/api/v2/accounting/get_invoices`` and returns the
    normalized ``process_result(...)`` payload for the invoice query.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/accounting/get_invoices",
        json=request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(cast(Any, request_result))


def run_rescind_underwriting_cancellation_pending_logic(
    revision_id: str,
    old_status: str,
    date_cursor: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Run rescind underwriting cancellation-pending logic for a revision.

    This wrapper sends ``revision_id``, ``old_status``, and the optional
    ``date_cursor`` to
    ``/api/v2/accounting/run_rescind_underwriting_cancellation_pending_logic``
    and returns the normalized ``process_result(...)`` payload for the job
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
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
