from datetime import datetime, timedelta
from json import loads
from types import MappingProxyType
from typing import Any, Mapping  # typing added

import urllib3
from urllib3 import BaseHTTPResponse, Retry, Timeout
from urllib3.util import Url, parse_url

from britecore_libraries import logger
from britecore_libraries.exceptions import BritecoreError

timeout: Timeout = Timeout(10)
retries: Retry = Retry(total=5, status_forcelist=frozenset({502, 503, 504}))
http: urllib3.PoolManager = urllib3.PoolManager(
    retries=retries, timeout=timeout, maxsize=5, num_pools=5
)

# Token safety buffer and default headers introduced to avoid magic literals
TOKEN_SKEW_SECONDS: int = 60
DEFAULT_HEADERS: dict[str, str] = {
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
    "Connection": "keep-alive",
}


class OAuthToken:
    """Class for retrieving OAuth2 token"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        url: str,
    ) -> None:
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        # Robustly parse incoming URL (with or without scheme) and rebuild endpoints
        parsed: Url = parse_url(url)
        scheme: str = parsed.scheme or "https"
        host: str = parsed.host or url  # fallback if a bare host was passed
        self.scope = Url(scheme=scheme, host=host, path="/api").url
        self.url = Url(scheme=scheme, host=host, path="/api/auth/oauth2/token").url
        self.token: str = ""
        self.token_time: datetime = datetime(1970, 1, 1)

    def _is_token_expired(self) -> bool:
        """Check whether the current token is missing or past its refresh time."""
        return not self.token or self.token_time < datetime.now()

    def _request_new_token(self) -> None:
        """Request and store a new OAuth2 token, exiting on fatal failure."""
        http_request: dict[str, str] = {
            "grant_type": "client_credentials",
            "scope": self.scope,
        }
        http_header: dict[str, str] = urllib3.make_headers(
            basic_auth=f"{self.client_id}:{self.client_secret}"
        )
        logger.debug("Requesting token")
        http_result: BaseHTTPResponse = http.request(
            "POST",
            self.url,
            fields=http_request,
            headers=http_header,
            encode_multipart=False,
        )
        if http_result.status != 200 and not self.token:
            raise BritecoreError.NoTokenReturned
        logger.debug("Received token")
        http_result_dict: Any = loads(http_result.data)
        self.token: str = http_result_dict.get("access_token", "")
        expires_in: float = float(http_result_dict.get("expires_in", 0))
        self.token_time: datetime = (
            datetime.now()
            + timedelta(seconds=expires_in)
            - timedelta(seconds=TOKEN_SKEW_SECONDS)
        )

    def _build_auth_headers(self) -> Mapping[str, str]:
        """Build immutable authorization headers using the current token."""
        request_headers: dict[str, str] = {
            "Authorization": f"Bearer {self.token}",
            **DEFAULT_HEADERS,
        }
        return MappingProxyType(request_headers)

    def get_authorization_headers(self) -> Mapping[str, str]:
        """
        Returns immutable headers containing a valid Bearer token.
        """
        if self._is_token_expired():
            self._request_new_token()
        return self._build_auth_headers()
