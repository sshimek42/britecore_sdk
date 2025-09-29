"""Wrapper for BriteCore API calls"""

import sys
from json import dumps, loads
from typing import Any, Dict, Optional  # added typing

import sclogging.sclogging_main as scl
import urllib3
from britecore_exceptions import BritecoreError
from britecore_oauth_token_manager import OAuthToken
from urllib3.exceptions import (
    ProtocolError,
    RequestError,
    ResponseError,
)
from urllib3.exceptions import TimeoutError as urlTimeoutError
from urllib3.util import Retry, Timeout, Url

from britecore_libraries import settings

_LOGGER = scl.get_logger()
LOGGER_UPDATED = False


class LoadClientSettings:
    def __init__(self, target_site):
        self.target_site = target_site

    def load_config(self):
        target_site = self.target_site

        site_settings = settings.__getattr__("default")
        site_settings += settings.__getattr__(target_site)

        return site_settings


def _full_url(host: str, path: str) -> str:
    """Build a full URL using the configured base_url."""
    return Url(host=host, path=path).url


class BritecoreAPIClient:
    site_settings = None
    http = None
    token_class = None
    use_api_key = None
    web_retry = None
    web_timeout = None
    web_timeout_long = None
    base_url = None

    def __init__(self, target_site: str):
        self.api_key = None
        self.token_class = None
        self.use_api_key = None
        self.http = None
        self.web_retry = None
        self.web_timeout_long = None
        self.web_timeout = None
        self.base_url = None
        self.bad_url_error = None
        self.enable_timers = None
        self.site_settings = None
        self.target_site = target_site

    def init_client(self):
        target_site = self.target_site

        self._ensure_logger()

        self.site_settings = LoadClientSettings(target_site).load_config()
        BritecoreAPIClient.site_settings = self.site_settings

        self.enable_timers = True  # renamed from timers
        self.bad_url_error = "Invalid URL"  # renamed from bad_url_error

        if self.site_settings.base_url:
            self.base_url = self.site_settings.base_url
            self.base_url = Url(
                scheme="https", host=self.base_url, path=None).url
            if self.base_url.endswith("/"):
                self.base_url = self.base_url[:-1]
        else:
            _LOGGER.critical(self.bad_url_error)
            sys.exit(self.bad_url_error)

        BritecoreAPIClient.base_url = self.base_url

        self.web_timeout = self.site_settings.web_timeout
        if not self.web_timeout:
            self.web_timeout = self.site_settings.web_timeout = 5

        BritecoreAPIClient.web_timeout = self.web_timeout

        self.web_timeout_long = self.site_settings.web_timeout_long
        if not self.web_timeout_long:
            self.web_timeout_long = self.site_settings.web_timeout * 10

        BritecoreAPIClient.web_timeout_long = self.web_timeout_long

        self.web_retry = self.site_settings.web_retry
        if not self.web_retry:
            self.web_retry = 5

        BritecoreAPIClient.web_retry = self.web_retry

        timeout = Timeout(self.web_timeout)
        retries = Retry(
            total=self.web_retry, status_forcelist=frozenset({502, 503, 504})
        )
        self.http = urllib3.PoolManager(
            retries=retries, timeout=timeout, maxsize=5, num_pools=5
        )

        BritecoreAPIClient.http = self.http

        self.use_api_key = (
            self.site_settings.client_id == "" or self.site_settings.client_secret == ""
        )

        BritecoreAPIClient.use_api_key = self.use_api_key

        if self.use_api_key:
            _LOGGER.info(
                "client_id or client_secret not found. using api key.")
            try:
                self.api_key = self.site_settings.api_key
            except AttributeError:
                raise BritecoreError.BritecoreKeyError(
                    "api key not found. please set the api key in your "
                    "settings.py "
                    "file."
                )

        if self.use_api_key:
            self.token_class = None
        else:
            self.token_class = OAuthToken(
                self.site_settings.client_id,
                self.site_settings.client_secret,
                self.site_settings.base_url,
            )

        BritecoreAPIClient.token_class = self.token_class

    # helper utilities

    @classmethod
    def _ensure_logger(cls) -> None:
        """Ensure the module _LOGGER uses the parent _LOGGER if available (
        one-time)."""
        global _LOGGER
        global LOGGER_UPDATED
        if not LOGGER_UPDATED:
            plogger = scl.get_parent_logger()
            if plogger is not None:
                _LOGGER = plogger
                LOGGER_UPDATED = True

    @classmethod
    def process_result(cls, response: urllib3.HTTPResponse, logs: bool = False) -> Any:
        """Processes BriteCore response
        :param response: Request to parse
        :type response: HTTPResponse
        :param logs: Write full result to log
        :type logs: bool
        :return: Parsed data
        :rtype: Any
        """

        if response is None:
            _LOGGER.error("Error - No response")
            return None

        if response.status != 200:
            _LOGGER.error(f"Error - {response.status} - {response.reason}")
            return None

        json_result = loads(response.data.decode("utf-8"))

        result = json_result.get("success", None)
        message = json_result.get(
            "message", json_result.get("messages", "Unknown error")
        )

        if not result:
            _LOGGER.error(f"Error - {message}")
            return None

        data = json_result.get("data")
        if logs:
            _LOGGER.debug(data)

        if data is None:
            _LOGGER.warning("No data returned")

        return data

    @classmethod
    def do_request(
        cls,
        path: str,
        json: dict = None,
        request_timeout: urllib3.util.Timeout = None,
        request_retries: urllib3.util.Retry = None,
        request_headers: Optional[Dict[str, Any]] = None,
        # timer: bool = None,
        # timer_start_note: str = "",
        # timer_end_note: str = "",
        method: str = "POST",
    ) -> Optional[urllib3.HTTPResponse | urllib3.BaseHTTPResponse | None]:
        """Do web request
        :param path: URL to request
        :type path: str
        :param json: Request options
        :type json: dict
        :param request_timeout: urllib3 Timeout object
        :type request_timeout: urllib3.util.Timeout
        :param request_retries: urllib3 Retry object
        :type request_retries: urllib3.util.Retry
        :param request_headers: Headers (defaults to retrieving auth token)
        :type request_headers: dict
        # :param timer: Option to time request
        # :type timer: bool
        # :param timer_start_note: Note for start timer
        # :type timer_start_note: str
        # :param timer_end_note: Note for stop timer
        # :type timer_end_note: str
        :param method: POST, GET, etc.
        :type method: str
        :return: Request result
        :rtype: HTTPResponse | None
        """

        if not request_timeout:
            request_timeout = BritecoreAPIClient.web_timeout
        if not request_retries:
            request_retries = BritecoreAPIClient.web_retry

        if request_headers is None or BritecoreAPIClient.use_api_key:
            request_headers = {}
        if not request_headers and not BritecoreAPIClient.use_api_key:
            request_headers = BritecoreAPIClient.token_class.get_authorization_headers()

        request_url = _full_url(BritecoreAPIClient.base_url, path)

        request_result: Optional[urllib3.BaseHTTPResponse] = None
        try:
            if json:
                if BritecoreAPIClient.use_api_key:
                    json.update({"api_key": cls.site_settings.api_key})
                request_result = cls.http.request(
                    method=method,
                    url=request_url,
                    headers=request_headers,
                    body=dumps(json).encode("utf-8"),
                    timeout=request_timeout,
                    retries=request_retries,
                )
            else:
                if BritecoreAPIClient.use_api_key:
                    json = dumps(
                        {"api_key": cls.site_settings.api_key}).encode("utf-8")
                request_result = cls.http.request(
                    method=method,
                    url=request_url,
                    headers=request_headers,
                    timeout=request_timeout,
                    retries=request_retries,
                    body=json,
                )
        except (
            ProtocolError,
            ResponseError,
            urlTimeoutError,
            RequestError,
        ) as request_error:
            _LOGGER.error(request_error)

        if not request_result:
            _LOGGER.error("Error getting request")

        return request_result
