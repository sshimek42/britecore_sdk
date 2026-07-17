"""BriteCore v2 Quotes API endpoint wrappers.

These wrappers cover quote creation and retrieval workflows exposed by the SDK's
current v2 quote surface. The quote paths remain known spec-gap wrappers, so the
docstrings describe the intended API contract first and call out SDK-specific
response normalization where needed.
"""

from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse, Timeout

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
    web_timeout_long,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def create_full_quote(
    quote_json: dict[str, Any],
    *,
    client: BritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> tuple[dict[str, Any] | None, str | None]:
    """Create a quote from the supplied quote payload.

    This wrapper submits ``quote_json`` to ``/api/v2/quotes/create_full_quote``
    and normalizes the response through ``process_result(...)``. As an SDK-
    specific convenience, it returns a tuple of ``(quote_data, quote_id)``,
    where ``quote_id`` is extracted from the normalized payload when present.
    ``**kwargs`` accepts ``RequestParameters`` overrides such as timeout,
    headers, or retry settings.

    **v2.0.0 Explicit Client Pattern:**

    In v2.0.0, the explicit ``client`` parameter is now the recommended approach:

    .. code-block:: python

        from britecore_sdk import BritecoreAPIClient
        from britecore_sdk.api.api_calls.v2 import quotes

        client = BritecoreAPIClient("site").init_client()
        quote_data, quote_id = quotes.create_full_quote(
            quote_json={"...": "..."},
            client=client,
        )

    **v1.x Implicit Client Pattern (still supported but deprecated):**

    .. code-block:: python

        from britecore_sdk.api.api_calls import init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        init_api_client(target_site="site")
        quote_data, quote_id = quotes.create_full_quote(quote_json={"...": "..."})

    Args:
        quote_json: The quote payload to create.
        client: Optional explicit client instance. If omitted, uses the module-level client.
        **kwargs: RequestParameters overrides (timeout, headers, retry, etc.)

    Returns:
        tuple: ``(quote_data, quote_id)`` where quote_id is extracted from the payload,
            or ``(None, None)`` if the response could not be processed.

    Raises:
        BritecoreError.MissingParameter: If quote_json is missing or empty.
        BritecoreError.ConfigurationError: If no explicit client is provided and the
            module-level client has not been initialized.
    """
    # Validate required parameters
    if not quote_json or not isinstance(quote_json, dict):
        raise BritecoreError.MissingParameter(
            "quote_json is required and must be a dict"
        )

    # Preserve module-level API_CLIENT behavior while allowing explicit override.
    effective_client: BritecoreAPIClient = client or API_CLIENT

    # Quote creation is a long-running write; apply the long timeout unless the
    # caller has already provided an explicit request_timeout override.
    provided_timeout: Timeout | None = kwargs.get("request_timeout")
    if not provided_timeout:
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    request_result: BaseHTTPResponse | HTTPResponse | None = (
        effective_client.do_request(
            path="/api/v2/quotes/create_full_quote", json=quote_json, **kwargs
        )
    )

    json_info: Any = effective_client.process_result(
        request_result, endpoint="/api/v2/quotes/create_full_quote"
    )

    if not json_info:
        return None, None

    return json_info, json_info["id"]


def get_quote(
    quote_id: str,
    *,
    client: BritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a quote by quote identifier.

    This wrapper sends ``quote_id`` to ``/api/v2/quotes/get_quote`` and returns the
    normalized ``process_result(...)`` payload for the requested quote.
    ``**kwargs`` accepts ``RequestParameters`` overrides such as timeout,
    headers, or retry settings.

    **v2.0.0 Explicit Client Pattern:**

    .. code-block:: python

        from britecore_sdk import BritecoreAPIClient
        from britecore_sdk.api.api_calls.v2 import quotes

        client = BritecoreAPIClient("site").init_client()
        quote = quotes.get_quote(quote_id="Q123", client=client)

    **v1.x Implicit Client Pattern (still supported but deprecated):**

    .. code-block:: python

        from britecore_sdk.api.api_calls import init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        init_api_client(target_site="site")
        quote = quotes.get_quote(quote_id="Q123")

    Args:
        quote_id: The quote ID to retrieve.
        client: Optional explicit client instance. If omitted, uses the module-level client.
        **kwargs: RequestParameters overrides (timeout, headers, retry, etc.)

    Returns:
        dict: The normalized quote response.

    Raises:
        BritecoreError.MissingParameter: If quote_id is missing.
        BritecoreError.ConfigurationError: If no explicit client is provided and the
            module-level client has not been initialized.
    """
    # Validate required parameters
    if not quote_id or not quote_id.strip():
        raise BritecoreError.MissingParameter("quote id is required")
    quote_json: dict[str, str] = {"id": quote_id}

    # Preserve module-level API_CLIENT behavior while allowing explicit override.
    effective_client: BritecoreAPIClient = client or API_CLIENT

    LOGGER.debug("Getting quote")

    request_result: BaseHTTPResponse | HTTPResponse | None = (
        effective_client.do_request(
            path="/api/v2/quotes/get_quote", json=quote_json, **kwargs
        )
    )

    return effective_client.process_result(
        request_result, endpoint="/api/v2/quotes/get_quote"
    )


__all__ = ["create_full_quote", "get_quote"]

# --- Autogenerated spec wrappers ---


def associate_agentcy_to_quote(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/associate_agentcy_to_quote``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/associate_agentcy_to_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/associate_agentcy_to_quote"
    )


def bind_full_quote(
    external_system_reference: str | None = None,
    id: str | None = None,
    submit_bound: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/bind_full_quote``."""
    request_json: dict[str, Any] = {
        "external_system_reference": external_system_reference,
        "id": id,
        "submit_bound": submit_bound,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/bind_full_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/bind_full_quote"
    )


def copy_quote(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/copy_quote``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/copy_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/copy_quote"
    )


def create_and_rate_full_quote(
    quote: dict[str, Any] | None = None,
    stateless: bool | None = None,
    rate_quote: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/create_and_rate_full_quote``."""
    request_json: dict[str, Any] = {
        "quote": quote,
        "stateless": stateless,
        "rate_quote": rate_quote,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/create_and_rate_full_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/create_and_rate_full_quote"
    )


def create_endorsement_quote(
    quote_external_system_reference: str | None = None,
    quote_id: str | None = None,
    endorsement_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/create_endorsement_quote``."""
    request_json: dict[str, Any] = {
        "quote_external_system_reference": quote_external_system_reference,
        "quote_id": quote_id,
        "endorsement_date": endorsement_date,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/create_endorsement_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/create_endorsement_quote"
    )


def create_renewal_quote(
    external_system_reference: str | None = None,
    quote_id: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/create_renewal_quote``."""
    request_json: dict[str, Any] = {
        "external_system_reference": external_system_reference,
        "quote_id": quote_id,
        "policy_number": policy_number,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/create_renewal_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/create_renewal_quote"
    )


def delete_full_quote(
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/delete_full_quote``."""
    request_json: dict[str, Any] = {
        "external_system_reference": external_system_reference,
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/delete_full_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/delete_full_quote"
    )


def delete_quote(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/delete_quote``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/delete_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/delete_quote"
    )


def get_estimated_quote(
    rate_quote: bool | None = None,
    quote_id: str | None = None,
    stateless: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/get_estimated_quote``."""
    request_json: dict[str, Any] = {
        "rate_quote": rate_quote,
        "quote_id": quote_id,
        "stateless": stateless,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/get_estimated_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/get_estimated_quote"
    )


def get_quote_properties_summary(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/get_quote_properties_summary``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/get_quote_properties_summary",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/get_quote_properties_summary"
    )


def get_quote_wizard_plugin(
    integration_point_code: str | None = None,
    revision_id: str | None = None,
    integration_instance_id: str | None = None,
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/get_quote_wizard_plugin``."""
    request_json: dict[str, Any] = {
        "integration_point_code": integration_point_code,
        "revision_id": revision_id,
        "integration_instance_id": integration_instance_id,
        "property_id": property_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/get_quote_wizard_plugin",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/get_quote_wizard_plugin"
    )


def get_risks(
    quote_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/get_risks``."""
    request_json: dict[str, Any] = {
        "quote_id": quote_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/get_risks",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/get_risks"
    )


def issue_full_quote(
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/issue_full_quote``."""
    request_json: dict[str, Any] = {
        "external_system_reference": external_system_reference,
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/issue_full_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/issue_full_quote"
    )


def list_available_offers(
    contact_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/list_available_offers``."""
    request_json: dict[str, Any] = {"contact_id": contact_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/list_available_offers",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/list_available_offers"
    )


def modify_full_quote(
    messages: list[str] | None = None,
    data: Any | dict[str, Any] | None = None,
    success: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/modify_full_quote``."""
    request_json: dict[str, Any] = {
        "messages": messages,
        "data": data,
        "success": success,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/modify_full_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/modify_full_quote"
    )


def prefill_loss_history(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/prefill_loss_history``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/prefill_loss_history",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/prefill_loss_history"
    )


def prefill_quote(
    api_key: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/prefill_quote``."""
    request_json: dict[str, Any] = {
        "api_key": api_key,
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/prefill_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/prefill_quote"
    )


def prefill_violations(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/prefill_violations``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/prefill_violations",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/prefill_violations"
    )


def rate_full_quote(
    debug: bool | None = None,
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/rate_full_quote``."""
    request_json: dict[str, Any] = {
        "debug": debug,
        "external_system_reference": external_system_reference,
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/rate_full_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/rate_full_quote"
    )


def rate_quote(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/rate_quote``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/rate_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/rate_quote"
    )


def retrieve_full_quote(
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/retrieve_full_quote``."""
    request_json: dict[str, Any] = {
        "external_system_reference": external_system_reference,
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/retrieve_full_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/retrieve_full_quote"
    )


def submit_application(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/submit_application``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/submit_application",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/submit_application"
    )


def submit_change(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/submit_change``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/submit_change",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/submit_change"
    )


def summary(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/summary``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/summary",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(request_result, endpoint="/api/v2/quotes/summary")


def turn_quote_into_application(
    quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/turn_quote_into_application``."""
    request_json: dict[str, Any] = {"quote_id": quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/turn_quote_into_application",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/turn_quote_into_application"
    )


def update_e_delivery_enabled(
    revision_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/quotes/update_e_delivery_enabled``."""
    request_json: dict[str, Any] = {"revision_id": revision_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/update_e_delivery_enabled",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/update_e_delivery_enabled"
    )


__all__.extend(
    [
        "associate_agentcy_to_quote",
        "bind_full_quote",
        "copy_quote",
        "create_and_rate_full_quote",
        "create_endorsement_quote",
        "create_renewal_quote",
        "delete_full_quote",
        "delete_quote",
        "get_estimated_quote",
        "get_quote_properties_summary",
        "get_quote_wizard_plugin",
        "get_risks",
        "issue_full_quote",
        "list_available_offers",
        "modify_full_quote",
        "prefill_loss_history",
        "prefill_quote",
        "prefill_violations",
        "rate_full_quote",
        "rate_quote",
        "retrieve_full_quote",
        "submit_application",
        "submit_change",
        "summary",
        "turn_quote_into_application",
        "update_e_delivery_enabled",
    ]
)
