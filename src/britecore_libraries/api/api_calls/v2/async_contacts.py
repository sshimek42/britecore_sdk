from logging import Logger
from typing import Any, Literal, Optional, Unpack

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
    phone: Optional[list[Optional[dict[str, str]]]] = None,
    email: Optional[list[Optional[dict[str, str]]]] = None,
    contact_type: Optional[Literal["individual", "organization"]] = "individual",
    **kwargs: Unpack[RequestParameters],
) -> tuple[str | None, str | None]:
    """Create a new contact and invalidate cached contact reads on success."""
    LOGGER.debug(f"Creating contact %f.yellow%{name}%f%")
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

    request_result = await API_CLIENT.ado_request(
        path="/api/v2/contacts/new_contact",
        json=contact_request_json,
        **_apply_contact_mutation_cache(dict(kwargs)),
    )
    contact_json: Any = await API_CLIENT.aprocess_result(request_result)

    try:
        new_id: str = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id = "Fail"

    if new_id == "Fail":
        LOGGER.error(f"Failed to add contact - %f.yellow%{name}%f%")
        return None, None

    LOGGER.debug(f"Added %f.yellow%{name}%f%")
    return contact_json, new_id


async def aadd_contact_to_role(
    contact_id: str,
    role: Optional[ROLETYPES] = "Named Insured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a contact to a role and invalidate cached contact reads on success."""
    LOGGER.debug(f"Adding role %f.yellow%{role}%f% to %f.yellow%{contact_id}%f%")
    role_request_json: dict[
        Literal["contact_id", "role_name"], Optional[str | ROLETYPES]
    ] = {"contact_id": contact_id, "role_name": role}
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **_apply_contact_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aupdate_contact(
    contact: dict[str, str | list[dict[str, str]]], **kwargs: Unpack[RequestParameters]
) -> Any:
    """Update contact information and invalidate cached contact reads on success."""
    LOGGER.debug(f"Updating contact information\n%f.yellow%{contact}%f%")
    update_request_json: dict[str, dict[str, str | list[dict[str, str]]]] = {
        "contact": contact
    }
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **_apply_contact_mutation_cache(dict(kwargs)),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def aget_contact(contact_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve contact information by contact ID with short-lived caching."""
    LOGGER.debug(f"Retrieving contact id %f.yellow%{contact_id}%f%")
    contact_retrieve_json: dict[str, str] = {"contact_id": contact_id}
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **_apply_contact_read_cache(
            dict(kwargs), cache_key_parts=[f"contact:{contact_id}"]
        ),
    )
    return await API_CLIENT.aprocess_result(request_result)


async def afind_contact_by_params(
    name: str,
    role_name: Optional[ROLETYPES] = None,
    dob: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Search for contacts using cacheable parameterized lookups."""
    LOGGER.debug(f"Finding contact %f.yellow%{name}%f%")
    contact_retrieve_json: dict[str, str | None] = {
        "name": name,
        "role_name": role_name,
        "dob": dob,
    }
    cache_parts = [f"name:{name}"]
    if role_name:
        cache_parts.append(f"role:{role_name}")
    if dob:
        cache_parts.append(f"dob:{dob}")
    request_result = await API_CLIENT.ado_request(
        path="/api/v2/contacts/find_contact_by_params",
        json=contact_retrieve_json,
        **_apply_contact_read_cache(dict(kwargs), cache_key_parts=cache_parts),
    )
    return await API_CLIENT.aprocess_result(request_result)


__all__ = [
    "aadd_contact_to_role",
    "afind_contact_by_params",
    "aget_contact",
    "anew_contact",
    "aupdate_contact",
]
