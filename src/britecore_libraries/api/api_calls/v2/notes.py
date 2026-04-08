"""BriteCore v2 Notes API endpoint wrappers.

Provides:
    retrieve_notes -- Retrieve paginated, filterable notes for any entity ID.
"""

from json import loads
from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse, Timeout

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
    web_timeout_long,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def retrieve_notes(
    id: str,
    pageSize: int | None = 1000,
    searchString: str | None = None,
    aggregateAll: bool | None = False,
    advSearch: bool | None = False,
    filterAlerts: bool | None = False,
    filterUserGen: bool | None = False,
    orderBy: str | None = "",
    page: int | None = 0,
    ascending: bool | None = False,
    note_type: str | None = "",
    filterExcludeAlerts: bool | None = False,
    filterSystemNotesOnly: bool | None = False,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve notes for an entity with filtering and pagination controls.

    This wrapper sends note query fields to ``/api/v2/notes/retrieveNotes``.
    SDK-specific behavior: it bypasses ``process_result(...)`` and parses the
    raw JSON response directly, returning the ``records`` list or ``[]`` when
    the response is empty or does not contain records. ``**kwargs`` accepts
    ``RequestParameters`` overrides, and a long request timeout is applied when
    one is not provided.
    """
    LOGGER.debug("Getting notes")

    notes_json: dict[str, Any] = {}
    local_env: dict[str, str | None] = {**locals()}

    for _, (k, v) in enumerate(
        local_env.items()
    ):  # Add any non-default parameters to the request
        if v:
            if k == "note_type":
                k = "type"
            notes_json.update({k: v})

    provided_timeout: Timeout | None = kwargs.get("request_timeout")
    if not provided_timeout:
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/notes/retrieveNotes", json=notes_json, **kwargs
    )
    if not request_result:
        return []
    try:
        return loads(request_result.data.decode("utf-8"))["records"]
    except KeyError:
        return []
