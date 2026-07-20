"""Helper functions for generating contextual error hints.

This module provides utilities to generate helpful troubleshooting suggestions
for common BriteCore SDK errors, improving developer experience when debugging issues.

Example:
    >>> from britecore_sdk.utils.error_hints import get_hint_for_error
    >>> hint = get_hint_for_error("configuration", "base_url")
    >>> print(hint)
    Set base_url via: ~/.britecore/.secrets.toml[site_name] or $env:BRITECORE_SDK_BASE_URL
"""

from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors for hint generation."""

    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    NOT_FOUND = "not_found"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    SERVER = "server"
    CONNECTION = "connection"


def get_hint_for_error(
    category: str | ErrorCategory, error_type: str | None = None
) -> str | None:
    """Get a helpful hint for a specific error category and type.

    Args:
        category: Error category (e.g., "configuration", "authentication")
        error_type: Specific error type (e.g., "missing_base_url", "invalid_key")

    Returns:
        A helpful hint string, or None if no hint is available.

    Example:
        >>> hint = get_hint_for_error("configuration", "missing_base_url")
        >>> print(hint)
        Set base_url via: ~/.britecore/.secrets.toml[site_name]...
    """
    if isinstance(category, ErrorCategory):
        category = category.value

    hints_map = {
        "configuration": _configuration_hints,
        "authentication": _authentication_hints,
        "rate_limit": _rate_limit_hints,
        "not_found": _not_found_hints,
        "validation": _validation_hints,
        "timeout": _timeout_hints,
        "server": _server_hints,
        "connection": _connection_hints,
    }

    hint_provider = hints_map.get(category.lower())
    if hint_provider:
        return hint_provider(error_type)

    return None


# Configuration hints
def _configuration_hints(error_type: str | None = None) -> str | None:
    """Generate hints for configuration errors."""
    hints = {
        "missing_base_url": (
            "Set base_url via: ~/.britecore/.secrets.toml[site_name] or "
            "$env:BRITECORE_SDK_BASE_URL (Windows) / $BRITECORE_SDK_BASE_URL (Linux)"
        ),
        "missing_api_key": (
            "Set api_key via: ~/.britecore/.secrets.toml[site_name] or "
            "$env:BRITECORE_SDK_API_KEY (Windows) / $BRITECORE_SDK_API_KEY (Linux)"
        ),
        "missing_oauth": (
            "For OAuth, set client_id and client_secret via: "
            "~/.britecore/.secrets.toml[site_name] or env vars "
            "BRITECORE_SDK_CLIENT_ID / BRITECORE_SDK_CLIENT_SECRET"
        ),
        "missing_target_site": (
            "Set target_site via: ~/.britecore/settings.toml [default] section or "
            "$env:target_site (Windows) / $target_site (Linux). "
            "Run: britecore-check-config to see available sites."
        ),
        "missing_credentials": (
            "Provide either: (1) api_key OR (2) client_id + client_secret. "
            "See ~/.britecore/.secrets.toml template."
        ),
        "invalid_config_file": (
            "Configuration file has invalid TOML syntax. "
            "Verify format with: britecore-check-config"
        ),
        "config_not_found": (
            "No configuration found. Create ~/.britecore/settings.toml and "
            "~/.britecore/.secrets.toml or use BRITECORE_SDK_* env vars."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


# Authentication hints
def _authentication_hints(error_type: str | None = None) -> str | None:
    """Generate hints for authentication errors."""
    hints = {
        "invalid_credentials": (
            "API key is invalid or expired. Verify in BriteCore admin panel "
            "and update in ~/.britecore/.secrets.toml"
        ),
        "expired_token": (
            "OAuth token has expired. Tokens are automatically refreshed, "
            "but verify client_id and client_secret are correct."
        ),
        "insufficient_permissions": (
            "Your credentials are valid but lack permission for this operation. "
            "Check your user role in BriteCore admin."
        ),
        "token_refresh_failed": (
            "OAuth token refresh failed. Verify: (1) client_id and client_secret "
            "are correct, (2) OAuth token endpoint is accessible."
        ),
        "401_unauthorized": (
            "Authentication failed (HTTP 401). Credentials may be invalid or expired. "
            "Run: britecore-check-config"
        ),
        "403_forbidden": (
            "Access forbidden (HTTP 403). You may lack permission for this resource. "
            "Check your user role in BriteCore."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


# Rate limit hints
def _rate_limit_hints(error_type: str | None = None) -> str | None:
    """Generate hints for rate limit errors."""
    hints = {
        "rate_limit_exceeded": (
            "API rate limit exceeded (HTTP 429). The SDK automatically retries, "
            "but heavy load detected. Consider: (1) Batch operations, "
            "(2) Stagger requests over time, (3) Reduce polling frequency."
        ),
        "retry_after": (
            "Rate limited. The server requests we wait {retry_after}s before retrying. "
            "This is handled automatically by the SDK."
        ),
        "burst_limit": (
            "You're sending requests too quickly. Consider adding delays between "
            "requests or using batch endpoints where available."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


# Not found hints
def _not_found_hints(error_type: str | None = None) -> str | None:
    """Generate hints for not found errors."""
    hints = {
        "resource_not_found": (
            "The requested resource doesn't exist. Verify the ID/number is correct "
            "and that the resource hasn't been deleted."
        ),
        "policy_not_found": (
            "Policy not found. Double-check the policy number and verify you have "
            "permission to access policies from that customer."
        ),
        "quote_not_found": (
            "Quote not found. Verify the quote number is correct and hasn't expired."
        ),
        "endpoint_not_implemented": (
            "This endpoint is not yet available in the SDK. "
            "Check API.md for supported endpoints."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


# Validation hints
def _validation_hints(error_type: str | None = None) -> str | None:
    """Generate hints for validation errors."""
    hints = {
        "missing_required_field": (
            "A required field is missing. Check the error details for which field(s) "
            "are needed and ensure they're populated."
        ),
        "invalid_format": (
            "A field has an invalid format. Common issues: "
            "(1) Email not valid, (2) Phone number wrong format, (3) Date format incorrect."
        ),
        "invalid_enum_value": (
            "An enum field has an invalid value. Check API.md for allowed values "
            "for this field."
        ),
        "constraint_violation": (
            "Data violates a business constraint. Review error message for details "
            "and check BriteCore business rules."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


# Timeout hints
def _timeout_hints(error_type: str | None = None) -> str | None:
    """Generate hints for timeout errors."""
    hints = {
        "request_timeout": (
            "Request timed out. The API took longer than expected. "
            "Try: (1) Increase timeout via timeout parameter, (2) Check network, "
            "(3) Retry operation."
        ),
        "connect_timeout": (
            "Connection timeout. Cannot reach the API server. "
            "Verify: (1) base_url is correct, (2) Network connectivity, "
            "(3) Firewall allows HTTPS outbound."
        ),
        "read_timeout": (
            "Read timeout waiting for response. API is taking too long. "
            "Try: (1) Increase timeout, (2) Simplify query, (3) Contact support if persistent."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


# Server error hints
def _server_hints(error_type: str | None = None) -> str | None:
    """Generate hints for server errors."""
    hints = {
        "500_internal_error": (
            "BriteCore server error (HTTP 500). This is temporary. "
            "The SDK will retry automatically. If persistent, contact BriteCore support "
            "with request ID: {request_id}"
        ),
        "503_service_unavailable": (
            "BriteCore service temporarily unavailable (HTTP 503). "
            "Likely maintenance or high load. Retry in a few moments. "
            "Check status page for updates."
        ),
        "502_bad_gateway": (
            "Bad gateway error (HTTP 502). The API is likely restarting. "
            "Retry after a short delay."
        ),
        "server_maintenance": (
            "BriteCore appears to be under maintenance. Check the status page "
            "at https://status.britecore.com for updates."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


# Connection hints
def _connection_hints(error_type: str | None = None) -> str | None:
    """Generate hints for connection errors."""
    hints = {
        "connection_refused": (
            "Connection refused. The API server is not accepting connections. "
            "Verify: (1) base_url is correct, (2) API is online, (3) No firewall blocks."
        ),
        "dns_resolution_failed": (
            "Cannot resolve the API hostname. Check: (1) base_url domain is correct, "
            "(2) DNS is working, (3) Network has internet access."
        ),
        "certificate_error": (
            "SSL/TLS certificate verification failed. Likely causes: "
            "(1) Outdated CA certificates, (2) Corporate proxy intercepting SSL, "
            "(3) Update certifi: pip install --upgrade certifi"
        ),
        "network_unreachable": (
            "Network is unreachable. Check your internet connection and "
            "verify the API server is accessible from your network."
        ),
    }
    return hints.get(error_type.lower()) if error_type else None


__all__ = [
    "ErrorCategory",
    "get_hint_for_error",
]

