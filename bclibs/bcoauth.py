import sys
from datetime import datetime, timedelta
from json import loads
from types import MappingProxyType

import sclogging.sclogging_main as scl
import urllib3
from urllib3 import Retry, Timeout
from urllib3.util import Url

logger = scl.get_logger(__file__)
timeout = Timeout(10)
retries = Retry(total=5, status_forcelist=frozenset({502, 503, 504}))
http = urllib3.PoolManager(retries=retries, timeout=timeout, maxsize=5, num_pools=5)


class OAuthToken:
    """Class for retrieving OAuth2 token"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        url: str,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = Url(host=url, path="/api").url
        self.url = Url(host=url, path="/api/auth/oauth2/token").url
        self.token = ""
        self.token_time = datetime(1970, 1, 1)

    def get_token(self) -> [MappingProxyType[dict[str, str]], None]:
        """
        Returns bearer token
        :return: OAuth2 token
        :rtype: [MappingProxyType[dict[str, str]], None]
        """
        while self.token == "" or self.token_time < datetime.now():
            http_request = {"grant_type": "client_credentials", "scope": self.scope}
            http_header = urllib3.make_headers(
                basic_auth=f"{self.client_id}:{self.client_secret}"
            )
            logger.debug("Requesting token")
            http_result = http.request(
                "POST",
                self.url,
                fields=http_request,
                headers=http_header,
                encode_multipart=False,
            )

            if http_result.status != 200 and self.token == "":
                logger.critical(f"Error getting token - " f"{http_result.reason}")
                sys.exit(f"Error getting token - {http_result.reason}")
            else:
                logger.info("Received token")
                http_result_dict = loads(http_result.data)
                self.token = http_result_dict.get("access_token")
                self.token_time = (
                    datetime.now()
                    + timedelta(seconds=float(http_result_dict.get("expires_in")))
                    - timedelta(seconds=60)
                )

        request_head = MappingProxyType(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive",
            }
        )

        return request_head
