"""Version 2 API wrappers, including async cache-aware variants.

Sync domain modules
-------------------
Import a domain module to access its endpoint wrappers::

    from britecore_libraries.api.api_calls.v2 import policies
    result = policies.retrieve_policy(policy_number="POL-001")

All sync domain modules are listed in ``__all__`` and are importable
directly from this package.

Async helpers
-------------
Individual async cache-aware wrapper functions are also re-exported
directly from this package for backwards compatibility.
"""

# ------------------------------------------------------------------
# Sync domain modules
# ------------------------------------------------------------------
from britecore_libraries.api.api_calls.v2 import (
    accounting,
    attachments,
    billing,
    claims,
    commissions,
    contacts,
    custom_ui,
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
    printing,
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
# Async cache-aware wrappers (individual function re-exports)
# ------------------------------------------------------------------
from britecore_libraries.api.api_calls.v2.async_contacts import (
	aadd_contact_to_role,
	afind_contact_by_params,
	aget_contact,
	anew_contact,
	aupdate_contact,
)
from britecore_libraries.api.api_calls.v2.async_policies import (
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
from britecore_libraries.api.api_calls.v2.async_quotes import (
	acreate_full_quote,
	aget_quote,
)

__all__ = [
    # Sync domain modules
    "accounting",
    "attachments",
    "billing",
    "claims",
    "commissions",
    "contacts",
    "custom_ui",
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
    "printing",
    "quotes",
    "reports",
    "return_premium",
    "search",
    "settings",
    "signatures",
    "uploads",
    "utils",
    "vendors",
    # Async function re-exports
    "aadd_contact_to_role",
    "aadd_line_item",
    "acreate_full_quote",
    "acreate_policy",
    "acreate_risk",
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

