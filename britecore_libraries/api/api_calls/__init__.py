import os

from api.britecore_api_client import BritecoreAPIClient, _LOGGER

_LOGGER = _LOGGER

def init_api_client(target_site = os.environ.get("target_site", None)):
    _api_client = BritecoreAPIClient(target_site)
    _api_client.init_client()
    return _api_client

api_client = init_api_client()
web_timeout_long = api_client.web_timeout_long
web_timeout = api_client.web_timeout