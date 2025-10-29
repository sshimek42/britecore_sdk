
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
            http_error: str | None = None
        ):
            self.message = message
            self.request = request
            self.http_error = http_error
            super().__init__(self.message)

        def __str__(self) -> str:
            return (
                f"BriteCore was unable to return any data - {self.message}\n"
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
            return "No target site assigned"
