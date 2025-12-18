import os

from britecore_libraries.api.britecore_api_client import BritecoreAPIClient, RequestParameters


def init_api_client(target_site=os.environ.get("target_site")) -> BritecoreAPIClient:
    _api_client: BritecoreAPIClient = BritecoreAPIClient(target_site)
    _api_client.init_client()
    return _api_client


api_client: BritecoreAPIClient = init_api_client()
web_timeout_long: int = api_client.web_timeout_long
web_timeout: int = api_client.web_timeout

__all__ = ["RequestParameters", "api_client", "BritecoreAPIClient"]
