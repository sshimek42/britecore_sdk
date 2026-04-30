"""Version 2 API wrappers, including async variants and batch aliases.

Sync domain modules
-------------------
Import a domain module to access its endpoint wrappers::

    from britecore_sdk.api.api_calls.v2 import policies
    result = policies.retrieve_policy(policy_number="POL-001")

All sync domain modules are listed in ``__all__`` and are importable
directly from this package.

Async helpers and batch aliases
-------------------------------
This package re-exports async v2 wrapper functions and exposes lazy,
backwards-compatible aliases for workflow batch helpers.
"""

from importlib import import_module
from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters

# ------------------------------------------------------------------
# Sync domain modules
# ------------------------------------------------------------------
from britecore_sdk.api.api_calls.v2 import (
    accounting,
    attachments,
    billing,
    claims,
    commissions,
    contacts,
    dashboards,
    data,
    deliverables,
    errors,
    inspections,
    insured,
    intacct,
    lines,
    nightly_jobs,
    notes,
    notifications,
    payments,
    policies,
    quotes,
    reports,
    return_premium,
    search,
    settings,
    signatures,
    uploads,
    utils,
    vendors,
)

# ------------------------------------------------------------------
# Async v2 wrapper function re-exports
# ------------------------------------------------------------------
from britecore_sdk.api.api_calls.v2.async_contacts import (
    aadd_contact_to_role,
    afind_contact_by_params,
    aget_contact,
    anew_contact,
    aupdate_contact,
)
from britecore_sdk.api.api_calls.v2.async_policies import (
    aadd_line_item,
    acreate_policy,
    acreate_risk,
    anew_mortgagee,
    anew_revision_contact,
    arate_revision,
    arate_risk,
    aretrieve_policy,
    aretrieve_policy_contact_info,
    aretrieve_policy_ids,
    aretrieve_policy_snapshot,
    aretrieve_policy_terms,
    aretrieve_revision_details,
    aretrieve_risk_details,
    aretrieve_risks,
    astore_mortgagee,
    aupdate_property_location,
    aupdate_rating_information,
)
from britecore_sdk.api.api_calls.v2.async_quotes import (
    acreate_full_quote,
    aget_quote,
)


def create_contacts_batch(
    contacts_json: list[dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `create_contacts_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.batch_contacts"
    ).create_contacts_batch
    return _impl(contacts_json, max_workers=max_workers, fail_fast=fail_fast, **kwargs)


def create_policies_batch(
    policies_json: list[dict[str, Any]],
    max_workers: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `create_policies_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.batch_policies"
    ).create_policies_batch
    return _impl(policies_json, max_workers=max_workers, fail_fast=fail_fast, **kwargs)


def create_risks_batch(
    risks_json: list[dict[str, Any]],
    max_workers: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `create_risks_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.batch_policies"
    ).create_risks_batch
    return _impl(risks_json, max_workers=max_workers, fail_fast=fail_fast, **kwargs)


def create_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `create_full_quotes_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.batch_quotes"
    ).create_full_quotes_batch
    return _impl(quotes_json, max_workers=max_workers, fail_fast=fail_fast, **kwargs)


async def acreate_contacts_batch(
    contacts_json: list[dict[str, Any]],
    max_concurrent: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `acreate_contacts_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.async_batch_contacts"
    ).acreate_contacts_batch
    return await _impl(
        contacts_json,
        max_concurrent=max_concurrent,
        fail_fast=fail_fast,
        **kwargs,
    )


async def acreate_policies_batch(
    policies_json: list[dict[str, Any]],
    max_concurrent: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `acreate_policies_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.async_batch_policies"
    ).acreate_policies_batch
    return await _impl(
        policies_json,
        max_concurrent=max_concurrent,
        fail_fast=fail_fast,
        **kwargs,
    )


async def acreate_risks_batch(
    risks_json: list[dict[str, Any]],
    max_concurrent: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `acreate_risks_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.async_batch_policies"
    ).acreate_risks_batch
    return await _impl(
        risks_json,
        max_concurrent=max_concurrent,
        fail_fast=fail_fast,
        **kwargs,
    )


async def acreate_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_concurrent: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Backward-compatible alias to workflows `acreate_full_quotes_batch(...)`."""
    _impl = import_module(
        "britecore_sdk.api.workflows.async_batch_quotes"
    ).acreate_full_quotes_batch
    return await _impl(
        quotes_json,
        max_concurrent=max_concurrent,
        fail_fast=fail_fast,
        **kwargs,
    )


__all__ = [
    # Sync domain modules
    "accounting",
    "attachments",
    "billing",
    "claims",
    "commissions",
    "contacts",
    "dashboards",
    "data",
    "deliverables",
    "errors",
    "inspections",
    "insured",
    "intacct",
    "lines",
    "nightly_jobs",
    "notes",
    "notifications",
    "payments",
    "policies",
    "quotes",
    "reports",
    "return_premium",
    "search",
    "settings",
    "signatures",
    "uploads",
    "utils",
    "vendors",
    # Sync batch helpers (from workflows)
    "create_contacts_batch",
    "create_full_quotes_batch",
    "create_policies_batch",
    "create_risks_batch",
    # Async function re-exports
    "aadd_contact_to_role",
    "aadd_line_item",
    "acreate_contacts_batch",
    "acreate_full_quote",
    "acreate_full_quotes_batch",
    "acreate_policies_batch",
    "acreate_policy",
    "acreate_risk",
    "acreate_risks_batch",
    "afind_contact_by_params",
    "aget_contact",
    "aget_quote",
    "anew_contact",
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
    "aupdate_contact",
    "aupdate_property_location",
    "aupdate_rating_information",
]
