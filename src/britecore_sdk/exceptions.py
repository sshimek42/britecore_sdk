"""BriteCore custom exceptions."""


class BritecoreError:
    """Namespace for custom exceptions related to BriteCore operations."""

    class Base(Exception):
        """Base class for all SDK-originated exceptions."""

        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return str(self.message)

    class NoDataReturned(Base):
        """Raised when BriteCore API returns no usable data."""

        def __init__(
            self,
            message: str,
            request: str | None = None,
            http_error: str | None = None,
            endpoint: str | None = None,
            http_status: int | None = None,
        ) -> None:
            self.request = request
            self.http_error = http_error
            self.endpoint = endpoint
            self.http_status = http_status
            super().__init__(message)

        def __str__(self) -> str:
            parts = [f"No data returned - {self.message}"]
            if self.endpoint:
                parts.append(f"Endpoint: {self.endpoint}")
            if self.http_status:
                parts.append(f"HTTP Status: {self.http_status}")
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
        ) -> None:
            self.request = request
            self.http_error = http_error
            self.http_status = http_status
            super().__init__(message)

        def __str__(self) -> str:
            parts = [
                f"BriteCore was unable to return any authorization token - {self.message}"
            ]
            if self.http_status:
                parts.append(f"HTTP Status: {self.http_status}")
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
        ) -> None:
            self.http_status = http_status
            self.endpoint = endpoint
            super().__init__(message)

        def __str__(self) -> str:
            parts = ["BriteCore authentication failed"]
            if self.http_status:
                parts[0] += f" (HTTP {self.http_status})"
            parts[0] += f" - {self.message}"
            if self.endpoint:
                parts.append(f"Endpoint: {self.endpoint}")
            return "\n".join(parts)

    class RateLimitError(Base):
        """Raised when the API rate limit is exceeded (HTTP 429)."""

        def __init__(
            self,
            message: str,
            retry_after: int | None = None,
        ) -> None:
            self.retry_after = retry_after
            super().__init__(message)

        def __str__(self) -> str:
            retry_info = (
                f" Retry after {self.retry_after}s." if self.retry_after else ""
            )
            return f"BriteCore rate limit exceeded - {self.message}.{retry_info}"

    class ServerError(Base):
        """Raised when the API returns a 5xx server error."""

        def __init__(
            self,
            message: str,
            http_status: int | None = None,
            endpoint: str | None = None,
        ) -> None:
            self.http_status = http_status
            self.endpoint = endpoint
            super().__init__(message)

        def __str__(self) -> str:
            parts = ["BriteCore server error"]
            if self.http_status:
                parts[0] += f" (HTTP {self.http_status})"
            parts[0] += f" - {self.message}"
            if self.endpoint:
                parts.append(f"Endpoint: {self.endpoint}")
            return "\n".join(parts)

    class ValidationError(NoDataReturned):
        """Raised when API validation fails (for example HTTP 400/422)."""

    class NotFoundError(NoDataReturned):
        """Raised when an API resource is not found (HTTP 404)."""

    class ConflictError(NoDataReturned):
        """Raised when API returns a conflict (HTTP 409)."""

    class ConfigurationError(Base):
        """Raised when the client is misconfigured (missing base_url, api_key, etc.)."""

        def __str__(self) -> str:
            return f"BriteCore configuration error - {self.message}"

    class RequestTimeoutError(Base):
        """Raised when an API request exceeds its configured timeout."""

        def __init__(
            self,
            message: str,
            timeout_seconds: int | float | None = None,
            endpoint: str | None = None,
        ) -> None:
            self.timeout_seconds = timeout_seconds
            self.endpoint = endpoint
            super().__init__(message)

        def __str__(self) -> str:
            parts = ["Request timeout"]
            if self.timeout_seconds:
                parts[0] += f" ({self.timeout_seconds}s)"
            parts[0] += f" - {self.message}"
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
