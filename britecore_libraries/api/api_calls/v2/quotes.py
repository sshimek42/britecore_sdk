from britecore_libraries.api.api_calls import api_client
from datetime import datetime

API_CLIENT = api_client

def create_full_quote(
    number,
    policy_type_id,
    agency_id,
    named_insureds,
    risks,
    policy_number_origin="manual",
    underwriting_questions=None,
    transaction_type="renewal",
    term_type="1 Year",
    inception_date=datetime.today().strftime("%Y-%m-%d"),
    next_inspection_date = None,
    **kwargs,
):
    if not underwriting_questions:
        underwriting_questions = []

    quote_json = {
        "number": number,
        "number_origin": policy_number_origin,
        "underwriting_questions": underwriting_questions,
        "effective_date": datetime.today().strftime("%Y-%m-%d"),
        "policy_type_id": policy_type_id,
        "transaction_type": transaction_type,
        "term_type": term_type,
        "agency_id": agency_id,
        "named_insureds": named_insureds,
        "risks": risks,
        "inception_date": inception_date,
        "description": f"From Policy {number[3:]}"
    }

    if next_inspection_date:
        quote_json.update({"next_inspection_date": next_inspection_date})

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