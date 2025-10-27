from urllib3 import Retry, Timeout
from json import loads

from britecore_libraries.api.api_calls import init_api_client

API_CLIENT = init_api_client()

def get_to_be_printed(from_date, to_date, **kwargs):
    required_json = {
        "json_dict": {
            "from_date": from_date,
            "to_date": to_date,
            "ignore_state": True,
        }
    }
    request_timeout = Timeout(120)
    request_retries = Retry(
        total=3, status_forcelist=frozenset({502, 503, 504}))

    result_request = API_CLIENT.do_request(
        "/api/v1/printing/getToBePrinted",
        json=required_json,
        request_timeout=request_timeout,
        request_retries=request_retries,
        **kwargs,
    )

    return_data = None
    if result_request:
        return_data = loads(result_request.data.decode("utf-8"))

    return return_data


def mark_as_printed(file_ids, **kwargs):
    required_json = {"file_ids": file_ids}

    result_request = API_CLIENT.do_request(
        "/api/v1/printing/markAsPrinted",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)
