"""BriteCore v2 Async Policies API endpoint wrappers.

Asynchronous (cached) counterparts to the synchronous wrappers in policies.py.
Uses AsyncBritecoreAPIClient for non-blocking, TTL-cached HTTP requests.

Read operations (retrieve_policy, retrieve_revision_details, etc.) are cached
with a short TTL by default.  Mutation operations (create, cancel, reinstate,
etc.) automatically invalidate the policy cache namespace on success.
"""

from logging import Logger
from typing import Any, Literal, Unpack

from urllib3.util import Timeout

from britecore_libraries import BritecoreError, logger
from britecore_libraries.api.api_calls import (
    AsyncBritecoreAPIClient,
    RequestParameters,
    async_api_client,
)

LOGGER: Logger = logger

API_CLIENT: AsyncBritecoreAPIClient = async_api_client
POLICY_CACHE_NAMESPACE = "policies"
DEFAULT_CACHE_TTL_SECONDS = 60


def _apply_policy_read_cache(
    kwargs: dict[str, Any], *, cache_key_parts: list[str] | None = None
) -> dict[str, Any]:
    """Apply default caching for policy read requests while allowing overrides."""
    kwargs.setdefault("cache_enabled", True)
    kwargs.setdefault("cache_namespace", POLICY_CACHE_NAMESPACE)
    kwargs.setdefault("cache_ttl_seconds", DEFAULT_CACHE_TTL_SECONDS)
    if cache_key_parts:
        kwargs.setdefault("cache_key_parts", cache_key_parts)
    return kwargs


