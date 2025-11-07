from britecore_libraries.api.api_calls import api_client

API_CLIENT = api_client


def create_full_quote(quote_json: dict, **kwargs):
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/create_full_quote", json=quote_json, **kwargs
    )

    json_info = API_CLIENT.process_result(request_result)

    if not json_info:
        return None, None

    return json_info, json_info["id"]


def get_quote(id, **kwargs):
    quote_json = {"id": id}

    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/get_quote", json=quote_json, **kwargs
    )

    quote_info = API_CLIENT.process_result(request_result)

    return quote_info
