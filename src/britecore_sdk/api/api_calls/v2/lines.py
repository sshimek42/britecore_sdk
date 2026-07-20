"""BriteCore v2 Lines API endpoint wrappers.

Provides programmatic helpers for working with BriteCore
line/policy export data.

Key functions:
    get_export_line_file -- Fetch export data for a specific line or policy type.

For interactive menu functionality, see britecore_sdk.utils.interactive_menu.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from json import loads
from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import post

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _effective_date_payload(
    *, effective_date_id: str | None = None, effective_date: str | None = None
) -> dict[str, str | None]:
    """Resolve effective-date parameters using existing priority rules."""
    if effective_date_id:
        return {"effective_date_id": effective_date_id}
    if effective_date:
        return {"effective_date": effective_date}
    return {}


def get_export_line_file(
    line: tuple,
    include_custom_sequences: bool | None = False,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve export-line file data for a line.

    This wrapper sends line identifiers to
    ``/api/v2/lines/get_export_line_file`` and returns the parsed JSON payload data.
    ``**kwargs`` accepts ``RequestParameters`` overrides.

    Args:
        line: Tuple of (effective_date_id, state_id, line_id)
        include_custom_sequences: Whether to include custom sequences in the export
        **kwargs: Additional request parameters for the API client
    """
    LOGGER.info("Retrieving line export for IDs: %s", line)

    web_request_json: dict[str, str | bool | None] = {
        "curr_eff_date_id": line[0],
        "curr_line_id": line[2],
        "curr_state_id": line[1],
        "include_custom_sequences": include_custom_sequences,
    }

    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_export_line_file",
        json={k: v for k, v in web_request_json.items() if v is not None},
        **kwargs,
    )

    LOGGER.info("Finished retrieving line export for IDs: %s", line)

    processed_result = API_CLIENT.process_result(request_result)
    if processed_result is not None:
        return loads(processed_result)

    return request_result


def get_all_effective_dates(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve available effective dates for lines.

    This wrapper calls ``/api/v2/lines/get_all_effective_dates`` and returns
    the normalized ``process_result(...)`` payload containing effective date
    options. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates", **kwargs
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/get_all_effective_dates"
    )


