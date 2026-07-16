"""BriteCore custom exceptions.

v2.0.0 Enhanced Error Model
=============================

All exceptions now include structured metadata for better error handling:

- **status_code**: HTTP status code (e.g., 400, 404, 500)
- **error_code**: BriteCore error code (e.g., "quote_not_found", "invalid_field")
- **request_id**: Request correlation ID for debugging (e.g., "abc123def456")
- **detail**: Human-readable error message
- **raw_payload**: Full server response dict for debugging

Example:

    try:
        retrieve_quote(quote_number="INVALID", client=client)
    except NotFoundError as e:
        print(f"Status: {e.status_code}")      # 404
        print(f"Code: {e.error_code}")         # "quote_not_found"
        print(f"Request ID: {e.request_id}")   # "abc123def456"
        print(f"Detail: {e.detail}")           # "Quote INVALID does not exist"
        print(f"Raw: {e.raw_payload}")         # {"success": false, ...}
"""

from typing import Any, Optional


class BritecoreError:
    """Namespace for custom exceptions related to BriteCore operations."""

    class Base(Exception):
        """Base class for all SDK-originated exceptions.

        v2.0.0 Enhanced with structured metadata:
        - status_code: HTTP status code
        - error_code: BriteCore error code
        - request_id: Request correlation ID
        - detail: Human-readable error message
        - raw_payload: Full server response
        """

        def __init__(
            self,
            message: str,
            *,
            status_code: int = 500,
            error_code: Optional[str] = None,
            request_id: Optional[str] = None,
            raw_payload: Optional[dict[str, Any]] = None,
        ) -> None:
            self.message = message
            self.detail = message  # Alias for clarity
            self.status_code = status_code
            self.error_code = error_code
            self.request_id = request_id
            self.raw_payload = raw_payload or {}
            super().__init__(self.message)

        def __str__(self) -> str:
            parts = [str(self.message)]
            if self.request_id:
                parts.append(f"[Request ID: {self.request_id}]")
            if self.error_code:
                parts.append(f"[Error Code: {self.error_code}]")
            return " ".join(parts)

    class NoDataReturned(Base):
        """Raised when BriteCore API returns no usable data."""

        def __init__(
            self,
            message: str,
            request: str | None = None,
            http_error: str | None = None,
            endpoint: str | None = None,
            http_status: int | None = None,
            *,
            status_code: int | None = None,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            self.request = request
            self.http_error = http_error
            self.endpoint = endpoint
            self.http_status = http_status
            # v2.0.0: Use status_code parameter, fall back to http_status
            resolved_status = status_code or http_status or 500
            super().__init__(
                message,
                status_code=resolved_status,
                error_code=error_code,
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            parts = [f"No data returned - {self.message}"]
            if self.endpoint:
                parts.append(f"Endpoint: {self.endpoint}")
            if self.http_status:
                parts.append(f"HTTP Status: {self.http_status}")
            if self.error_code:
                parts.append(f"Error Code: {self.error_code}")
            if self.request_id:
                parts.append(f"Request ID: {self.request_id}")
            if self.request:
                parts.append(f"Request: {self.request}")
            if self.http_error:
                parts.append(f"HTTP Error: {self.http_error}")
            return "\n".join(parts)

    class NoTokenReturned(Base):
        """Raised when OAuth token request fails."""

        def __init__(
            self,
            message: str,
            request: str | None = None,
            http_error: str | None = None,
            http_status: int | None = None,
            *,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            self.request = request
            self.http_error = http_error
            self.http_status = http_status
            resolved_status = http_status or 500
            super().__init__(
                message,
                status_code=resolved_status,
                error_code=error_code,
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            parts = [
                f"BriteCore was unable to return any authorization token - {self.message}"
            ]
            if self.http_status:
                parts.append(f"HTTP Status: {self.http_status}")
            if self.error_code:
                parts.append(f"Error Code: {self.error_code}")
            if self.request_id:
                parts.append(f"Request ID: {self.request_id}")
            if self.request:
                parts.append(f"Request: {self.request}")
            if self.http_error:
                parts.append(f"HTTP Error: {self.http_error}")
            return "\n".join(parts)

    class InvalidPhoneNumber(Base):
        """Raised when phone number validation fails."""

        def __str__(self) -> str:
            return f"Invalid Phone Number - {self.message}"

    class InvalidEmailAddress(Base):
        """Raised when email address validation fails."""

        def __str__(self) -> str:
            return f"Invalid E-Mail Address - {self.message}"

    class InvalidAddress(Base):
        """Raised when address validation fails."""

        def __str__(self) -> str:
            return f"Invalid Address - {self.message}"

    class BritecoreKeyError(Base):
        """Raised when a required key is missing."""

    class NoSiteError(Base):
        """Raised when no target site is assigned."""

    class MissingParameter(Base):
        """Raised when a required parameter is missing."""

    class ConflictingParameters(Base):
        """Raised when multiple conflicting parameters are specified."""

    class AuthenticationError(Base):
        """Raised when API authentication fails (invalid key, expired token, 401/403)."""

        def __init__(
            self,
            message: str,
            http_status: int | None = None,
            endpoint: str | None = None,
            *,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            self.http_status = http_status
            self.endpoint = endpoint
            resolved_status = http_status or 401
            super().__init__(
                message,
                status_code=resolved_status,
                error_code=error_code or "authentication_failed",
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            parts = ["BriteCore authentication failed"]
            if self.http_status:
                parts[0] += f" (HTTP {self.http_status})"
            parts[0] += f" - {self.message}"
            if self.error_code:
                parts.append(f"Error Code: {self.error_code}")
            if self.request_id:
                parts.append(f"Request ID: {self.request_id}")
            if self.endpoint:
                parts.append(f"Endpoint: {self.endpoint}")
            return "\n".join(parts)

    class RateLimitError(Base):
        """Raised when the API rate limit is exceeded (HTTP 429)."""

        def __init__(
            self,
            message: str,
            retry_after: int | None = None,
            *,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            self.retry_after = retry_after
            super().__init__(
                message,
                status_code=429,
                error_code=error_code or "rate_limit_exceeded",
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            retry_info = (
                f" Retry after {self.retry_after}s." if self.retry_after else ""
            )
            msg = f"BriteCore rate limit exceeded - {self.message}.{retry_info}"
            if self.request_id:
                msg += f" [Request ID: {self.request_id}]"
            return msg

    class ServerError(Base):
        """Raised when the API returns a 5xx server error."""

        def __init__(
            self,
            message: str,
            http_status: int | None = None,
            endpoint: str | None = None,
            *,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            self.http_status = http_status
            self.endpoint = endpoint
            resolved_status = http_status or 500
            super().__init__(
                message,
                status_code=resolved_status,
                error_code=error_code or "server_error",
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            parts = ["BriteCore server error"]
            if self.http_status:
                parts[0] += f" (HTTP {self.http_status})"
            parts[0] += f" - {self.message}"
            if self.error_code:
                parts.append(f"Error Code: {self.error_code}")
            if self.request_id:
                parts.append(f"Request ID: {self.request_id}")
            if self.endpoint:
                parts.append(f"Endpoint: {self.endpoint}")
            return "\n".join(parts)

    class ValidationError(NoDataReturned):
        """Raised when API validation fails (for example HTTP 400/422).

        v2.0.0 Enhancement: includes validation_errors dict with field-level details.
        """

        def __init__(
            self,
            message: str,
            request: str | None = None,
            http_error: str | None = None,
            endpoint: str | None = None,
            http_status: int | None = None,
            *,
            validation_errors: dict[str, Any] | None = None,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            self.validation_errors = validation_errors or {}
            resolved_status = http_status or 400
            super().__init__(
                message,
                request=request,
                http_error=http_error,
                endpoint=endpoint,
                http_status=resolved_status,
                status_code=resolved_status,
                error_code=error_code or "validation_error",
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            base = super().__str__()
            if self.validation_errors:
                base += "\nValidation Errors:"
                for field, errors in self.validation_errors.items():
                    if isinstance(errors, list):
                        for error in errors:
                            base += f"\n  {field}: {error}"
                    else:
                        base += f"\n  {field}: {errors}"
            return base

    class NotFoundError(NoDataReturned):
        """Raised when an API resource is not found (HTTP 404)."""

    class ConflictError(NoDataReturned):
        """Raised when API returns a conflict (HTTP 409)."""

    class ConfigurationError(Base):
        """Raised when the client is misconfigured (missing base_url, api_key, etc.)."""

        def __init__(
            self,
            message: str,
            *,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            super().__init__(
                message,
                status_code=400,
                error_code=error_code or "configuration_error",
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            return f"BriteCore configuration error - {self.message}"

    class RequestTimeoutError(Base):
        """Raised when an API request exceeds its configured timeout."""

        def __init__(
            self,
            message: str,
            timeout_seconds: int | float | None = None,
            endpoint: str | None = None,
            *,
            error_code: str | None = None,
            request_id: str | None = None,
            raw_payload: dict[str, Any] | None = None,
        ) -> None:
            self.timeout_seconds = timeout_seconds
            self.endpoint = endpoint
            super().__init__(
                message,
                status_code=408,
                error_code=error_code or "request_timeout",
                request_id=request_id,
                raw_payload=raw_payload,
            )

        def __str__(self) -> str:
            parts = ["Request timeout"]
            if self.timeout_seconds:
                parts[0] += f" ({self.timeout_seconds}s)"
            parts[0] += f" - {self.message}"
            if self.error_code:
                parts.append(f"Error Code: {self.error_code}")
            if self.request_id:
                parts.append(f"Request ID: {self.request_id}")
            if self.endpoint:
                parts.append(f"Endpoint: {self.endpoint}")
            return "\n".join(parts)


# ---------------------------------------------------------------------------
# Flat aliases — importable directly from britecore_sdk.exceptions
# so consumer code can write:
#   from britecore_sdk.exceptions import NotFoundError
# instead of:
#   except BritecoreError.NotFoundError
# ---------------------------------------------------------------------------
BritecoreBaseError = BritecoreError.Base
NoDataReturned = BritecoreError.NoDataReturned
NoTokenReturned = BritecoreError.NoTokenReturned
AuthenticationError = BritecoreError.AuthenticationError
RateLimitError = BritecoreError.RateLimitError
ServerError = BritecoreError.ServerError
ValidationError = BritecoreError.ValidationError
NotFoundError = BritecoreError.NotFoundError
ConflictError = BritecoreError.ConflictError
ConfigurationError = BritecoreError.ConfigurationError
RequestTimeoutError = BritecoreError.RequestTimeoutError
BritecoreKeyError = BritecoreError.BritecoreKeyError
NoSiteError = BritecoreError.NoSiteError
MissingParameter = BritecoreError.MissingParameter
ConflictingParameters = BritecoreError.ConflictingParameters
InvalidPhoneNumber = BritecoreError.InvalidPhoneNumber
InvalidEmailAddress = BritecoreError.InvalidEmailAddress
InvalidAddress = BritecoreError.InvalidAddress

__all__ = [
    "BritecoreError",
    # Flat aliases
    "BritecoreBaseError",
    "NoDataReturned",
    "NoTokenReturned",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "ConfigurationError",
    "RequestTimeoutError",
    "BritecoreKeyError",
    "NoSiteError",
    "MissingParameter",
    "ConflictingParameters",
    "InvalidPhoneNumber",
    "InvalidEmailAddress",
    "InvalidAddress",
]
