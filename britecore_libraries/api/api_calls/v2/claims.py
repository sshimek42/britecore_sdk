from britecore_libraries.api.api_calls import _LOGGER, api_client

API_CLIENT = api_client


def get_claim(claim_id: str, **kwargs) -> dict:
    """
    Retrieve policy claim information
    :param claim_id: Claim Number
    :type claim_id: str
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    _LOGGER.debug("Getting claim information")
    claim_search = {"claim_id": claim_id}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/claims/get_claim", json=claim_search, **kwargs
    )
    return BritecoreAPIClient.process_result(request_result)
