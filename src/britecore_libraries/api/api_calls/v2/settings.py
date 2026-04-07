"""BriteCore v2 Settings API endpoint wrappers.

This module provides wrappers for settings, ZIP override, PDF engine, and
system-tag endpoints in the BriteCore v2 settings API.
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
    """Add a city override for a ZIP code.

    This wrapper sends the ZIP override fields to
    ``/api/v2/settings/add_city_to_zip_override`` and returns the normalized
    ``process_result(...)`` payload for the update request. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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
    """Add county records to a state.

    This wrapper sends ``counties``, ``country``, and ``state`` to
    ``/api/v2/settings/add_counties_to_state`` and returns the normalized
    ``process_result(...)`` payload for the update request. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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
    """Add a county override for a ZIP code.

    This wrapper sends the county override fields to
    ``/api/v2/settings/add_county_to_zip_override`` and returns the normalized
    ``process_result(...)`` payload for the update request. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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
    """Retrieve the active PDF engine setting.

    This wrapper calls ``/api/v2/settings/get_pdf_engine`` and returns the
    normalized ``process_result(...)`` payload for the configured PDF engine.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post("/api/v2/settings/get_pdf_engine", {}, **kwargs)


def get_setting_value(
    option: str | None = None,
    section: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a specific system setting value.

    This wrapper sends ``option`` and ``section`` to
    ``/api/v2/settings/get_setting_value`` and returns the normalized
    ``process_result(...)`` payload for the requested setting. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/settings/get_setting_value",
        _build_payload(option=option, section=section),
        **kwargs,
    )


def get_system_tags_list(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the complete system tag list.

    This wrapper calls ``/api/v2/settings/get_system_tags_list`` and returns
    the normalized ``process_result(...)`` payload for the available system
    tags. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post("/api/v2/settings/get_system_tags_list", {}, **kwargs)


def retrieve_credit_permission_prompt(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the configured credit permission prompt.

    This wrapper calls ``/api/v2/settings/retrieve_credit_permission_prompt``
    and returns the normalized ``process_result(...)`` payload for the prompt
    text shown to users. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post("/api/v2/settings/retrieve_credit_permission_prompt", {}, **kwargs)


def retrieve_property_valuation_availability(
    chosen_role: str | None = None,
    is_app: bool | None = None,
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check property valuation availability for a revision.

    This wrapper sends ``chosen_role``, ``is_app``, and ``revision_id`` to
    ``/api/v2/settings/retrieve_property_valuation_availability`` and returns
    the normalized ``process_result(...)`` payload describing valuation
    availability. ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends the optional ``level`` filter to
    ``/api/v2/settings/retrieve_system_tags`` and returns the normalized
    ``process_result(...)`` payload for the matching tags. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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

    This wrapper sends ``engine`` to ``/api/v2/settings/set_pdf_engine`` and
    returns the normalized ``process_result(...)`` payload for the update
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``option``, ``section``, and ``value`` to
    ``/api/v2/settings/set_setting_value`` and returns the normalized
    ``process_result(...)`` payload for the update request. ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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
