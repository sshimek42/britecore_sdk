"""
BriteCore custom exceptions.

Defines specific error types for handling various situations such as
invalid data, missing tokens, or invalid input formats.
"""


class BritecoreError:
    """Collection of custom exceptions related to BriteCore operations."""

    class NoDataReturned(Exception):
        """Raised when BriteCore API returns no data."""

        def __init__(
            self,
            message: str,
            request: str | None = None,
            http_error: str | None = None,
        ):
            self.message = message
            self.request = request
            self.http_error = http_error
            super().__init__(self.message)

        def __str__(self) -> str:
            return (
                f"No data returned - {self.message}\n"
                f"Request: {self.request}\n"
                f"HTTP Error: {self.http_error}"
            )

    class NoTokenReturned(Exception):
        """Raised when OAuth token request fails."""

        def __init__(
            self,
            message: str,
            request: str | None = None,
            http_error: str | None = None,
        ) -> None:
            self.message = message
            self.request = request
            self.http_error = http_error
            super().__init__(self.message)

        def __str__(self) -> str:
            return (
                f"BriteCore was unable to return any authorization token - "
                f"{self.message}\n"
                f"Request: {self.request}\n"
                f"HTTP Error: {self.http_error}"
            )

    class InvalidPhoneNumber(Exception):
        """Raised when phone number validation fails."""

        def __init__(self, message: str):
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return f"Invalid Phone Number - {self.message}"

    class InvalidEmailAddress(Exception):
        """Raised when email address validation fails."""

        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return f"Invalid E-Mail Address - {self.message}"

    class InvalidAddress(Exception):
        """Raised when address validation fails."""

        def __init__(self, message: str):
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return f"Invalid Address - {self.message}"

    class BritecoreKeyError(Exception):
        """Raised when a required key is missing."""

        def __init__(self, message: str):
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return self.message

    class NoSiteError(Exception):
        """Raised when no target site is assigned."""

        def __init__(self, message: str):
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return self.message

    class MissingParameter(Exception):
        """Raised when a required parameter is missing."""

        def __init__(self, message: str):
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return self.message

    class ConflictingParameters(Exception):
        """Raised when multiple conflicting parameters are specified."""

        def __init__(self, message: str):
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return self.message

    class AuthenticationError(Exception):
        """Raised when API authentication fails (invalid key, expired token, 401/403)."""

        def __init__(
            self,
            message: str,
            http_status: int | None = None,
        ) -> None:
            self.message = message
            self.http_status = http_status
            super().__init__(self.message)

        def __str__(self) -> str:
            status_info = f" (HTTP {self.http_status})" if self.http_status else ""
            return f"BriteCore authentication failed{status_info} - {self.message}"

    class RateLimitError(Exception):
        """Raised when the API rate limit is exceeded (HTTP 429)."""

        def __init__(
            self,
            message: str,
            retry_after: int | None = None,
        ) -> None:
            self.message = message
            self.retry_after = retry_after
            super().__init__(self.message)

        def __str__(self) -> str:
            retry_info = f" Retry after {self.retry_after}s." if self.retry_after else ""
            return f"BriteCore rate limit exceeded - {self.message}.{retry_info}"

    class ServerError(Exception):
        """Raised when the API returns a 5xx server error."""

        def __init__(
            self,
            message: str,
            http_status: int | None = None,
        ) -> None:
            self.message = message
            self.http_status = http_status
            super().__init__(self.message)

        def __str__(self) -> str:
            status_info = f" (HTTP {self.http_status})" if self.http_status else ""
            return f"BriteCore server error{status_info} - {self.message}"

    class ConfigurationError(Exception):
        """Raised when the client is misconfigured (missing base_url, api_key, etc.)."""

        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return f"BriteCore configuration error - {self.message}"

    class RequestTimeoutError(Exception):
        """Raised when an API request exceeds its configured timeout."""

        def __init__(
            self,
            message: str,
            timeout_seconds: int | float | None = None,
        ) -> None:
            self.message = message
            self.timeout_seconds = timeout_seconds
            super().__init__(self.message)

        def __str__(self) -> str:
            timeout_info = f" (timeout={self.timeout_seconds}s)" if self.timeout_seconds else ""
            return f"BriteCore request timed out{timeout_info} - {self.message}"
