from britecore_libraries.api.api_calls import api_client
from britecore_libraries import logger

LOGGER = logger

API_CLIENT = api_client

def list_attachments(policy_id: str, **kwargs) -> list:
    """
    Retrieve policy attachments
    :param policy_id: Policy Id
    :type policy_id: str
    :param kwargs:
    :type kwargs:
    :return: Attachments
    :rtype: list
    """
    LOGGER.debug("Getting attachments")
    attachments_search = {"policy_id": policy_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/deliverables/list_attachments",
        json=attachments_search,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)

def get_attachment(file_id: str, **kwargs) -> dict:
    """
    Retrieve policy attachment
    :param file_id: Attachment ID
    :type file_id: str
    :param kwargs:
    :type kwargs:
    :return: Attachment
    :rtype: dict
    """
    LOGGER.debug("Getting attachment")
    file_search = {"file_id": file_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/deliverables/get_attachment", json=file_search, **kwargs
    )

    return API_CLIENT.process_result(request_result)

def get_edeliverables(date_from, date_to, **kwargs):
    required_json = {
        "date_from": date_from,
        "date_to": date_to,
        "unprocessed_only": False,
    }

    result_request = API_CLIENT.do_request(
        "/api/v2/deliverables/get_edeliverables",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)
