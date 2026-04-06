"""BriteCore v2 Vendors API endpoint wrappers.

Provides:
    build_ivans_manual_claim                              -- Build an IVANS manual claim file.
    build_nxtech_initial_load                             -- Build an NxTech initial load file.
    build_nxtech_manual_transactions                      -- Build NxTech manual transaction records.
    commercial_munichre_indepth_eligibility               -- Check commercial MunichRe in-depth eligibility.
    fetch_motor_vehicle_report_for_drivers                -- Fetch MVR reports for a list of drivers.
    get_aon_cat_score                                     -- Retrieve an AON CAT score for a risk.
    get_prefill_services_data                             -- Retrieve prefill services data for a property.
    get_value360_token                                    -- Retrieve a Value360 token for a property.
    get_wtw_score                                         -- Retrieve a Willis Towers Watson score.
    invoice_cloud_autopay_enroll                          -- Enroll or unenroll a policy in Invoice Cloud autopay.
    invoice_cloud_autopay_is_enrolled                     -- Check Invoice Cloud autopay enrollment status.
    invoice_cloud_suppress_insured_deliverable_printings  -- Suppress/unsuppress insured printings via Invoice Cloud.
    ivans_edocs_build                                     -- Build IVANS eDocs for a set of files.
    ivans_file_upload                                     -- Upload a file to IVANS.
    munichre_indepth_eligibility                          -- Check MunichRe in-depth eligibility for a property.
    update_value360_replacement_cost_value                -- Update the Value360 replacement cost value.
"""
from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a vendors request and normalize the response."""
    LOGGER.debug("Calling vendors endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def build_ivans_manual_claim(
    data_list: list | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build an IVANS manual claim file.

    Parameters
    ----------
    data_list : list, optional
        List of claim data records to include.
    file_date : str, optional
        Date of the file in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/vendors/build_ivans_manual_claim",
        _build_payload(data_list=data_list, file_date=file_date),
        **kwargs,
    )


def build_nxtech_initial_load(
    contact_id: str | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build an NxTech initial load file for a contact.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the contact to include in the initial load.
    file_date : str, optional
        Date of the file in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/vendors/build_nxtech_initial_load",
        _build_payload(contact_id=contact_id, file_date=file_date),
        **kwargs,
    )


def build_nxtech_manual_transactions(
    data_list: list | None = None,
    file_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build NxTech manual transaction records.

    Parameters
    ----------
    data_list : list, optional
        List of transaction data records.
    file_date : str, optional
        Date of the file in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/vendors/build_nxtech_manual_transactions",
        _build_payload(data_list=data_list, file_date=file_date),
        **kwargs,
    )


def commercial_munichre_indepth_eligibility(
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check commercial MunichRe in-depth eligibility for a property.

    Parameters
    ----------
    property_id : str, optional
        UUID of the commercial property to evaluate.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing eligibility results.
    """
    return _post(
        "/api/v2/vendors/commercial_munichre_indepth_eligibility",
        _build_payload(property_id=property_id),
        **kwargs,
    )


def fetch_motor_vehicle_report_for_drivers(
    drivers: list | None = None,
    store_no_hit: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Fetch Motor Vehicle Report (MVR) data for a list of drivers.

    Parameters
    ----------
    drivers : list, optional
        List of driver objects to process.
    store_no_hit : bool, optional
        Whether to store records when no hit is found.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing MVR results.
    """
    return _post(
        "/api/v2/vendors/fetch_motor_vehicle_report_for_drivers",
        _build_payload(drivers=drivers, store_no_hit=store_no_hit),
        **kwargs,
    )


def get_aon_cat_score(
    geocoding_service: str | None = None,
    risk_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve an AON CAT score for a specific risk.

    Parameters
    ----------
    geocoding_service : str, optional
        Name of the geocoding service to use.
    risk_id : str, optional
        UUID of the risk to score.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the CAT score.
    """
    return _post(
        "/api/v2/vendors/get_aon_cat_score",
        _build_payload(geocoding_service=geocoding_service, risk_id=risk_id),
        **kwargs,
    )


def get_prefill_services_data(
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve prefill services data for a property.

    Parameters
    ----------
    property_id : str, optional
        UUID of the property for which to retrieve prefill data.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing prefill data.
    """
    return _post(
        "/api/v2/vendors/get_prefill_services_data",
        _build_payload(property_id=property_id),
        **kwargs,
    )


def get_value360_token(
    home_type: str | None = None,
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a Value360 token for a property valuation session.

    Parameters
    ----------
    home_type : str, optional
        Type of home/property.
    property_id : str, optional
        UUID of the property.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the Value360 token.
    """
    return _post(
        "/api/v2/vendors/get_value360_token",
        _build_payload(home_type=home_type, property_id=property_id),
        **kwargs,
    )


def get_wtw_score(
    property_descriptor: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a Willis Towers Watson (WTW) score for a property.

    Parameters
    ----------
    property_descriptor : str, optional
        Property identifier or descriptor passed to the WTW service as
        ``property`` in the request body.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the WTW score.
    """
    payload: dict[str, Any] = {}
    if property_descriptor is not None:
        payload["property"] = property_descriptor
    return _post("/api/v2/vendors/get_wtw_score", payload, **kwargs)


def invoice_cloud_autopay_enroll(
    enable: Any | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Enroll or unenroll a policy in Invoice Cloud autopay.

    Parameters
    ----------
    enable : Any, optional
        ``True`` to enroll; ``False`` to unenroll.
    policy_number : str, optional
        Policy number to update.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/vendors/invoice_cloud_autopay_enroll",
        _build_payload(enable=enable, policy_number=policy_number),
        **kwargs,
    )


def invoice_cloud_autopay_is_enrolled(
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check the Invoice Cloud autopay enrollment status for a policy.

    Parameters
    ----------
    policy_number : str, optional
        Policy number to check.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response indicating enrollment status.
    """
    return _post(
        "/api/v2/vendors/invoice_cloud_autopay_is_enrolled",
        _build_payload(policy_number=policy_number),
        **kwargs,
    )


def invoice_cloud_suppress_insured_deliverable_printings(
    enable: bool | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Suppress or unsuppress insured deliverable printings via Invoice Cloud.

    Parameters
    ----------
    enable : bool, optional
        ``True`` to suppress; ``False`` to unsuppress.
    policy_number : str, optional
        Policy number to update.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/vendors/invoice_cloud_suppress_insured_deliverable_printings",
        _build_payload(enable=enable, policy_number=policy_number),
        **kwargs,
    )


def ivans_edocs_build(
    date_cursor: str | None = None,
    file_ids: list | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Build IVANS eDocs for a set of files.

    Parameters
    ----------
    date_cursor : str, optional
        Date cursor in ``YYYY-MM-DD`` format.
    file_ids : list, optional
        List of file UUIDs to include in the eDocs build.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/vendors/ivans_edocs_build",
        _build_payload(date_cursor=date_cursor, file_ids=file_ids),
        **kwargs,
    )


def ivans_file_upload(
    file_name: str | None = None,
    ivans_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a file to IVANS.

    Parameters
    ----------
    file_name : str, optional
        Name of the file to upload.
    ivans_type : str, optional
        IVANS file type identifier.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/vendors/ivans_file_upload",
        _build_payload(file_name=file_name, ivans_type=ivans_type),
        **kwargs,
    )


def munichre_indepth_eligibility(
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check MunichRe in-depth eligibility for a residential property.

    Parameters
    ----------
    property_id : str, optional
        UUID of the property to evaluate.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing eligibility results.
    """
    return _post(
        "/api/v2/vendors/munichre_indepth_eligibility",
        _build_payload(property_id=property_id),
        **kwargs,
    )


def update_value360_replacement_cost_value(
    report_id: str | None = None,
    result: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update the Value360 replacement cost value from a report result.

    Parameters
    ----------
    report_id : str, optional
        UUID of the Value360 report.
    result : dict, optional
        The result object containing replacement cost data.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the update.
    """
    return _post(
        "/api/v2/vendors/update_value360_replacement_cost_value",
        _build_payload(report_id=report_id, result=result),
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
