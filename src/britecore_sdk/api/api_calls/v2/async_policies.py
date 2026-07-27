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

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
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
    """Apply default caching for policy read requests while allowing overrides.."""
    kwargs.setdefault("cache_enabled", True)
    kwargs.setdefault("cache_namespace", POLICY_CACHE_NAMESPACE)
    kwargs.setdefault("cache_ttl_seconds", DEFAULT_CACHE_TTL_SECONDS)
    if cache_key_parts:
        kwargs.setdefault("cache_key_parts", cache_key_parts)
    return kwargs


def _apply_policy_mutation_cache(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Invalidate cached policy reads after a successful mutation.."""
    kwargs.setdefault("cache_invalidate_on_success", [POLICY_CACHE_NAMESPACE])
    return kwargs


async def _ensure_long_timeout(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Apply the configured long timeout when the caller did not provide one.."""
    if not kwargs.get("request_timeout"):
        client = await API_CLIENT.aget_client()
        long_timeout = getattr(client, "web_timeout_long", None) or 50
        kwargs["request_timeout"] = Timeout(long_timeout)
    return kwargs


async def aretrieve_policy(
    policy_number: str | None = None,
    policy_id: str | None = None,
    revision_state: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve top-level policy information asynchronously.."""
    LOGGER.debug("Retrieving policy")
    client = await API_CLIENT.aget_client()
    verification_list: list[dict[str, str | None]] = [
        {"policy_number": policy_number},
        {"policy_id": policy_id},
    ]
    priority_list: list[str] = ["policy_id", "policy_number"]
    policy_request_json = client.multiple_parameter_verification(
        verification_list, priority_list
    )
    if revision_state:
        policy_request_json.update({"revision_state": revision_state})

    request_kwargs = await _ensure_long_timeout(dict(kwargs))
    cache_parts = [
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aretrieve_policy")
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
    """Add a line item to a revision or property asynchronously.

    POST /api/v2/policies/add_line_item
    """
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aadd_line_item")
    line_json = await API_CLIENT.aprocess_result(request_result)
    if line_json is not None:
        LOGGER.debug(line_json["added_items"])
        return bool(line_json["added_items"])
    return False


async def aretrieve_policy_ids(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> tuple[str, str]:
    """Retrieve the active revision ID and primary property ID for a policy.

    POST /api/v2/policies/retrieve_policy
    """
    LOGGER.debug("Getting policy info")
    policy_json = await aretrieve_policy(policy_number=policy_number, **kwargs)
    active_revision = policy_json["active_revision"]
    return active_revision["id"], active_revision["primary_property_id"]


async def aretrieve_policy_contact_info(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> list[Any]:
    """Retrieve named insured contact information for a policy.

    POST /api/v2/policies/retrieve_policy
    """
    LOGGER.debug("Getting contact info")
    contact_json = await aretrieve_policy(policy_number=policy_number, **kwargs)
    return contact_json["active_revision"]["named_insureds"]


async def acreate_policy(
    policy_number: str | None = "",
    policy_type_id: str | None = "",
    inception_date: str | None = "",
    term_type: (
        Literal[
            "Custom",
            "3 Years",
            "18 Months",
            "1 Year",
            "9 Months",
            "6 Months",
            "3 Months",
        ]
        | None
    ) = "1 Year",
    expiration_date: str | None = "",
    renewal_term_type: (
        Literal["3 Years", "18 Months", "1 Year", "9 Months", "6 Months", "3 Months"]
        | None
    ) = "1 Year",
    is_renewal: bool | None = False,
    as_agent: bool | None = False,
    manual_policy_number: bool | None = True,
    effective_date: str | None = "",
    property_zip: str | None = "",
    underwriting_questions: list[Any] | None = None,
    underwriting_options: list[Any] | None = None,
    external_system_reference: str | None = "",
    client: AsyncBritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, str]:
    """Create a new policy asynchronously.

    The payload mirrors ``/api/v2/policies/create_policy`` and accepts policy,
    term, underwriting, and external reference fields, including the documented
    custom-term expiration requirement. Returns the async ``aprocess_result(...)``
    payload together with the new ``revision_id``, invalidates cached policy reads
    on success, and accepts ``RequestParameters`` overrides.

    Args:
        policy_number: The policy number (default empty string).
        policy_type_id: The policy type identifier.
        inception_date: Policy inception date.
        term_type: The term type (default '1 Year'). When 'Custom', expiration_date
            is required.
        expiration_date: Policy expiration date (required when term_type is 'Custom').
        renewal_term_type: The renewal term type (default '1 Year').
        is_renewal: Whether this is a renewal policy (default False).
        as_agent: Whether creating as an agent (default False).
        manual_policy_number: Whether the policy number is manually entered (default True).
        effective_date: Policy effective date.
        property_zip: Primary property ZIP code.
        underwriting_questions: List of underwriting question responses.
        underwriting_options: List of underwriting option selections.
        external_system_reference: External system reference identifier.
        **kwargs: Additional request parameters and cache invalidation settings.

    Returns:
        tuple[Any, str]: A tuple of (processed_policy_data, revision_id).

    Raises:
        BritecoreError.MissingParameter: When term_type is 'Custom' but
            expiration_date is not provided.
        RuntimeError: When ado_request returns None.
    """
    if term_type == "Custom" and not expiration_date:
        raise BritecoreError.MissingParameter(
            "expiration_date needed with 'Custom' term_type"
        )

    LOGGER.debug("Creating policy '%s'", policy_number)
    effective_client: AsyncBritecoreAPIClient = client or API_CLIENT
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
    request_result = await effective_client.ado_request(
        path="/api/v2/policies/create_policy",
        json=policy_request_json,
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for acreate_policy")
    policy_json = await effective_client.aprocess_result(request_result)
    return policy_json, policy_json["revision_id"]


async def aretrieve_policy_terms(
    policy_id: str | None = "",
    policy_number: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy terms and revisions asynchronously.

    POST /api/v2/policies/retrieve_policy_terms
    """
    LOGGER.debug("Retrieving terms")
    if not policy_number and not policy_id:
        raise BritecoreError.MissingParameter(
            "Either policy_id or policy_number is required"
        )

    client = await API_CLIENT.aget_client()
    parameter_list: list[dict[str, str | None]] = [
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aretrieve_policy_terms")
    return await API_CLIENT.aprocess_result(request_result)


async def arate_revision(revision_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Calculate a rate for a revision asynchronously.

    POST /api/v2/policies/rate_revision
    """
    LOGGER.debug("Re-rating revision '%s'", revision_id)
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/rate_revision",
        json={"revision_id": revision_id},
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for arate_revision")
    return await API_CLIENT.aprocess_result(request_result)


async def aretrieve_revision_details(
    revision_id: str,
    include_contact_details: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve detailed revision information asynchronously.

    POST /api/v2/policies/retrieve_revision_details
    """
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aretrieve_revision_details")
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
    """Retrieve paginated or filtered risks for a revision asynchronously.

    POST /api/v2/policies/retrieve_risks
    """
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aretrieve_risks")
    return await API_CLIENT.aprocess_result(request_result)


async def aretrieve_risk_details(
    risk_id: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve risk details asynchronously.

    POST /api/v2/policies/retrieve_risk_details
    """
    LOGGER.debug("Getting risk details")
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/retrieve_risk_details",
        json={"risk_id": risk_id},
        **_apply_policy_read_cache(
            dict(kwargs), cache_key_parts=[f"risk_id:{risk_id}"]
        ),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for aretrieve_risk_details")
    return await API_CLIENT.aprocess_result(request_result)


async def aupdate_rating_information(
    property_id: str | None = "",
    revision_id: str | None = "",
    items: list[dict[str, Any]] | None = None,
    reset_premium: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update rating information for a revision or property asynchronously.

    POST /api/v2/policies/update_rating_information
    """
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aupdate_rating_information")
    return await API_CLIENT.aprocess_result(request_result)


async def arate_risk(risk_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Calculate a rate for a risk asynchronously.

    POST /api/v2/policies/rate_risk
    """
    LOGGER.debug("Re-rating policy")
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/policies/rate_risk",
        json={"risk_id": risk_id},
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for arate_risk")
    return await API_CLIENT.aprocess_result(request_result)


async def anew_revision_contact(
    revision_id: str,
    contact_id: str,
    x_id: str | None = None,
    contact_role: (
        Literal[
            "namedInsured", "addtlInterest", "financeCompany", "underwriter", "driver"
        ]
        | None
    ) = "namedInsured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add or update a contact assignment on a revision asynchronously.

    The workflow uses ``revision_id``, ``contact_id``, and ``contact_role`` to
    create or reuse an ``x_revisions_contact_id`` before updating the revision
    contact link. Returns the async ``aprocess_result(...)`` payload, invalidates
    cached policy reads on success, and accepts ``RequestParameters`` overrides.

    Args:
        revision_id: The revision identifier.
        contact_id: The contact identifier to assign.
        x_id: Optional existing x_revisions_contact_id (creates new if not provided).
        contact_role: The role for the contact assignment (default 'namedInsured').
        **kwargs: Additional request parameters and cache invalidation settings.

    Returns:
        Any: The processed result from the final update_revision_contact call.

    Raises:
        RuntimeError: Multiple conditions when ado_request returns None for any operation,
            or KeyError when contact_add_result missing 'x_revisions_contact_id' key.
    """
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
        if request_result is None:
            raise RuntimeError(
                "ado_request returned None for anew_revision_contact (new_revision_contact)"
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
        if request_result is None:
            raise RuntimeError(
                "ado_request returned None for anew_revision_contact (update_revision_contact)"
            )

    if request_result is None:
        raise RuntimeError(
            "ado_request returned None for anew_revision_contact (final)"
        )
    return await API_CLIENT.aprocess_result(request_result)


async def acreate_risk(
    revision_id: str,
    property_group_number: int | None = None,
    building_number: int | None = None,
    force_categories: bool | None = None,
    client: AsyncBritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a risk for a revision asynchronously.

    POST /api/v2/policies/create_risk
    """
    effective_client: AsyncBritecoreAPIClient = client or API_CLIENT
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
    request_result = await effective_client.ado_request(
        path="/api/v2/policies/create_risk",
        json=risk_json,
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for acreate_risk")
    return await effective_client.aprocess_result(request_result)


async def aupdate_property_location(
    location: dict[str, Any],
    soft_geoservice_bypass: bool | None = None,
    hard_geoservice_bypass: bool | None = None,
    reset_premiums: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update property location details asynchronously.

    POST /api/v2/policies/update_property_location
    """
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aupdate_property_location")
    return await API_CLIENT.aprocess_result(request_result)


async def anew_mortgagee(property_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Create a new mortgagee for a property asynchronously.

    POST /api/v2/policies/new_mortgagee
    """
    request_result = await API_CLIENT.ado_request(
        "/api/v2/policies/new_mortgagee",
        json={"property_id": property_id},
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for anew_mortgagee")
    return await API_CLIENT.aprocess_result(request_result)


async def astore_mortgagee(
    property_contact_id: str,
    mortgagee_contact_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store mortgagee information for a property contact asynchronously.

    POST /api/v2/policies/store_mortgagee
    """
    request_result = await API_CLIENT.ado_request(
        "/api/v2/policies/store_mortgagee",
        json={
            "x_properties_contact_id": property_contact_id,
            "mortgagee_contact_id": mortgagee_contact_id,
        },
        **_apply_policy_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for astore_mortgagee")
    return await API_CLIENT.aprocess_result(request_result)


async def aretrieve_policy_snapshot(
    policy_number: str, snapshot_date: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve a policy snapshot asynchronously.

    POST /api/v2/policies/retrieve_policy_snapshot
    """
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for aretrieve_policy_snapshot")
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


async def alist_policies(
    page: int = 1,
    limit: int = 100,
    client: AsyncBritecoreAPIClient | None = None,
    **kwargs: Any,
) -> Any:
    """Return a paginated list of policies (async).

    Pagination helper for ``aiter_policies``.  Calls
    ``/api/v2/policies/search`` and normalises the result to
    ``{"data": [...]}``.

    Args:
        page: Page number (1-based).
        limit: Results per page.
        client: Optional explicit async client; defaults to module-level client.
        **kwargs: Additional request parameters.

    Returns:
        Normalized response dict ``{"data": [...]}``.
    """
    _client = client if client is not None else API_CLIENT
    request_json: dict[str, Any] = {
        "sort_obj": {"field": "policy_number", "order": "asc"},
        "current_page": page,
        "page_size": limit,
    }
    request_result = await _client.ado_request(
        path="/api/v2/policies/search",
        json=request_json,
        **kwargs,
    )
    if request_result is None:
        return {"data": []}
    raw = await _client.aprocess_result(request_result)
    if isinstance(raw, dict) and "records" in raw:
        return {"data": raw["records"]}
    if isinstance(raw, list):
        return {"data": raw}
    return {"data": []}
