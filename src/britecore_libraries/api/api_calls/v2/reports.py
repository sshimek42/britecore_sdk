from britecore_libraries.api.api_calls import api_client

API_CLIENT = api_client


def list_files(report_id, **kwargs):
    required_json = {"report_id": report_id}

    result_request = API_CLIENT.do_request(
        "/api/v2/reports/list_files",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)


def retrieve_reports(**kwargs):
    required_json = None

    result_request = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_reports", json=required_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def retrieve_report(report_id, **kwargs):
    required_json = {"report_id": report_id}

    result_request = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_report", json=required_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)
