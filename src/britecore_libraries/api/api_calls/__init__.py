import os

from britecore_libraries.api.britecore_api_client import (
    BritecoreAPIClient,
    RequestParameters,
)


def init_api_client(target_site=os.environ.get("target_site")) -> BritecoreAPIClient:
    """
    Initializes and returns a configured Britecore API client instance.

    This function creates a new BritecoreAPIClient object using the specified target site
    and initializes the client connection. The target site can be provided as an argument
    or will default to the value of the 'target_site' environment variable.

    Args:
        target_site: The target site URL or identifier for the Britecore API.
                     Defaults to the value of the 'target_site' environment variable.

    Returns:
        BritecoreAPIClient: A configured and initialized Britecore API client instance.

    """

    _api_client: BritecoreAPIClient = BritecoreAPIClient(target_site)
    _api_client.init_client()
    return _api_client


api_client: BritecoreAPIClient = init_api_client()
web_timeout_long: int = api_client.web_timeout_long
web_timeout: int = api_client.web_timeout

__all__ = [
    "RequestParameters",
    "api_client",
    "BritecoreAPIClient",
    "web_timeout_long",
    "web_timeout",
]
