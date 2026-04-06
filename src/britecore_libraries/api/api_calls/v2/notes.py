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
    type: str | None = "",
    filterExcludeAlerts: bool | None = False,
    filterSystemNotesOnly: bool | None = False,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieves notes from the API based on the specified parameters.

    This function fetches notes from the API endpoint `/api/v2/notes/retrieveNotes` with various filtering and sorting options.
    It handles request timeouts and processes the response to extract note records.

    Parameters:
        id (str): The identifier for the notes to retrieve.
        pageSize (int, optional): The number of records to return per page. Defaults to 1000.
        searchString (str, optional): A string to search for within the notes. Defaults to None.
        aggregateAll (bool, optional): Whether to aggregate all notes. Defaults to False.
        advSearch (bool, optional): Whether to perform an advanced search. Defaults to False.
        filterAlerts (bool, optional): Whether to filter out alerts. Defaults to False.
        filterUserGen (bool, optional): Whether to filter out user-generated notes. Defaults to False.
        orderBy (str, optional): The field to order results by. Defaults to "".
        page (int, optional): The page number to retrieve. Defaults to 0.
        ascending (bool, optional): Whether to sort in ascending order. Defaults to False.
        type (str, optional): The type of notes to retrieve. Defaults to "".
        filterExcludeAlerts (bool, optional): Whether to exclude alerts from filtering. Defaults to False.
        filterSystemNotesOnly (bool, optional): Whether to filter for system notes only. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the API client request.

    Returns:
        list: A list of note records retrieved from the API, or an empty list if the request fails or no records are found.
    """

    LOGGER.debug("Getting notes")

    notes_json: dict[str, Any] = {}
    local_env: dict[str, str | None] = {**locals()}

    for _, (k, v) in enumerate(
        local_env.items()
    ):  # Add any non-default parameters to the request
        if v:
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
