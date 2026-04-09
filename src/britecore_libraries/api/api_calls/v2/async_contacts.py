"""BriteCore v2 Async Contacts API endpoint wrappers.

Asynchronous (cached) counterparts to the synchronous wrappers in contacts.py.
Uses AsyncBritecoreAPIClient for non-blocking, TTL-cached HTTP requests.

Provides:
    anew_contact            -- Async create a new contact.
    aadd_contact_to_role    -- Async assign a contact to a named role.
    aupdate_contact         -- Async update contact fields.
    aget_contact            -- Async retrieve a contact by ID (cached by default).
    afind_contact_by_params -- Async search for contacts.
"""

from logging import Logger
from typing import Any, Literal, Unpack

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    AsyncBritecoreAPIClient,
    RequestParameters,
    async_api_client,
)
from britecore_libraries.models.contact import ROLETYPES

LOGGER: Logger = logger

API_CLIENT: AsyncBritecoreAPIClient = async_api_client
CONTACT_CACHE_NAMESPACE = "contacts"
DEFAULT_CACHE_TTL_SECONDS = 60


def _apply_contact_read_cache(
    kwargs: dict[str, Any], *, cache_key_parts: list[str] | None = None
) -> dict[str, Any]:
    """Apply default caching for contact read requests while allowing overrides."""
    kwargs.setdefault("cache_enabled", True)
    kwargs.setdefault("cache_namespace", CONTACT_CACHE_NAMESPACE)
    kwargs.setdefault("cache_ttl_seconds", DEFAULT_CACHE_TTL_SECONDS)
    if cache_key_parts:
        kwargs.setdefault("cache_key_parts", cache_key_parts)
    return kwargs


def _apply_contact_mutation_cache(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Invalidate cached contact reads after a successful mutation."""
    kwargs.setdefault("cache_invalidate_on_success", [CONTACT_CACHE_NAMESPACE])
    return kwargs


async def anew_contact(
    name: str,
    address: list[dict[str, str]],
    phone: list[dict[str, str] | None] | None = None,
    email: list[dict[str, str] | None] | None = None,
    contact_type: Literal["individual", "organization"] | None = "individual",
    **kwargs: Unpack[RequestParameters],
) -> tuple[str | None, str | None]:
    """Create a new contact record asynchronously.

    The request uses the provided name, addresses, optional phones and emails,
    and ``contact_type`` to create the contact documented by
    ``/api/v2/contacts/new_contact``. Returns the async ``aprocess_result(...)``
    payload together with the extracted contact ID, and invalidates cached contact
    reads on success; ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Creating contact '%s'", name)
    if not phone:
        phone = [{}]
    if not email:
        email = [{}]

    contact_request_json: dict[str, Any] = {
        "name": name,
        "addresses": address,
        "type": contact_type,
    }
    if email[0] != {}:
        contact_request_json.update({"emails": email})
    if phone[0] != {}:
        contact_request_json.update({"phones": phone})

    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/contacts/new_contact",
        json=contact_request_json,
        **_apply_contact_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for anew_contact")
    contact_json: Any = await API_CLIENT.aprocess_result(request_result)

    try:
        new_id: str = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id = "Fail"

    if new_id == "Fail":
        LOGGER.error("Failed to add contact - '%s'", name)
        return None, None

    LOGGER.debug("Added '%s'", name)
    return contact_json, new_id


async def aadd_contact_to_role(
    contact_id: str,
    role: ROLETYPES | None = "Named Insured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a contact to a named role asynchronously.

    Use ``contact_id`` and ``role`` to assign the contact to the requested role
    through ``/api/v2/contacts/add_contact_to_role``. Returns the async
    ``aprocess_result(...)`` payload, invalidates cached contact reads on success,
    and accepts ``RequestParameters`` overrides via ``**kwargs``.
    """
    LOGGER.debug("Adding role '%s' to '%s'", role, contact_id)
    role_request_json: dict[str, str | ROLETYPES | None] = {
        "contact_id": contact_id,
        "role_name": role,
    }
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **_apply_contact_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for aadd_contact_to_role")
    return await API_CLIENT.aprocess_result(request_result)


async def aupdate_contact(
    contact: dict[str, str | list[dict[str, str]]], **kwargs: Unpack[RequestParameters]
) -> Any:
    """Update an existing contact asynchronously.

    Pass the serialized ``contact`` payload to update stored contact fields via
    ``/api/v2/contacts/update_contact``. Returns the async
    ``aprocess_result(...)`` payload, invalidates cached contact reads on success,
    and accepts ``RequestParameters`` overrides via ``**kwargs``.
    """
    LOGGER.debug("Updating contact information\n%s", contact)
    update_request_json: dict[str, Any] = {"contact": contact}
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **_apply_contact_mutation_cache(dict(kwargs)),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for aupdate_contact")
    return await API_CLIENT.aprocess_result(request_result)


async def aget_contact(contact_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a contact by identifier with short-lived async caching.

    The request uses ``contact_id`` for ``/api/v2/contacts/get_contact`` and
    enables the default contact read cache unless the caller overrides it.
    Returns the async ``aprocess_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` plus cache override settings.
    """
    LOGGER.debug("Retrieving contact id '%s'", contact_id)
    contact_retrieve_json: dict[str, str] = {"contact_id": contact_id}
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **_apply_contact_read_cache(
            dict(kwargs), cache_key_parts=[f"contact:{contact_id}"]
        ),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for aget_contact")
    return await API_CLIENT.aprocess_result(request_result)


async def afind_contact_by_params(
    name: str,
    role_name: ROLETYPES | None = None,
    dob: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Find contacts by the supported search parameters with async caching.

    Use ``name`` together with optional ``role_name`` and ``dob`` to call
    ``/api/v2/contacts/find_contact_by_params``. Returns the async
    ``aprocess_result(...)`` payload, enables cacheable read lookups by default,
    and accepts ``RequestParameters`` plus cache override settings via ``**kwargs``.
    """
    LOGGER.debug("Finding contact '%s'", name)
    contact_retrieve_json: dict[str, str | ROLETYPES | None] = {
        "name": name,
        "role_name": role_name,
        "dob": dob,
    }
    cache_parts = [f"name:{name}"]
    if role_name:
        cache_parts.append(f"role:{role_name}")
    if dob:
        cache_parts.append(f"dob:{dob}")
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/contacts/find_contact_by_params",
        json=contact_retrieve_json,
        **_apply_contact_read_cache(dict(kwargs), cache_key_parts=cache_parts),
    )
    if request_result is None:
        raise RuntimeError("ado_request returned None for afind_contact_by_params")
    return await API_CLIENT.aprocess_result(request_result)


__all__ = [
    "aadd_contact_to_role",
    "afind_contact_by_params",
    "aget_contact",
    "anew_contact",
    "aupdate_contact",
]