def _apply_policy_mutation_cache(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Invalidate cached policy reads after a successful mutation."""
    kwargs.setdefault("cache_invalidate_on_success", [POLICY_CACHE_NAMESPACE])
    return kwargs


async def _ensure_long_timeout(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Apply the configured long timeout when the caller did not provide one."""
    if not kwargs.get("request_timeout"):
        client = await API_CLIENT.aget_client()
        long_timeout = getattr(client, "web_timeout_long", None) or 50
        kwargs["request_timeout"] = Timeout(long_timeout)
    return kwargs


async def aretrieve_policy(
    policy_number: str | None = None,
    policy_id: str | None = None,
    revision_state: str | None = None,
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy information with cache enabled by default."""
    LOGGER.debug("Retrieving policy")
    client = await API_CLIENT.aget_client()
    verification_list: list[dict[str, str | None]] = [
        {"policy_number": policy_number},
        {"policy_id": policy_id},
        {"revision_id": revision_id},
    ]
    priority_list: list[str] = ["revision_id", "policy_id", "policy_number"]
    policy_request_json = client.multiple_parameter_verification(
        verification_list, priority_list
    )
    if revision_state:
        policy_request_json.update({"revision_state": revision_state})

    request_kwargs = await _ensure_long_timeout(dict(kwargs))
    cache_parts = [
        f"revision_id:{revision_id}" if revision_id else "",
        f"policy_id:{policy_id}" if policy_id else "",
        f"policy_number:{policy_number}" if policy_number else "",
        f"revision_state:{revision_state}" if revision_state else "",
    ]
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/retrieve_policy",
        json=policy_request_json,
        **_apply_policy_read_cache(
            request_kwargs, cache_key_parts=[part for part in cache_parts if part]
        ),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aadd_line_item(
    revision_id: str,
    item_id: str,
    property_id: str | None = "",
    sub_line_id: str | None = "",
    link_id: str | None = "",
    check_for_subline: bool | None = False,
    **kwargs: Unpack[RequestParameters],
) -> bool:
    """Add a line item and invalidate cached policy reads on success."""
    LOGGER.debug("Adding line")
    line_add_json = {
        key: value
        for key, value in {
            "revision_id": revision_id,
            "item_id": item_id,
            "property_id": property_id,
            "sub_line_id": sub_line_id,
            "link_id": link_id,
            "check_for_subline": check_for_subline,
        }.items()
        if value not in (None, "")
    }
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/add_line_item",
        json=line_add_json,
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    line_json = await API_CLIENT.aprocess_result(request_result)
    if line_json is not None:
        LOGGER.debug(line_json["added_items"])
        return bool(line_json["added_items"])
    return False


async def aretrieve_policy_ids(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> tuple[str, str]:
    """Retrieve the active revision and property IDs for a policy number."""
    LOGGER.debug("Getting policy info")
    policy_json = await aretrieve_policy(policy_number=policy_number, **kwargs)
    active_revision = policy_json["active_revision"]
    return active_revision["id"], active_revision["primary_property_id"]


async def aretrieve_policy_contact_info(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> list[Any]:
    """Retrieve named insured contact information for a policy."""
    LOGGER.debug("Getting contact info")
    contact_json = await aretrieve_policy(policy_number=policy_number, **kwargs)
    return contact_json["active_revision"]["named_insureds"]


async def acreate_policy(
    policy_number: str | None = "",
    policy_type_id: str | None = "",
    inception_date: str | None = "",
    term_type: Literal[
        "Custom", "3 Years", "18 Months", "1 Year", "9 Months", "6 Months", "3 Months"
    ]
    | None = "1 Year",
    expiration_date: str | None = "",
    renewal_term_type: Literal[
        "3 Years", "18 Months", "1 Year", "9 Months", "6 Months", "3 Months"
    ]
    | None = "1 Year",
    is_renewal: bool | None = False,
    as_agent: bool | None = False,
    manual_policy_number: bool | None = True,
    effective_date: str | None = "",
    property_zip: str | None = "",
    underwriting_questions: list[Any] | None = None,
    underwriting_options: list[Any] | None = None,
    external_system_reference: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, str]:
    """Create a policy and invalidate cached policy reads on success."""
    if term_type == "Custom" and not expiration_date:
        raise BritecoreError.MissingParameter(
            "expiration_date needed with 'Custom' term_type"
        )

    LOGGER.debug(f"Creating policy %f.yellow%{policy_number}%f%")
    policy_request_json = {
        key: value
        for key, value in {
            "policy_number": policy_number,
            "policy_type_id": policy_type_id,
            "inception_date": inception_date,
            "term_type": term_type,
            "expiration_date": expiration_date,
            "renewal_term_type": renewal_term_type,
            "is_renewal": is_renewal,
            "as_agent": as_agent,
            "manual_policy_number": manual_policy_number,
            "effective_date": effective_date,
            "property_zip": property_zip,
            "underwriting_questions": underwriting_questions,
            "underwriting_options": underwriting_options,
            "external_system_reference": external_system_reference,
        }.items()
        if value not in (None, "")
    }
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/create_policy",
        json=policy_request_json,
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    policy_json = await API_CLIENT.aprocess_result(request_result)
    return policy_json, policy_json["revision_id"]


async def aretrieve_policy_terms(
    policy_id: str | None = "",
    policy_number: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy terms with caching enabled by default."""
    LOGGER.debug("Retrieving terms")
    if not policy_number and not policy_id:
        raise BritecoreError.MissingParameter(
            "Either policy_id or policy_number is required"
        )

    client = await API_CLIENT.aget_client()
    parameter_list: list[dict[str, str]] = [
        {"policy_id": policy_id},
        {"policy_number": policy_number},
    ]
    parameter_priority: list[str] = ["policy_id", "policy_number"]
    policy_retrieve_json = client.multiple_parameter_verification(
        parameter_list, parameter_priority
    )
    cache_parts = [
        f"policy_id:{policy_id}" if policy_id else "",
        f"policy_number:{policy_number}" if policy_number else "",
        "policy_terms",
    ]
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/retrieve_policy_terms",
        json=policy_retrieve_json,
        **_apply_policy_read_cache(
            dict(kwargs), cache_key_parts=[p for p in cache_parts if p]
        ),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def arate_revision(revision_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Rate a revision and invalidate cached policy reads on success."""
    LOGGER.debug(f"Re-rating revision %f.yellow%{revision_id}%f%")
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/rate_revision",
        json={"revision_id": revision_id},
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aretrieve_revision_details(
    revision_id: str,
    include_contact_details: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve revision details with long timeout and caching enabled by default."""
    LOGGER.debug("Getting revision")
    request_kwargs = await _ensure_long_timeout(dict(kwargs))
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/retrieve_revision_details",
        json={
            "revision_id": revision_id,
            "include_contact_details": include_contact_details,
        },
        **_apply_policy_read_cache(
            request_kwargs,
            cache_key_parts=[
                f"revision_id:{revision_id}",
                f"include_contact_details:{include_contact_details}",
            ],
        ),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aretrieve_risks(
    revision_id: str,
    page: int | None = 0,
    page_size: int | None = 10,
    retrieve_remaining: bool | None = True,
    order_by: str | None = "name",
    risk_types: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve risks for a revision with caching enabled by default."""
    LOGGER.debug("Getting risks")
    revision_retrieve_json = {
        key: value
        for key, value in {
            "revision_id": revision_id,
            "page": page,
            "page_size": page_size,
            "retrieve_remaining": retrieve_remaining,
            "order_by": order_by,
            "risk_types": risk_types,
        }.items()
        if value is not None
    }
    cache_parts = [
        f"revision_id:{revision_id}",
        f"page:{page}",
        f"page_size:{page_size}",
        f"retrieve_remaining:{retrieve_remaining}",
        f"order_by:{order_by}",
    ]
    if risk_types:
        cache_parts.extend(f"risk_type:{risk_type}" for risk_type in risk_types)
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/retrieve_risks",
        json=revision_retrieve_json,
        **_apply_policy_read_cache(dict(kwargs), cache_key_parts=cache_parts),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aretrieve_risk_details(
    risk_id: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve risk details with caching enabled by default."""
    LOGGER.debug("Getting risk details")
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/retrieve_risk_details",
        json={"risk_id": risk_id},
        **_apply_policy_read_cache(
            dict(kwargs), cache_key_parts=[f"risk_id:{risk_id}"]
        ),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aupdate_rating_information(
    property_id: str | None = "",
    revision_id: str | None = "",
    items: list[dict[str, Any]] | None = None,
    reset_premium: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update rating information and invalidate cached policy reads on success."""
    LOGGER.debug("Updating line item")
    revision_retrieve_json = {
        key: value
        for key, value in {
            "property_id": property_id,
            "revision_id": revision_id,
            "items": items,
            "reset_premium": reset_premium,
        }.items()
        if value is not None and value != ""
    }
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/update_rating_information",
        json=revision_retrieve_json,
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def arate_risk(risk_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Rate a risk and invalidate cached policy reads on success."""
    LOGGER.debug("Re-rating policy")
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/rate_risk",
        json={"risk_id": risk_id},
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def anew_revision_contact(
    revision_id: str,
    contact_id: str,
    x_id: str | None = None,
    contact_role: Literal[
        "namedInsured", "addtlInterest", "financeCompany", "underwriter", "driver"
    ]
    | None = "namedInsured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a contact to a revision and invalidate cached policy reads on success."""
    LOGGER.debug("Adding contact")
    request_kwargs = _apply_policy_mutation_cache(dict(kwargs))
    request_result = None
    contact_add_result: Any
    contact_add_json = {"revision_id": revision_id, "role": contact_role}

    if not x_id:
        request_result = await API_CLIENT.ado_request(
            path="/api/v2/policies/new_revision_contact",
            json=contact_add_json,
            **request_kwargs,
        )
        contact_add_result = await API_CLIENT.aprocess_result(request_result)
    else:
        contact_add_result = {"x_revisions_contact_id": x_id}

    if contact_add_result:
        x_contact = contact_add_result["x_revisions_contact_id"]
        update_revision_json = {
            "x_revisions_contact_id": x_contact,
            "contact_id": contact_id,
        }
        request_result = await API_CLIENT.ado_request(
            path="/api/v2/policies/update_revision_contact",
            json=update_revision_json,
            **request_kwargs,
        )

    return await API_CLIENT.aprocess_result(request_result)


async def acreate_risk(
    revision_id: str,
    property_group_number: int | None = None,
    building_number: int | None = None,
    force_categories: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a risk and invalidate cached policy reads on success."""
    risk_json = {
        key: value
        for key, value in {
            "revision_id": revision_id,
            "property_group_number": property_group_number,
            "building_number": building_number,
            "force_categories": force_categories,
        }.items()
        if value is not None
    }
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/create_risk",
        json=risk_json,
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aupdate_property_location(
    location: dict[str, Any],
    soft_geoservice_bypass: bool | None = None,
    hard_geoservice_bypass: bool | None = None,
    reset_premiums: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update property location and invalidate cached policy reads on success."""
    prop_json = {
        "location": {
            key: value
            for key, value in {
                "location": location,
                "soft_geoservice_bypass": soft_geoservice_bypass,
                "hard_geoservice_bypass": hard_geoservice_bypass,
                "reset_premiums": reset_premiums,
            }.items()
            if value is not None
        }
    }
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/update_property_location",
        json=prop_json,
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def anew_mortgagee(property_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Create a new mortgagee and invalidate cached policy reads on success."""
    request_result = await API_CLIENT.ado_request(
        "/api/v2/policies/new_mortgagee",
        json={"property_id": property_id},
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def astore_mortgagee(
    property_contact_id: str,
    mortgagee_contact_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store a mortgagee and invalidate cached policy reads on success."""
    request_result = await API_CLIENT.ado_request(
        "/api/v2/policies/store_mortgagee",
        json={
            "x_properties_contact_id": property_contact_id,
            "mortgagee_contact_id": mortgagee_contact_id,
        },
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aretrieve_policy_snapshot(
    policy_number: str, snapshot_date: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve a policy snapshot with caching enabled by default."""
    request_result = await API_CLIENT.ado_request(
        "/api/v2/policies/retrieve_policy_snapshot",
        json={"policy_number": policy_number, "snapshot_date": snapshot_date},
        **_apply_policy_read_cache(
            dict(kwargs),
            cache_key_parts=[
                f"policy_number:{policy_number}",
                f"snapshot_date:{snapshot_date}",
                "snapshot",
            ],
        ),
    )
    return await API_CLIENT.aprocess_result(request_result)


__all__ = [
    "aadd_line_item",
    "acreate_policy",
    "acreate_risk",
    "anew_mortgagee",
    "anew_revision_contact",
    "arate_revision",
    "arate_risk",
    "aretrieve_policy",
    "aretrieve_policy_contact_info",
    "aretrieve_policy_ids",
    "aretrieve_policy_snapshot",
    "aretrieve_policy_terms",
    "aretrieve_revision_details",
    "aretrieve_risk_details",
    "aretrieve_risks",
    "astore_mortgagee",
    "aupdate_property_location",
    "aupdate_rating_information",
]
