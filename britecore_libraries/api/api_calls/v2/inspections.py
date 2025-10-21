from britecore_libraries.api.api_calls import api_client

API_CLIENT = api_client


def update_inspection_dates(policy_number, inspection_dict, **kwargs):
    inspection_json = {"policy_number": policy_number,
                       "payload": inspection_dict}
    # inspection_json.update(inspection_json)

    request_result = API_CLIENT.do_request(
        path="/api/v2/inspections/update_inspection_dates",
        json=inspection_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)
