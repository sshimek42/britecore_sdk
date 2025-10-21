from britecore_libraries.api.api_calls import _LOGGER, api_client

API_CLIENT = api_client


def get_available_function_names(**kwargs) -> dict:
    """
    Get available functions
    :param kwargs:
    :type kwargs:
    :return: Functions
    :rtype: dict
    """
    _LOGGER.debug("Retrieving functions")
    request_result = API_CLIENT.do_request(
        path="/api/v2/utils/get_available_function_names",
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def rebuild_search_index(index_to_rebuild: list, **kwargs) -> bool:
    """
    Rebuild BriteCore search indexes
    :param index_to_rebuild:
    :type index_to_rebuild: list
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    _LOGGER.debug("Rebuilding index")
    rebuild_index = {"only_build": index_to_rebuild}
    request_result = API_CLIENT.do_request(
        path="/api/v2/utils/rebuild_search_index",
        json=rebuild_index,
        **kwargs,
    )
    return API_CLIENT.process_result(request_result)
