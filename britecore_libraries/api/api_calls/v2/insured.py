from britecore_libraries.api.api_calls import api_client, _LOGGER

API_CLIENT = api_client


def get_property_information_and_photos(property_id: str, **kwargs) -> dict:
    """Retrieve a single property and return data needed to add item to
    policy
    :param property_id:Property ID
    :type property_id: str
    :return: Property data
    :rtype: dict
    """
    _LOGGER.debug("Getting property info")
    property_json = API_CLIENT.do_request(
        path="/api/v2/insured/get_property_information_and_photos",
        json={"property_id": property_id},
        **kwargs,
    )
    property_json = API_CLIENT.process_result(property_json)

    return property_json