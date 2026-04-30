"""BriteCore v2 Async Lines API endpoint wrappers.

Asynchronous counterparts to the synchronous wrappers in lines.py.
Uses AsyncBritecoreAPIClient for non-blocking HTTP requests.

Provides:
    aget_export_line_files_stitched -- Async fetch and stitch line file exports.
"""

import asyncio
from json import loads
from logging import Logger
from typing import Any, Unpack

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    AsyncBritecoreAPIClient,
    RequestParameters,
    async_api_client,
)

LOGGER: Logger = logger

API_CLIENT: AsyncBritecoreAPIClient = async_api_client


async def aget_export_line_file(
    line: tuple,
    include_custom_sequences: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve export-line file data for a single line asynchronously.

    This wrapper sends line identifiers to
    ``/api/v2/lines/get_export_line_file`` asynchronously and returns the
    parsed JSON payload data.

    Args:
        line: Tuple of ``(effective_date_id, state_id, line_id)``.
        include_custom_sequences: Whether to include custom sequences in the
            export.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` overrides.  Consider passing a long
            ``request_timeout`` (e.g., ``120``) as these calls can take
            45–60 seconds.
    """
    LOGGER.info("Retrieving line export for IDs: %s", line)

    web_request_json: dict[str, Any] = {
        "curr_eff_date_id": line[0],
        "curr_line_id": line[2],
        "curr_state_id": line[1],
        "include_custom_sequences": include_custom_sequences,
    }

    request_result = await API_CLIENT.ado_request(
        path="/api/v2/lines/get_export_line_file",
        json={k: v for k, v in web_request_json.items() if v is not None},
        **kwargs,
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for aget_export_line_file")

    LOGGER.info("Finished retrieving line export for IDs: %s", line)

    processed_result = await API_CLIENT.aprocess_result(request_result)
    if processed_result is not None:
        return loads(processed_result)

    return request_result


async def aget_export_line_files_stitched(
    lines: list[tuple],
    max_concurrent: int = 2,
    include_custom_sequences: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Fetch export data for multiple lines asynchronously and stitch the results.

    Line file export calls are **long-running** (typically 45–60 seconds each).
    This helper intentionally defaults to low concurrency (``max_concurrent=2``)
    to avoid overloading the BriteCore backend and to limit timeout failures.
    Callers should pass a generous ``request_timeout`` (e.g., 120–180 seconds)
    via ``**kwargs``.

    The stitched result contains all per-line payloads keyed by line index,
    plus a summary of successes and failures.

    Args:
        lines: List of ``(effective_date_id, state_id, line_id)`` tuples,
            one per line to extract.
        max_concurrent: Maximum concurrent coroutines.  Default is ``2`` (low
            because each extract call is long-running and heavy).
        include_custom_sequences: Whether to include custom sequences in each
            export.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` overrides.  It is strongly recommended
            to pass a long ``request_timeout``::

                await aget_export_line_files_stitched(
                    lines,
                    request_timeout=120,
                )

    Returns:
        dict[str, Any]:
            - ``total``: total number of lines requested
            - ``succeeded``: number of successful extracts
            - ``failed``: number of failed extracts
            - ``results``: list of per-line outcome dicts with keys
              ``index``, ``line``, ``success``, ``data``, ``error``

    Raises:
        BritecoreError.MissingParameter: If ``lines`` is missing/empty.
        ValueError: If ``max_concurrent`` is less than 1.
    """
    if not lines or not isinstance(lines, list):
        raise BritecoreError.MissingParameter(
            "lines is required and must be a non-empty list"
        )
    if max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1")

    results: list[dict[str, Any] | None] = [None] * len(lines)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _fetch_one_semaphored(index: int, line: tuple) -> tuple[int, Any]:
        async with semaphore:
            data = await aget_export_line_file(
                line,
                include_custom_sequences=include_custom_sequences,
                **kwargs,
            )
            return index, data

    tasks = [
        asyncio.create_task(_fetch_one_semaphored(idx, line))
        for idx, line in enumerate(lines)
    ]

    task_results = await asyncio.gather(*tasks, return_exceptions=True)  # type: ignore[assignment]
    for idx, result in enumerate(task_results):
        line = lines[idx]
        if isinstance(result, Exception):
            LOGGER.error("Async line extract failed for %s: %s", line, result)
            results[idx] = {
                "index": idx,
                "line": line,
                "success": False,
                "data": None,
                "error": str(result),
            }
        else:
            result_idx, data = result
            results[result_idx] = {
                "index": result_idx,
                "line": line,
                "success": True,
                "data": data,
                "error": None,
            }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(lines),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = [
    "aget_export_line_file",
    "aget_export_line_files_stitched",
]
