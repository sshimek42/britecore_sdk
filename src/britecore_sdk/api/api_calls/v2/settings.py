"""BriteCore v2 Settings API endpoint wrappers.

This module provides wrappers for settings, ZIP override, PDF engine, and
system-tag endpoints in the BriteCore v2 settings API.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


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
    return post(
        "/api/v2/settings/add_city_to_zip_override",
        build_payload(
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
    return post(
        "/api/v2/settings/add_counties_to_state",
        build_payload(counties=counties, country=country, state=state),
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
    return post(
        "/api/v2/settings/add_county_to_zip_override",
        build_payload(
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
    return post("/api/v2/settings/get_pdf_engine", {}, **kwargs)


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
    return post(
        "/api/v2/settings/get_setting_value",
        build_payload(option=option, section=section),
        **kwargs,
    )


def get_system_tags_list(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the complete system tag list.

    This wrapper calls ``/api/v2/settings/get_system_tags_list`` and returns
    the normalized ``process_result(...)`` payload for the available system
    tags. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post("/api/v2/settings/get_system_tags_list", {}, **kwargs)


def retrieve_credit_permission_prompt(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the configured credit permission prompt.

    This wrapper calls ``/api/v2/settings/retrieve_credit_permission_prompt``
    and returns the normalized ``process_result(...)`` payload for the prompt
    text shown to users. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post("/api/v2/settings/retrieve_credit_permission_prompt", {}, **kwargs)


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
    return post(
        "/api/v2/settings/retrieve_property_valuation_availability",
        build_payload(
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
    return post(
        "/api/v2/settings/retrieve_system_tags",
        build_payload(level=level),
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
    return post(
        "/api/v2/settings/set_pdf_engine",
        build_payload(engine=engine),
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
    return post(
        "/api/v2/settings/set_setting_value",
        build_payload(option=option, section=section, value=value),
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

# --- Autogenerated spec wrappers ---


def create_carbone_custom_deliverable(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/create_carbone_custom_deliverable``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/create_carbone_custom_deliverable",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/create_carbone_custom_deliverable"
    )


def create_system_tags(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/create_system_tags``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/create_system_tags",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/create_system_tags"
    )


def delete_carbone_custom_deliverable(
    id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/delete_carbone_custom_deliverable``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/delete_carbone_custom_deliverable",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/delete_carbone_custom_deliverable"
    )


def get_deliverable_preview_json(
    entity_id: Any | None = None,
    deliverable_id: Any | None = None,
    entity_type: Any | None = None,
    entity_number: Any | None = None,
    policy_type_name: Any | None = None,
    location_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/get_deliverable_preview_json``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "entity_id": entity_id,
        "deliverable_id": deliverable_id,
        "entity_type": entity_type,
        "entity_number": entity_number,
        "policy_type_name": policy_type_name,
        "location_id": location_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/get_deliverable_preview_json",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/get_deliverable_preview_json"
    )


def list_cancellation_reasons(
    ids: list[str] | None = None,
    policy_life_cycle_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/list_cancellation_reasons``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "ids": ids,
        "policy_life_cycle_ids": policy_life_cycle_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/list_cancellation_reasons",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/list_cancellation_reasons"
    )


def list_system_tags(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/list_system_tags``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/list_system_tags",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/list_system_tags"
    )


def new_permission_level_rule_dashboard(
    permission_level_id: str | None = None,
    is_primary: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/new_permission_level_rule_dashboard``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "permission_level_id": permission_level_id,
        "is_primary": is_primary,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/new_permission_level_rule_dashboard",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/new_permission_level_rule_dashboard"
    )


def persist_carbone_draft(
    new_draft_filename: Any | None = None,
    deliverable_id: Any | None = None,
    new_draft_id: Any | None = None,
    prior_draft_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/persist_carbone_draft``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "new_draft_filename": new_draft_filename,
        "deliverable_id": deliverable_id,
        "new_draft_id": new_draft_id,
        "prior_draft_id": prior_draft_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/persist_carbone_draft",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/persist_carbone_draft"
    )


def remove_permission_level_rule_dashboard(
    permission_level_rule_dashboard_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/remove_permission_level_rule_dashboard``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "permission_level_rule_dashboard_id": permission_level_rule_dashboard_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/remove_permission_level_rule_dashboard",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result,
        endpoint="/api/v2/settings/remove_permission_level_rule_dashboard",
    )


def retrieve_permissions(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/retrieve_permissions``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/retrieve_permissions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/retrieve_permissions"
    )


def retrieve_quick_code_value_tags(
    quick_code: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/retrieve_quick_code_value_tags``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "quick_code": quick_code,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/retrieve_quick_code_value_tags",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/retrieve_quick_code_value_tags"
    )


def retrieve_template_setup(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/retrieve_template_setup``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/retrieve_template_setup",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/retrieve_template_setup"
    )


def update_carbone_custom_deliverable(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/update_carbone_custom_deliverable``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/update_carbone_custom_deliverable",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result, endpoint="/api/v2/settings/update_carbone_custom_deliverable"
    )


def update_permission_level_rule_dashboard(
    permission_level_rule_dashboard_id: str | None = None,
    dashboard_id: str | None = None,
    is_primary: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/settings/update_permission_level_rule_dashboard``."""
    from britecore_sdk.api.api_calls import api_client as _api_client

    request_json: dict[str, Any] = {
        "permission_level_rule_dashboard_id": permission_level_rule_dashboard_id,
        "dashboard_id": dashboard_id,
        "is_primary": is_primary,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = _api_client.do_request(
        path="/api/v2/settings/update_permission_level_rule_dashboard",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return _api_client.process_result(
        request_result,
        endpoint="/api/v2/settings/update_permission_level_rule_dashboard",
    )


__all__.extend(
    [
        "create_carbone_custom_deliverable",
        "create_system_tags",
        "delete_carbone_custom_deliverable",
        "get_deliverable_preview_json",
        "list_cancellation_reasons",
        "list_system_tags",
        "new_permission_level_rule_dashboard",
        "persist_carbone_draft",
        "remove_permission_level_rule_dashboard",
        "retrieve_permissions",
        "retrieve_quick_code_value_tags",
        "retrieve_template_setup",
        "update_carbone_custom_deliverable",
        "update_permission_level_rule_dashboard",
    ]
)
