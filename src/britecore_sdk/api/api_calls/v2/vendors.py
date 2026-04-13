"""BriteCore v2 Vendors API endpoint wrappers.

This module provides wrappers for third-party vendor integrations including
IVANS, NxTech, Munich Re, AON, Value360, WTW, Invoice Cloud, and MVR services.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


def build_ivans_manual_claim(
    data_list: list | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build an IVANS manual claim file.

    This wrapper sends ``data_list`` and ``file_date`` to
    ``/api/v2/vendors/build_ivans_manual_claim`` and returns the normalized
    ``process_result(...)`` payload for the IVANS build request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``contact_id`` and ``file_date`` to
    ``/api/v2/vendors/build_nxtech_initial_load`` and returns the normalized
    ``process_result(...)`` payload for the build request. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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

    This wrapper sends ``data_list`` and ``file_date`` to
    ``/api/v2/vendors/build_nxtech_manual_transactions`` and returns the
    normalized ``process_result(...)`` payload for the build request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``property_id`` to
    ``/api/v2/vendors/commercial_munichre_indepth_eligibility`` and returns the
    normalized ``process_result(...)`` payload for the eligibility request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``drivers`` and ``store_no_hit`` to
    ``/api/v2/vendors/fetch_motor_vehicle_report_for_drivers`` and returns the
    normalized ``process_result(...)`` payload for the MVR request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``geocoding_service`` and ``risk_id`` to
    ``/api/v2/vendors/get_aon_cat_score`` and returns the normalized
    ``process_result(...)`` payload for the CAT score request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``property_id`` to
    ``/api/v2/vendors/get_prefill_services_data`` and returns the normalized
    ``process_result(...)`` payload for the prefill request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``home_type`` and ``property_id`` to
    ``/api/v2/vendors/get_value360_token`` and returns the normalized
    ``process_result(...)`` payload for the token request. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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

    This wrapper sends ``property_descriptor`` as ``property`` to
    ``/api/v2/vendors/get_wtw_score`` and returns the normalized
    ``process_result(...)`` payload for the scoring request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``enable`` and ``policy_number`` to
    ``/api/v2/vendors/invoice_cloud_autopay_enroll`` and returns the
    normalized ``process_result(...)`` payload for the enrollment update.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``policy_number`` to
    ``/api/v2/vendors/invoice_cloud_autopay_is_enrolled`` and returns the
    normalized ``process_result(...)`` payload for the enrollment lookup.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``enable`` and ``policy_number`` to
    ``/api/v2/vendors/invoice_cloud_suppress_insured_deliverable_printings``
    and returns the normalized ``process_result(...)`` payload for the update
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``date_cursor`` and ``file_ids`` to
    ``/api/v2/vendors/ivans_edocs_build`` and returns the normalized
    ``process_result(...)`` payload for the eDocs build request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``file_name`` and ``ivans_type`` to
    ``/api/v2/vendors/ivans_file_upload`` and returns the normalized
    ``process_result(...)`` payload for the upload request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``property_id`` to
    ``/api/v2/vendors/munichre_indepth_eligibility`` and returns the normalized
    ``process_result(...)`` payload for the eligibility request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``report_id`` and ``result`` to
    ``/api/v2/vendors/update_value360_replacement_cost_value`` and returns the
    normalized ``process_result(...)`` payload for the update request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
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
