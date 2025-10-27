class BritecoreError:
    """
    Defines a collection of custom exceptions related to Britecore
    applications.

    This classes provides specific error types for handling various situations
    such as
    invalid data, missing tokens, or invalid input formats. It is designed
    to be used
    as part of error handling mechanisms in systems interacting with
    Britecore APIs.
    """

    class NoDataReturned(Exception):
        def __init__(self, message, request=None, http_error=None):
            self.message = message
            self.request = request
            self.http_error = http_error
            super().__init__(self.message)

        def __str__(self):
            return (
                f"BriteCore was unable to return any data - {self.message}\n"
                f"Request: {self.request}\n"
                f"HTTP Error: {self.http_error}"
            )

    class NoTokenReturned(Exception):
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
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

        def __str__(self):
            return f"Invalid Phone Number - {self.message}"

    class InvalidEmailAddress(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

        def __str__(self) -> str:
            return f"Invalid E-Mail Address - {self.message}"

    class InvalidAddress(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

        def __str__(self):
            return f"Invalid Address - {self.message}"

    class BritecoreKeyError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

        def __str__(self):
            return {self.message}

    class NoSiteError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

        def __str__(self):
            return f"No target site assigned"
