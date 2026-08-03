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
    line: tuple[str, str, str] | None = None,
    curr_eff_date_id: str | None = None,
    curr_state_id: str | None = None,
    curr_line_id: str | None = None,
    include_custom_sequences: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve export-line file data for a single line asynchronously.

    POST /api/v2/lines/get_export_line_file
    """
    if line is not None:
        try:
            curr_eff_date_id = str(line[0])
            curr_state_id = str(line[1])
            curr_line_id = str(line[2])
        except (IndexError, TypeError) as exc:
            raise BritecoreError.MissingParameter(
                "line must be a tuple of (curr_eff_date_id, curr_state_id, curr_line_id)"
            ) from exc

    if not curr_eff_date_id or not curr_state_id or not curr_line_id:
        raise BritecoreError.MissingParameter(
            "curr_eff_date_id, curr_state_id, and curr_line_id are required"
        )

    line_ids = (curr_eff_date_id, curr_state_id, curr_line_id)
    LOGGER.info("Retrieving line export for IDs: %s", line_ids)

    web_request_json: dict[str, Any] = {
        "curr_eff_date_id": curr_eff_date_id,
        "curr_line_id": curr_line_id,
        "curr_state_id": curr_state_id,
        "include_custom_sequences": include_custom_sequences,
    }

    request_result = await API_CLIENT.ado_request(
        path="/api/v2/lines/get_export_line_file",
        json={k: v for k, v in web_request_json.items() if v is not None},
        **kwargs,
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for aget_export_line_file")

    LOGGER.info("Finished retrieving line export for IDs: %s", line_ids)

    processed_result = await API_CLIENT.aprocess_result(request_result)
    if processed_result is not None:
        return loads(processed_result)

    return request_result


async def aget_line_export(*args: Any, **kwargs: Any) -> Any:
    """Backward-compatible alias for aget_export_line_file."""
    if args:
        if len(args) == 1 and "line" not in kwargs:
            kwargs["line"] = args[0]
        elif len(args) == 3 and "line" not in kwargs:
            kwargs["line"] = (args[0], args[1], args[2])
        else:
            raise TypeError(
                "aget_line_export accepts either one tuple argument or three ID arguments"
            )
    return await aget_export_line_file(**kwargs)


async def aget_export_line_files_stitched(
    lines: list[tuple],
    max_concurrent: int = 2,
    include_custom_sequences: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Fetch export data for multiple lines asynchronously and stitch the results.."""
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

    tasks: list[asyncio.Task[tuple[int, Any]]] = [
        asyncio.create_task(_fetch_one_semaphored(idx, line))
        for idx, line in enumerate(lines)
    ]

    task_results: list[tuple[int, Any] | BaseException] = await asyncio.gather(
        *tasks, return_exceptions=True
    )
    for idx, result in enumerate(task_results):
        line = lines[idx]
        if isinstance(result, BaseException):
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
    "aget_line_export",
    "aget_export_line_files_stitched",
]
