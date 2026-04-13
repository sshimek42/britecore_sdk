"""BriteCore v2 Lines API endpoint wrappers.

Provides programmatic helpers for working with BriteCore
line/policy export data.

Key functions:
    get_export_line_file -- Fetch export data for a specific line or policy type.

For interactive menu functionality, see britecore_sdk.utils.interactive_menu.
"""

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
    """Retrieve effective-date details for the provided identifiers."""
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
