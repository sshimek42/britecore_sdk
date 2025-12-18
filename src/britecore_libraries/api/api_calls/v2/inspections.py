from logging import Logger
from typing import Any, Optional, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_libraries.exceptions import BritecoreError

LOGGER:Logger = logger

API_CLIENT:BritecoreAPIClient = api_client


def update_inspection_dates(policy_number:Optional[str] = None,
                            property_id:Optional[str] = None,
                            next_inspection_date:Optional[str] = None,
                            inspection_date_request:Optional[str] = None,
                            **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Update inspection dates for a policy or property.

    This function allows updating inspection dates by providing either a policy number
    or property ID. It verifies the provided parameters and constructs a request to
    update the inspection dates through the API.

    Args:
        policy_number: The policy number for which inspection dates need to be updated.
        property_id: The property ID for which inspection dates need to be updated.
        next_inspection_date: The next inspection date to be set. (YYYY-MM-DD)
        inspection_date_request: The inspection date request to be set. (YYYY-MM-DD)
        **kwargs: Additional keyword arguments to be passed to the API client.

    Returns:
        The result of the API request processing.

    Raises:
        BritecoreError.MissingParameter: If neither policy_number nor property_id is provided.
    """
    local_env: dict[str, Optional[str]] = {**locals}

    if not policy_number and not property_id:
        BritecoreError.MissingParameter("policy_number or property_id is required")

    parameter_list:list[dict[str,str|None]] = [{"policy_number": policy_number},
                                               {"property_id":property_id}]
    parameter_priority: list[str] = ["property_id", "policy_number"]

    inspection_json:dict[str,str] = api_client.multiple_parameter_verification(parameter_list,parameter_priority)

    LOGGER.debug("Updating inspection dates")

    for _, (k,v) in enumerate(local_env.items()):
        if v and k not in parameter_priority:
            inspection_json.update({k:v})

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/inspections/update_inspection_dates",
        json=inspection_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)