def get_all_states(
    effective_date_id: str | None = None, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve available states, optionally filtered by effective date.

    This wrapper sends the optional ``effective_date_id`` to
    ``/api/v2/lines/get_all_states`` and returns the normalized
    ``process_result(...)`` payload for state options. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
    """
    effective_date_json: dict[str, str] | None = {}

    if effective_date_id:
        effective_date_json = {"effective_date_id": effective_date_id}

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states", json=effective_date_json, **kwargs
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/get_all_states"
    )


def get_all_lines(
    effective_date_id: str,
    location_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve available lines for an effective date and optional location.

    This wrapper sends ``effective_date_id`` and the optional ``location_id``
    filter to ``/api/v2/lines/get_all_lines`` and returns the normalized
    ``process_result(...)`` payload for available lines.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    current_lines_json: dict[str, str] = {
        "effective_date_id": effective_date_id,
    }

    if location_id:
        current_lines_json.update({"location_id": location_id})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_lines", json=current_lines_json, **kwargs
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/get_all_lines"
    )


def list_policy_types(
    location_id: str,
    effective_date_id: str | None = None,
    effective_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List policy types for a location and effective-date context.

    This wrapper requires a location and one effective-date identifier,
    then calls ``/api/v2/lines/list_policy_types`` and returns the normalized
    ``process_result(...)`` payload for policy-type options.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    if not effective_date and effective_date_id:
        BritecoreError.MissingParameter(
            "Either effective_date or effective_date is required"
        )

    parameter_list: list[dict[str, str | None]] = [
        {"effective_date": effective_date},
        {"effective_date_id": effective_date_id},
    ]
    parameter_priority: list[str] = ["effective_date_id", "effective_date"]

    policy_types_json: dict[str, str | None] = (
        api_client.multiple_parameter_verification(parameter_list, parameter_priority)
    )

    policy_types_json.update({"location_id": location_id})

    # Remove None values before sending
    filtered_policy_types_json = {
        k: v for k, v in policy_types_json.items() if v is not None
    }

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/list_policy_types",
        json=filtered_policy_types_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/list_policy_types"
    )


def find_effective_date(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Find the matching effective-date identifier for a provided date context."""
    return post(
        path="/api/v2/lines/find_effective_date",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def retrieve_effective_date(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve effective-date details for a given effective date ID.

    Args:
        payload: Dict containing ``effective_date_id`` (UUID, required).
            Example::

                {"effective_date_id": "1376645b-85ff-44db-9498-1e6f73049670"}

        **kwargs: :class:`~britecore_sdk.api.britecoreAPI_CLIENT.RequestParameters` overrides.

    Returns:
        Normalized response data dict with keys including ``effective_date``,
        ``id``, ``description``, ``states``, ``lines``, etc.
    """
    return post(
        path="/api/v2/lines/retrieve_effective_date",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def create_builderdiff_mapping(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a builderdiff mapping record for line migration workflows."""
    return post(
        path="/api/v2/lines/create_builderdiff_mapping",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def copy_underwriting_rules(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Copy underwriting rules between source and destination contexts."""
    return post(
        path="/api/v2/lines/copy_underwriting_rules",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def delete_builderdiff_mapping(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete an existing builderdiff mapping record."""
    return post(
        path="/api/v2/lines/delete_builderdiff_mapping",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def copy_line_items(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Copy line items from one line definition to another."""
    return post(
        path="/api/v2/lines/copy_line_items",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def get_policies_with_line_item(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Return policies that reference a specific line item."""
    return post(
        path="/api/v2/lines/get_policies_with_line_item",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def retrieve_policy_type(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy-type metadata for a policy type identifier."""
    return post(
        path="/api/v2/lines/retrieve_policy_type",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def delete_line_item(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a line item from a line configuration."""
    return post(
        path="/api/v2/lines/delete_line_item",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def import_line(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Import a line definition payload into the lines module."""
    return post(
        path="/api/v2/lines/import_line",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def copy_policy_type(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Copy a policy type definition to a new target context."""
    return post(
        path="/api/v2/lines/copy_policy_type",
        payload=payload,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def get_all_policy_types(
    location_id: str,
    effective_date_id: str | None = None,
    effective_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List all policy types for a location and effective-date context."""
    policy_types_json = _effective_date_payload(
        effective_date_id=effective_date_id,
        effective_date=effective_date,
    )
    policy_types_json.update({"location_id": location_id})
    return post(
        path="/api/v2/lines/get_all_policy_types",
        payload=policy_types_json,
        include_endpoint=True,
        client=API_CLIENT,
        **kwargs,
    )


def get_export_line_files_stitched(
    lines: list[tuple],
    max_workers: int = 2,
    include_custom_sequences: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Fetch export data for multiple lines and stitch the results together.

    Line file export calls are **long-running** (typically 45–60 seconds each).
    This helper intentionally defaults to low concurrency (``max_workers=2``)
    to avoid overloading the BriteCore backend and to limit timeout failures.
    Callers should pass a generous ``request_timeout`` (e.g., 120–180 seconds)
    via ``**kwargs``.

    The stitched result contains all per-line payloads keyed by line index,
    plus a summary of successes and failures.

    Args:
        lines: List of ``(effective_date_id, state_id, line_id)`` tuples,
            one per line to extract.
        max_workers: Maximum concurrent workers.  Default is ``2`` (low because
            each extract call is long-running and heavy).
        include_custom_sequences: Whether to include custom sequences in each
            export.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` overrides.  It is strongly recommended
            to pass a long ``request_timeout``::

                get_export_line_files_stitched(
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
        ValueError: If ``max_workers`` is less than 1.
    """
    if not lines or not isinstance(lines, list):
        raise BritecoreError.MissingParameter(
            "lines is required and must be a non-empty list"
        )
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    worker_count = min(max_workers, len(lines))
    results: list[dict[str, Any] | None] = [None] * len(lines)

    def _fetch_one(index: int, line: tuple) -> tuple[int, Any]:
        data = get_export_line_file(
            line, include_custom_sequences=include_custom_sequences, **kwargs
        )
        return index, data

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[tuple[int, Any]], int] = {
            executor.submit(_fetch_one, idx, line): idx
            for idx, line in enumerate(lines)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            line = lines[idx]
            try:
                result_idx, data = future.result()
                results[result_idx] = {
                    "index": result_idx,
                    "line": line,
                    "success": True,
                    "data": data,
                    "error": None,
                }
            except Exception as exc:
                LOGGER.error("Line extract failed for %s: %s", line, exc)
                results[idx] = {
                    "index": idx,
                    "line": line,
                    "success": False,
                    "data": None,
                    "error": str(exc),
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


# --- Autogenerated spec wrappers ---


def create_effective_date(
    force: bool | None = None,
    description: str | None = None,
    policy_type_external_system_references: list[str] | None = None,
    effective_date: str | None = None,
    policy_type_ids: list[str] | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/create_effective_date``."""
    request_json: dict[str, Any] = {
        "force": force,
        "description": description,
        "policy_type_external_system_references": policy_type_external_system_references,
        "effective_date": effective_date,
        "policy_type_ids": policy_type_ids,
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/create_effective_date",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/create_effective_date"
    )


def create_policy_type(
    line: Any | dict[str, Any] | None = None,
    location_id: str | None = None,
    policy_type: dict[str, Any] | None = None,
    effective_date_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/create_policy_type``."""
    request_json: dict[str, Any] = {
        "line": line,
        "location_id": location_id,
        "policy_type": policy_type,
        "effective_date_id": effective_date_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/create_policy_type",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/create_policy_type"
    )


def create_rating_grid_definition(
    name: Any | None = None,
    location_id: Any | None = None,
    type: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/create_rating_grid_definition``."""
    request_json: dict[str, Any] = {
        "name": name,
        "location_id": location_id,
        "type": type,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/create_rating_grid_definition",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/create_rating_grid_definition"
    )


def delete_effective_date(
    effective_date_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/delete_effective_date``."""
    request_json: dict[str, Any] = {
        "effective_date_id": effective_date_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/delete_effective_date",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/delete_effective_date"
    )


def delete_policy_type(
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/delete_policy_type``."""
    request_json: dict[str, Any] = {
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/delete_policy_type",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/delete_policy_type"
    )


def delete_rating_table(
    sort_by: str | None = None,
    sort_order: str | None = None,
    id: str | None = None,
    page_size: int | None = None,
    page: int | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/delete_rating_table``."""
    request_json: dict[str, Any] = {
        "sort_by": sort_by,
        "sort_order": sort_order,
        "id": id,
        "page_size": page_size,
        "page": page,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/delete_rating_table",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/delete_rating_table"
    )


def delete_rating_table_file(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/delete_rating_table_file``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/delete_rating_table_file",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/delete_rating_table_file"
    )


def get_effective_date(
    effective_date_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/get_effective_date``."""
    request_json: dict[str, Any] = {
        "effective_date_id": effective_date_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_effective_date",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/get_effective_date"
    )


def get_policy_type(
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/get_policy_type``."""
    request_json: dict[str, Any] = {
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_policy_type",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/get_policy_type"
    )


def get_rating_table_template(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/get_rating_table_template``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_rating_table_template",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/get_rating_table_template"
    )


def get_underwriting_question_autofill_answers(
    policy_type_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/get_underwriting_question_autofill_answers``."""
    request_json: dict[str, Any] = {
        "policy_type_id": policy_type_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_underwriting_question_autofill_answers",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/lines/get_underwriting_question_autofill_answers",
    )


def import_rating_table(
    location_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/import_rating_table``."""
    request_json: dict[str, Any] = {"location_id": location_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/import_rating_table",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/import_rating_table"
    )


def list_effective_dates(
    sort_order: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/list_effective_dates``."""
    request_json: dict[str, Any] = {
        "sort_order": sort_order,
        "page": page,
        "page_size": page_size,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/list_effective_dates",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/list_effective_dates"
    )


def list_rating_grid_definitions(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/list_rating_grid_definitions``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/list_rating_grid_definitions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/list_rating_grid_definitions"
    )


def list_rating_tables(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/list_rating_tables``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/list_rating_tables",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/list_rating_tables"
    )


def modify_effective_date(
    effective_date: str | None = None,
    force: bool | None = None,
    id: str | None = None,
    description: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/modify_effective_date``."""
    request_json: dict[str, Any] = {
        "effective_date": effective_date,
        "force": force,
        "id": id,
        "description": description,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/modify_effective_date",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/modify_effective_date"
    )


def modify_policy_type(
    items: list[dict[str, Any]] | None = None,
    id: str | None = None,
    sub_lines: list[dict[str, Any]] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/modify_policy_type``."""
    request_json: dict[str, Any] = {
        "items": items,
        "id": id,
        "sub_lines": sub_lines,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/modify_policy_type",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/modify_policy_type"
    )


def retrieve_policy_type_claims_tabs_visibility(
    policy_type_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/retrieve_policy_type_claims_tabs_visibility``."""
    request_json: dict[str, Any] = {
        "policy_type_id": policy_type_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/retrieve_policy_type_claims_tabs_visibility",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/lines/retrieve_policy_type_claims_tabs_visibility",
    )


def retrieve_rating_table(
    sort_by: str | None = None,
    sort_order: str | None = None,
    id: str | None = None,
    page_size: int | None = None,
    page: int | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/retrieve_rating_table``."""
    request_json: dict[str, Any] = {
        "sort_by": sort_by,
        "sort_order": sort_order,
        "id": id,
        "page_size": page_size,
        "page": page,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/retrieve_rating_table",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/retrieve_rating_table"
    )


def retrieve_underwriting_questions(
    policy_type_id: str | None = None,
    effective_date_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/retrieve_underwriting_questions``."""
    request_json: dict[str, Any] = {
        "policy_type_id": policy_type_id,
        "effective_date_id": effective_date_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/retrieve_underwriting_questions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/retrieve_underwriting_questions"
    )


def update_policy_type_claims_tab_visibility(
    policy_type_id: str | None = None,
    flagged: bool | None = None,
    code_value_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/update_policy_type_claims_tab_visibility``."""
    request_json: dict[str, Any] = {
        "policy_type_id": policy_type_id,
        "flagged": flagged,
        "code_value_type": code_value_type,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/update_policy_type_claims_tab_visibility",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/lines/update_policy_type_claims_tab_visibility",
    )


def update_rating_table(
    id: str | None = None,
    file_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/lines/update_rating_table``."""
    request_json: dict[str, Any] = {
        "id": id,
        "file_id": file_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/update_rating_table",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/lines/update_rating_table"
    )


__all__ = [
    "create_effective_date",
    "create_policy_type",
    "create_rating_grid_definition",
    "delete_effective_date",
    "delete_policy_type",
    "delete_rating_table",
    "delete_rating_table_file",
    "get_effective_date",
    "get_policy_type",
    "get_rating_table_template",
    "get_underwriting_question_autofill_answers",
    "import_rating_table",
    "list_effective_dates",
    "list_rating_grid_definitions",
    "list_rating_tables",
    "modify_effective_date",
    "modify_policy_type",
    "retrieve_policy_type_claims_tabs_visibility",
    "retrieve_rating_table",
    "retrieve_underwriting_questions",
    "update_policy_type_claims_tab_visibility",
    "update_rating_table",
]
