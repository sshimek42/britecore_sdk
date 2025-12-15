from json import loads
from logging import Logger

from typing import Any, Unpack, Optional

from urllib3 import Timeout, BaseHTTPResponse, HTTPResponse

from britecore_libraries.api.api_calls import (api_client, 
                                            web_timeout_long,
                                               RequestParameters, BritecoreAPIClient)
from britecore_libraries import logger

LOGGER:Logger = logger

API_CLIENT: BritecoreAPIClient = api_client

def retrieve_notes(id: str, pageSize:Optional[int] = 1000,
                   searchString: Optional[str] = None, aggregateAll: Optional[bool] = False,
                   advSearch: Optional[bool] = False, filterAlerts: Optional[bool] = False,
                   filterUserGen: Optional[bool] = False, orderBy: Optional[str] = "",
                   page: Optional[int] = 0, ascending: Optional[bool] = False, type: Optional[str] = "",
                   filterExcludeAlerts: Optional[bool] = False, filterSystemNotesOnly: Optional[bool] = False
                   ,**kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve policy notes - See original API docs for all parameter descriptions
    :param id: Policy ID
    :type id: str
    :param pageSize: Page size (Default 1000)
    :type pageSize: Optional[int]
    :param searchString: Search string (Default: "")
    :type searchString: Optional[str]
    :param aggregateAll: If True, the API will assume the id is a contactId (Default: False)
    :type aggregateAll: Optional[bool]
    :param advSearch: Advanced search (Default: False)
    :type advSearch: Optional[bool]
    :param filterAlerts: Filter alerts (Default: False)
    :type filterAlerts: Optional[bool]
    :param filterUserGen: Filter user generated notes (Default: False)
    :type filterUserGen: Optional[bool]
    :param orderBy: Order by column (Default: "")
    :type orderBy: Optional[str]
    :param page: Starting search page (Default: 0)
    :type page: Optional[int]
    :param ascending: Return search in ascending order (Default: False)
    :type ascending: Optional[bool]
    :param type: Type of note (Default: "")
    :type type: Optional[str]
    :param filterExcludeAlerts: Exclude alerts from request (Default: False)
    :type filterExcludeAlerts: Optional[bool]
    :param filterSystemNotesOnly: Get system notes only (Default: False)
    :type filterSystemNotesOnly: Optional[bool]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Notes
    :rtype: Any
    """

    LOGGER.debug("Getting notes")

    notes_json: dict[str,Any] = {}
    local_env: dict[str, Optional[str]] = {**locals}

    for _, (k,v) in enumerate(local_env.items()):   #Add any non-default parameters to the request
        if v:
            notes_json.update({k:v})

    provided_timeout: Optional[Timeout] = kwargs.get("request_timeout", None)
    if not provided_timeout:
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    request_result: Optional[BaseHTTPResponse, HTTPResponse]  = (
        API_CLIENT.do_request(
        path="/api/v2/notes/retrieveNotes",
        json=notes_json,
        **kwargs
    ))
    if not request_result:
        return []
    try:
        return loads(request_result.data.decode("utf-8"))["records"]
    except KeyError:
        return []
