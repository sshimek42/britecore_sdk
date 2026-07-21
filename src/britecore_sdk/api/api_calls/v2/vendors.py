"""BriteCore v2 Vendors API endpoint wrappers.

This module provides wrappers for third-party vendor integrations including
IVANS, NxTech, Munich Re, AON, Value360, WTW, Invoice Cloud, and MVR services.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import build_payload, post

API_CLIENT: BritecoreAPIClient = api_client


def build_ivans_manual_claim(
    data_list: list | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build an IVANS manual claim file.

    POST /api/v2/vendors/build_ivans_manual_claim
    """
    return post(
        "/api/v2/vendors/build_ivans_manual_claim",
        build_payload(data_list=data_list, file_date=file_date),
        **kwargs,
    )


def build_nxtech_initial_load(
    contact_id: str | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build an NxTech initial load file.

    POST /api/v2/vendors/build_nxtech_initial_load
    """
    return post(
        "/api/v2/vendors/build_nxtech_initial_load",
        build_payload(contact_id=contact_id, file_date=file_date),
        **kwargs,
    )


def build_nxtech_manual_transactions(
    data_list: list | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build NxTech manual transaction records.

    POST /api/v2/vendors/build_nxtech_manual_transactions
    """
    return post(
        "/api/v2/vendors/build_nxtech_manual_transactions",
        build_payload(data_list=data_list, file_date=file_date),
        **kwargs,
    )


def commercial_munichre_indepth_eligibility(
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check commercial Munich Re in-depth eligibility.

    POST /api/v2/vendors/commercial_munichre_indepth_eligibility
    """
    return post(
        "/api/v2/vendors/commercial_munichre_indepth_eligibility",
        build_payload(property_id=property_id),
        **kwargs,
    )


def fetch_motor_vehicle_report_for_drivers(
    drivers: list | None = None,
    store_no_hit: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Fetch motor vehicle reports for drivers.

    POST /api/v2/vendors/fetch_motor_vehicle_report_for_drivers
    """
    return post(
        "/api/v2/vendors/fetch_motor_vehicle_report_for_drivers",
        build_payload(drivers=drivers, store_no_hit=store_no_hit),
        **kwargs,
    )


def get_aon_cat_score(
    geocoding_service: str | None = None,
    risk_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve an AON CAT score for a risk.

    POST /api/v2/vendors/get_aon_cat_score
    """
    return post(
        "/api/v2/vendors/get_aon_cat_score",
        build_payload(geocoding_service=geocoding_service, risk_id=risk_id),
        **kwargs,
    )


def get_prefill_services_data(
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve prefill-services data for a property.

    POST /api/v2/vendors/get_prefill_services_data
    """
    return post(
        "/api/v2/vendors/get_prefill_services_data",
        build_payload(property_id=property_id),
        **kwargs,
    )


def get_value360_token(
    home_type: str | None = None,
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a Value360 token for a property valuation session.

    POST /api/v2/vendors/get_value360_token
    """
    return post(
        "/api/v2/vendors/get_value360_token",
        build_payload(home_type=home_type, property_id=property_id),
        **kwargs,
    )


def get_wtw_score(
    property_descriptor: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a WTW score for a property.

    POST /api/v2/vendors/get_wtw_score
    """
    payload: dict[str, Any] = {}
    if property_descriptor is not None:
        payload["property"] = property_descriptor
    return post("/api/v2/vendors/get_wtw_score", payload, **kwargs)


def invoice_cloud_autopay_enroll(
    enable: Any | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Enroll or unenroll a policy in Invoice Cloud autopay.

    POST /api/v2/vendors/invoice_cloud_autopay_enroll
    """
    return post(
        "/api/v2/vendors/invoice_cloud_autopay_enroll",
        build_payload(enable=enable, policy_number=policy_number),
        **kwargs,
    )


def invoice_cloud_autopay_is_enrolled(
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check Invoice Cloud autopay enrollment status.

    POST /api/v2/vendors/invoice_cloud_autopay_is_enrolled
    """
    return post(
        "/api/v2/vendors/invoice_cloud_autopay_is_enrolled",
        build_payload(policy_number=policy_number),
        **kwargs,
    )


def invoice_cloud_suppress_insured_deliverable_printings(
    enable: bool | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Suppress or unsuppress insured deliverable printings.

    POST /api/v2/vendors/invoice_cloud_suppress_insured_deliverable_printings
    """
    return post(
        "/api/v2/vendors/invoice_cloud_suppress_insured_deliverable_printings",
        build_payload(enable=enable, policy_number=policy_number),
        **kwargs,
    )


def ivans_edocs_build(
    date_cursor: str | None = None,
    file_ids: list | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build IVANS eDocs for a set of files.

    POST /api/v2/vendors/ivans_edocs_build
    """
    return post(
        "/api/v2/vendors/ivans_edocs_build",
        build_payload(date_cursor=date_cursor, file_ids=file_ids),
        **kwargs,
    )


def ivans_file_upload(
    file_name: str | None = None,
    ivans_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a file to IVANS.

    POST /api/v2/vendors/ivans_file_upload
    """
    return post(
        "/api/v2/vendors/ivans_file_upload",
        build_payload(file_name=file_name, ivans_type=ivans_type),
        **kwargs,
    )


def munichre_indepth_eligibility(
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check Munich Re in-depth eligibility for a property.

    POST /api/v2/vendors/munichre_indepth_eligibility
    """
    return post(
        "/api/v2/vendors/munichre_indepth_eligibility",
        build_payload(property_id=property_id),
        **kwargs,
    )


def update_value360_replacement_cost_value(
    report_id: str | None = None,
    result: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update the Value360 replacement cost value.

    POST /api/v2/vendors/update_value360_replacement_cost_value
    """
    return post(
        "/api/v2/vendors/update_value360_replacement_cost_value",
        build_payload(report_id=report_id, result=result),
        **kwargs,
    )


__all__ = [
    "build_ivans_manual_claim",
    "build_nxtech_initial_load",
    "build_nxtech_manual_transactions",
    "commercial_munichre_indepth_eligibility",
    "fetch_motor_vehicle_report_for_drivers",
    "get_aon_cat_score",
    "get_prefill_services_data",
    "get_value360_token",
    "get_wtw_score",
    "invoice_cloud_autopay_enroll",
    "invoice_cloud_autopay_is_enrolled",
    "invoice_cloud_suppress_insured_deliverable_printings",
    "ivans_edocs_build",
    "ivans_file_upload",
    "munichre_indepth_eligibility",
    "update_value360_replacement_cost_value",
]

# --- Autogenerated spec wrappers ---


def import_credit_report(
    report_number: str | None = None,
    contact_id: str | None = None,
    content: str | None = None,
    score: str | None = None,
    date_added: str | None = None,
    warning: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Import Credit Report.

    POST /api/v2/vendors/import_credit_report
    """
    request_json: dict[str, Any] = {
        "report_number": report_number,
        "contact_id": contact_id,
        "content": content,
        "score": score,
        "date_added": date_added,
        "warning": warning,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/vendors/import_credit_report",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/vendors/import_credit_report"
    )


def import_motor_vehicle_report(
    report_number: str | None = None,
    drivers_license_number: str | None = None,
    drivers_license_state: str | None = None,
    contact_id: str | None = None,
    report_content: str | None = None,
    date_added: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Import Motor Vehicle Report.

    POST /api/v2/vendors/import_motor_vehicle_report
    """
    request_json: dict[str, Any] = {
        "report_number": report_number,
        "drivers_license_number": drivers_license_number,
        "drivers_license_state": drivers_license_state,
        "contact_id": contact_id,
        "report_content": report_content,
        "date_added": date_added,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/vendors/import_motor_vehicle_report",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/vendors/import_motor_vehicle_report"
    )


def stripe_replay_missed_webhooks(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Stripe Replay Missed Webhooks.

    POST /api/v2/vendors/stripe_replay_missed_webhooks
    """
    request_json: dict[str, Any] = {
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/vendors/stripe_replay_missed_webhooks",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/vendors/stripe_replay_missed_webhooks"
    )


def sungard_retry_send_file(
    file_name: str | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Sungard Retry Send File.

    POST /api/v2/vendors/sungard_retry_send_file
    """
    request_json: dict[str, Any] = {
        "file_name": file_name,
        "file_date": file_date,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/vendors/sungard_retry_send_file",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/vendors/sungard_retry_send_file"
    )


__all__.extend(
    [
        "import_credit_report",
        "import_motor_vehicle_report",
        "stripe_replay_missed_webhooks",
        "sungard_retry_send_file",
    ]
)
