"""BriteCore v2 Async Policies API endpoint wrappers.

Asynchronous (cached) counterparts to the synchronous wrappers in policies.py.
Uses AsyncBritecoreAPIClient for non-blocking, TTL-cached HTTP requests.

Read operations (retrieve_policy, retrieve_revision_details, etc.) are cached
with a short TTL by default.  Mutation operations (create, cancel, reinstate,
etc.) automatically invalidate the policy cache namespace on success.
"""

import asyncio
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
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve top-level policy information asynchronously.

    The request accepts ``policy_id`` or ``policy_number`` with optional
    ``revision_state`` and follows the same identifier-priority rules as the
    synchronous wrapper. Returns the async ``aprocess_result(...)`` payload,
    enables cached reads by default, and accepts ``RequestParameters`` plus
    cache overrides.
    """
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

    Use ``revision_id`` and ``item_id`` with optional property or sub-line
    linkage fields to call ``/api/v2/policies/add_line_item``. Returns a boolean
    derived from the async ``aprocess_result(...)`` payload, invalidates cached
    policy reads on success, and accepts ``RequestParameters`` overrides.
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

    This convenience helper delegates to ``aretrieve_policy``
    (``/api/v2/policies/retrieve_policy``) and then extracts identifiers from
    the active revision in the normalized ``aprocess_result(...)`` payload.
    Returns a ``(revision_id, primary_property_id)`` tuple while preserving any
    ``RequestParameters`` or cache overrides supplied via ``**kwargs``.
    """
    LOGGER.debug("Getting policy info")
    policy_json = await aretrieve_policy(policy_number=policy_number, **kwargs)
    active_revision = policy_json["active_revision"]
    return active_revision["id"], active_revision["primary_property_id"]


