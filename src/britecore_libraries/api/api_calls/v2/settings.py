"""BriteCore v2 Settings API endpoint wrappers.

Provides:
    add_city_to_zip_override            -- Add a city override for a ZIP code.
    add_counties_to_state               -- Add counties to a state.
    add_county_to_zip_override          -- Add a county override for a ZIP code.
    get_pdf_engine                      -- Retrieve the current PDF engine setting.
    get_setting_value                   -- Retrieve a specific system setting value.
    get_system_tags_list                -- Retrieve the list of all system tags.
    retrieve_credit_permission_prompt   -- Retrieve the credit permission prompt.
    retrieve_property_valuation_availability -- Check property valuation availability.
    retrieve_system_tags                -- Retrieve system tags, optionally by level.
    set_pdf_engine                      -- Set the PDF engine for document generation.
    set_setting_value                   -- Set a specific system setting value.
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
    """Send a settings request and normalize the response."""
    LOGGER.debug("Calling settings endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def add_city_to_zip_override(
    city: str | None = None,
    county: str | None = None,
    state_abbreviation: str | None = None,
    zip_code: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a city-level override for a specific ZIP code.

    Parameters
    ----------
    city : str, optional
        City name to associate with the ZIP code.
    county : str, optional
        County name.
    state_abbreviation : str, optional
        Two-letter state abbreviation.
    zip_code : str, optional
        ZIP code to override.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/settings/add_city_to_zip_override",
        _build_payload(
            city=city,
            county=county,
            state_abbreviation=state_abbreviation,
            zip_code=zip_code,
        ),
        **kwargs,
    )


def add_counties_to_state(
    counties: list | None = None,
    country: str | None = None,
    state: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add one or more counties to a state.

    Parameters
    ----------
    counties : list, optional
        List of county objects to add.
    country : str, optional
        Country identifier.
    state : dict, optional
        State object containing state metadata.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/settings/add_counties_to_state",
        _build_payload(counties=counties, country=country, state=state),
        **kwargs,
    )


def add_county_to_zip_override(
    county: str | None = None,
    state_abbreviation: str | None = None,
    zip_code: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a county-level override for a specific ZIP code.

    Parameters
    ----------
    county : str, optional
        County name to associate with the ZIP code.
    state_abbreviation : str, optional
        Two-letter state abbreviation.
    zip_code : str, optional
        ZIP code to override.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/settings/add_county_to_zip_override",
        _build_payload(
            county=county,
            state_abbreviation=state_abbreviation,
            zip_code=zip_code,
        ),
        **kwargs,
    )


def get_pdf_engine(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the current PDF engine setting.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the active PDF engine name.
    """
    return _post("/api/v2/settings/get_pdf_engine", {}, **kwargs)


def get_setting_value(
    option: str | None = None,
    section: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the value of a specific system setting.

    Parameters
    ----------
    option : str, optional
        The setting option (key) to retrieve.
    section : str, optional
        The settings section the option belongs to.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the setting value.
    """
    return _post(
        "/api/v2/settings/get_setting_value",
        _build_payload(option=option, section=section),
        **kwargs,
    )


def get_system_tags_list(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the complete list of system tags.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the system tags list.
    """
    return _post("/api/v2/settings/get_system_tags_list", {}, **kwargs)


def retrieve_credit_permission_prompt(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the credit permission prompt text shown to users.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the prompt text.
    """
    return _post("/api/v2/settings/retrieve_credit_permission_prompt", {}, **kwargs)


def retrieve_property_valuation_availability(
    chosen_role: str | None = None,
    is_app: bool | None = None,
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve availability of property valuation for a revision and role.

    Parameters
    ----------
    chosen_role : str, optional
        The user role for which to check availability.
    is_app : bool, optional
        Whether the check is performed in application context.
    revision_id : str, optional
        UUID of the policy revision.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response indicating valuation availability.
    """
    return _post(
        "/api/v2/settings/retrieve_property_valuation_availability",
        _build_payload(
            chosen_role=chosen_role,
            is_app=is_app,
            revision_id=revision_id,
        ),
        **kwargs,
    )


def retrieve_system_tags(
    level: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve system tags, optionally filtered by level.

    Parameters
    ----------
    level : str, optional
        Tag level to filter by.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the matching system tags.
    """
    return _post(
        "/api/v2/settings/retrieve_system_tags",
        _build_payload(level=level),
        **kwargs,
    )


def set_pdf_engine(
    engine: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set the PDF engine used for document generation.

    Parameters
    ----------
    engine : str, optional
        Name of the PDF engine to activate.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the update.
    """
    return _post(
        "/api/v2/settings/set_pdf_engine",
        _build_payload(engine=engine),
        **kwargs,
    )


def set_setting_value(
    option: str | None = None,
    section: str | None = None,
    value: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set the value of a specific system setting.

    Parameters
    ----------
    option : str, optional
        The setting option (key) to update.
    section : str, optional
        The settings section the option belongs to.
    value : str, optional
        The new value to assign.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the update.
    """
    return _post(
        "/api/v2/settings/set_setting_value",
        _build_payload(option=option, section=section, value=value),
        **kwargs,
    )


__all__ = [
    "add_city_to_zip_override",
    "add_counties_to_state",
    "add_county_to_zip_override",
    "get_pdf_engine",
    "get_setting_value",
    "get_system_tags_list",
    "retrieve_credit_permission_prompt",
    "retrieve_property_valuation_availability",
    "retrieve_system_tags",
    "set_pdf_engine",
    "set_setting_value",
]
