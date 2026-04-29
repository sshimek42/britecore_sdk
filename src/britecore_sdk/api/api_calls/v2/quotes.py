"""BriteCore v2 Quotes API endpoint wrappers.

These wrappers cover quote creation and retrieval workflows exposed by the SDK's
current v2 quote surface. The quote paths remain known spec-gap wrappers, so the
docstrings describe the intended API contract first and call out SDK-specific
response normalization where needed.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from logging import Logger
from typing import Any, TypedDict, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


class BatchQuoteCreateResult(TypedDict):
    """Per-item outcome for ``create_full_quotes_batch``."""

    index: int
    success: bool
    quote_data: dict[str, Any] | None
    quote_id: str | None
    error: str | None


def create_full_quote(
    quote_json: dict[str, Any], **kwargs: Unpack[RequestParameters]
) -> tuple[dict[str, Any] | None, str | None]:
    """Create a quote from the supplied quote payload.

    This wrapper submits ``quote_json`` to ``/api/v2/quotes/create_full_quote``
    and normalizes the response through ``process_result(...)``. As an SDK-
    specific convenience, it returns a tuple of ``(quote_data, quote_id)``,
    where ``quote_id`` is extracted from the normalized payload when present.
    ``**kwargs`` accepts ``RequestParameters`` overrides such as timeout,
    headers, or retry settings.

    Raises:
        BritecoreError.MissingParameter: If quote_json is missing or empty.
    """
    # Validate required parameters
    if not quote_json or not isinstance(quote_json, dict):
        raise BritecoreError.MissingParameter(
            "quote_json is required and must be a dict"
        )
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/quotes/create_full_quote", json=quote_json, **kwargs
    )

    json_info: Any = API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/create_full_quote"
    )

    if not json_info:
        return None, None

    return json_info, json_info["id"]


def get_quote(id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a quote by quote identifier.

    This wrapper sends ``id`` to ``/api/v2/quotes/get_quote`` and returns the
    normalized ``process_result(...)`` payload for the requested quote.
    ``**kwargs`` accepts ``RequestParameters`` overrides such as timeout,
    headers, or retry settings.

    Raises:
        BritecoreError.MissingParameter: If id is missing.
    """
    # Validate required parameters
    if not id or not id.strip():
        raise BritecoreError.MissingParameter("quote id is required")
    quote_json: dict[str, str] = {"id": id}

    LOGGER.debug("Getting quote")

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/quotes/get_quote", json=quote_json, **kwargs
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/get_quote"
    )


def create_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many quotes concurrently and return per-item outcomes.

    This helper runs ``create_full_quote(...)`` in a bounded thread pool so
    high-volume quote creation jobs can complete much faster than fully
    serial execution. It returns a stable, index-aligned result list with
    success/error metadata for each submitted payload.

    Args:
        quotes_json: List of quote payload dictionaries.
        max_workers: Maximum concurrent workers. Defaults to ``5``.
        fail_fast: When ``True``, re-raises the first encountered exception and
            cancels pending futures. Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each quote create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted quote payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchQuoteCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``quotes_json`` is missing/empty.
        ValueError: If ``max_workers`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not quotes_json or not isinstance(quotes_json, list):
        raise BritecoreError.MissingParameter(
            "quotes_json is required and must be a non-empty list"
        )
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    worker_count = min(max_workers, len(quotes_json))
    results: list[BatchQuoteCreateResult | None] = [None] * len(quotes_json)

    def _create_one(
        index: int, payload: dict[str, Any]
    ) -> tuple[int, dict[str, Any] | None, str | None]:
        quote_data, quote_id = create_full_quote(payload, **kwargs)
        return index, quote_data, quote_id

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[tuple[int, dict[str, Any] | None, str | None]], int] = {
            executor.submit(_create_one, idx, payload): idx
            for idx, payload in enumerate(quotes_json)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                result_idx, quote_data, quote_id = future.result()
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "quote_data": quote_data,
                    "quote_id": quote_id,
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
                    "quote_data": None,
                    "quote_id": None,
                    "error": str(exc),
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(quotes_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = ["create_full_quote", "create_full_quotes_batch", "get_quote"]