async def aretrieve_policy_contact_info(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> list[Any]:
    """Retrieve named insured contact information for a policy.

    This convenience helper delegates to ``aretrieve_policy``
    (``/api/v2/policies/retrieve_policy``) and returns the
    ``active_revision.named_insureds`` collection from the normalized
    ``aprocess_result(...)`` payload. It preserves any ``RequestParameters`` or
    cache overrides passed in ``**kwargs``.
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
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, str]:
    """Create a new policy asynchronously.

    The payload mirrors ``/api/v2/policies/create_policy`` and accepts policy,
    term, underwriting, and external reference fields, including the documented
    custom-term expiration requirement. Returns the async ``aprocess_result(...)``
    payload together with the new ``revision_id``, invalidates cached policy reads
    on success, and accepts ``RequestParameters`` overrides.
    """
    if term_type == "Custom" and not expiration_date:
        raise BritecoreError.MissingParameter(
            "expiration_date needed with 'Custom' term_type"
        )

    LOGGER.debug("Creating policy '%s'", policy_number)
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for acreate_policy")
    policy_json = await API_CLIENT.aprocess_result(request_result)
    return policy_json, policy_json["revision_id"]


async def aretrieve_policy_terms(
    policy_id: str | None = "",
    policy_number: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy terms and revisions asynchronously.

    Use either ``policy_id`` or ``policy_number`` to request the policy terms
    documented by ``/api/v2/policies/retrieve_policy_terms``. Returns the async
    ``aprocess_result(...)`` payload, enables cached reads by default, and accepts
    ``RequestParameters`` plus cache overrides.
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

    The request uses ``revision_id`` for ``/api/v2/policies/rate_revision`` and
    returns the async ``aprocess_result(...)`` payload for the rating operation.
    Cached policy reads are invalidated on success, and ``**kwargs`` accepts
    ``RequestParameters`` overrides.
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

    Use ``revision_id`` and optional ``include_contact_details`` to call
    ``/api/v2/policies/retrieve_revision_details`` with the long-timeout behavior
    used by the synchronous wrapper. Returns the async ``aprocess_result(...)``
    payload, enables cached reads by default, and accepts ``RequestParameters`` plus cache overrides.
    """
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

    The request uses ``revision_id`` with optional pagination, ordering, and
    ``risk_types`` filters to call ``/api/v2/policies/retrieve_risks``. Returns
    the async ``aprocess_result(...)`` payload, enables cached reads by default,
    and accepts ``RequestParameters`` plus cache overrides.
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

    Use ``risk_id`` to fetch the detailed risk information documented by
    ``/api/v2/policies/retrieve_risk_details``. Returns the async
    ``aprocess_result(...)`` payload, enables cached reads by default, and
    accepts ``RequestParameters`` plus cache overrides.
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

    The payload uses ``revision_id``, ``property_id``, ``items``, and
    ``reset_premium`` to call ``/api/v2/policies/update_rating_information``.
    Returns the async ``aprocess_result(...)`` payload, invalidates cached policy
    reads on success, and accepts ``RequestParameters`` overrides.
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

    Use ``risk_id`` with ``/api/v2/policies/rate_risk`` to recalculate the risk's
    premium information. Returns the async ``aprocess_result(...)`` payload,
    invalidates cached policy reads on success, and accepts ``RequestParameters`` overrides.
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
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a risk for a revision asynchronously.

    Use ``revision_id`` together with optional property-group, building, and
    ``force_categories`` values to call ``/api/v2/policies/create_risk``. Returns
    the async ``aprocess_result(...)`` payload, invalidates cached policy reads on
    success, and accepts ``RequestParameters`` overrides.
    """
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
    if request_result is None:
        raise RuntimeError("ado_request returned None for acreate_risk")
    return await API_CLIENT.aprocess_result(request_result)


async def aupdate_property_location(
    location: dict[str, Any],
    soft_geoservice_bypass: bool | None = None,
    hard_geoservice_bypass: bool | None = None,
    reset_premiums: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update property location details asynchronously.

    The request wraps the ``location`` payload and optional geo-service bypass or
    ``reset_premiums`` flags for ``/api/v2/policies/update_property_location``.
    Returns the async ``aprocess_result(...)`` payload, invalidates cached policy
    reads on success, and accepts ``RequestParameters`` overrides.
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

    Use ``property_id`` to create the mortgagee record documented by
    ``/api/v2/policies/new_mortgagee``. Returns the async
    ``aprocess_result(...)`` payload, invalidates cached policy reads on success,
    and accepts ``RequestParameters`` overrides.
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

    The request uses ``property_contact_id`` and ``mortgagee_contact_id`` to call
    ``/api/v2/policies/store_mortgagee``. Returns the async
    ``aprocess_result(...)`` payload, invalidates cached policy reads on success,
    and accepts ``RequestParameters`` overrides.
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

    Use ``policy_number`` and ``snapshot_date`` to load the policy snapshot
    documented by ``/api/v2/policies/retrieve_policy_snapshot``. Returns the
    async ``aprocess_result(...)`` payload, enables cached reads by default, and
    accepts ``RequestParameters`` plus cache overrides.
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
    "acreate_policies_batch",
    "acreate_policy",
    "acreate_risk",
    "acreate_risks_batch",
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


async def acreate_policies_batch(
    policies_json: list[dict[str, Any]],
    max_concurrent: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many policies concurrently and return per-item outcomes.

    This helper runs ``acreate_policy(...)`` with bounded concurrency so
    high-volume policy creation jobs complete much faster than fully serial
    execution.  Each payload dict is unpacked as keyword arguments to
    ``acreate_policy``.

    Args:
        policies_json: List of policy payload dicts forwarded as kwargs to
            ``acreate_policy``.
        max_concurrent: Maximum concurrent coroutines.  Default is ``3``
            (conservative because each policy create triggers heavy backend
            work).
        fail_fast: When ``True``, raises the first encountered exception and
            cancels remaining tasks.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each policy create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list of per-item outcome dicts with keys
              ``index``, ``success``, ``policy_data``, ``revision_id``, ``error``

    Raises:
        BritecoreError.MissingParameter: If ``policies_json`` is missing/empty.
        ValueError: If ``max_concurrent`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not policies_json or not isinstance(policies_json, list):
        raise BritecoreError.MissingParameter(
            "policies_json is required and must be a non-empty list"
        )
    if max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1")

    results: list[dict[str, Any] | None] = [None] * len(policies_json)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _create_one_semaphored(
        index: int, payload: dict[str, Any]
    ) -> tuple[int, Any, str | None]:
        async with semaphore:
            policy_data, revision_id = await acreate_policy(**payload, **kwargs)
            return index, policy_data, revision_id

    tasks = [
        asyncio.create_task(_create_one_semaphored(idx, payload))
        for idx, payload in enumerate(policies_json)
    ]

    if fail_fast:
        try:
            task_results = await asyncio.gather(*tasks)
            for result_idx, policy_data, revision_id in task_results:
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "policy_data": policy_data,
                    "revision_id": revision_id,
                    "error": None,
                }
        except Exception:
            for task in tasks:
                task.cancel()
            raise
    else:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)  # type: ignore[assignment]
        for idx, result in enumerate(task_results):
            if isinstance(result, Exception):
                results[idx] = {
                    "index": idx,
                    "success": False,
                    "policy_data": None,
                    "revision_id": None,
                    "error": str(result),
                }
            else:
                result_idx, policy_data, revision_id = result
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "policy_data": policy_data,
                    "revision_id": revision_id,
                    "error": None,
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(policies_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


async def acreate_risks_batch(
    risks_json: list[dict[str, Any]],
    max_concurrent: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many risks concurrently and return per-item outcomes.

    This helper runs ``acreate_risk(...)`` with bounded concurrency so
    high-volume risk creation jobs complete much faster than fully serial
    execution.  Each payload dict must include ``revision_id``; optional
    keys ``property_group_number``, ``building_number``, and
    ``force_categories`` are forwarded if present.

    Args:
        risks_json: List of risk payload dicts forwarded as kwargs to
            ``acreate_risk``.
        max_concurrent: Maximum concurrent coroutines.  Default is ``3``.
        fail_fast: When ``True``, raises the first encountered exception and
            cancels remaining tasks.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each risk create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list of per-item outcome dicts with keys
              ``index``, ``success``, ``risk_data``, ``risk_id``, ``error``

    Raises:
        BritecoreError.MissingParameter: If ``risks_json`` is missing/empty.
        ValueError: If ``max_concurrent`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not risks_json or not isinstance(risks_json, list):
        raise BritecoreError.MissingParameter(
            "risks_json is required and must be a non-empty list"
        )
    if max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1")

    results: list[dict[str, Any] | None] = [None] * len(risks_json)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _create_one_semaphored(
        index: int, payload: dict[str, Any]
    ) -> tuple[int, Any, str | None]:
        async with semaphore:
            risk_data = await acreate_risk(**payload, **kwargs)
            risk_id: str | None = None
            if isinstance(risk_data, dict):
                risk_id = risk_data.get("risk_id") or risk_data.get("id")
            return index, risk_data, risk_id

    tasks = [
        asyncio.create_task(_create_one_semaphored(idx, payload))
        for idx, payload in enumerate(risks_json)
    ]

    if fail_fast:
        try:
            task_results = await asyncio.gather(*tasks)
            for result_idx, risk_data, risk_id in task_results:
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "risk_data": risk_data,
                    "risk_id": risk_id,
                    "error": None,
                }
        except Exception:
            for task in tasks:
                task.cancel()
            raise
    else:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)  # type: ignore[assignment]
        for idx, result in enumerate(task_results):
            if isinstance(result, Exception):
                results[idx] = {
                    "index": idx,
                    "success": False,
                    "risk_data": None,
                    "risk_id": None,
                    "error": str(result),
                }
            else:
                result_idx, risk_data, risk_id = result
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "risk_data": risk_data,
                    "risk_id": risk_id,
                    "error": None,
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(risks_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }
