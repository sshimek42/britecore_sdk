"""Wrapper for BriteCore API calls"""

import os
import sys
from json import dumps, loads
from logging import Logger
from typing import Any, NotRequired, Optional, TypedDict  # added typing

from britecore_libraries import logger

import urllib3
from urllib3.exceptions import (
    ProtocolError, RequestError, ResponseError,
    TimeoutError as urlTimeoutError,
    )
from urllib3.util import Retry, Timeout, Url

from britecore_libraries.api.britecore_oauth_token_manager import OAuthToken
from britecore_libraries.config import settings
from britecore_libraries.exceptions import BritecoreError

LOGGER:Logger = logger

class LoadClientSettings:
    def __init__(self, target_site: str) -> None:
        if not target_site:
            try:
                target_site = os.environ.get("target_site")
            except KeyError:
                LOGGER.error("Missing environment variable 'target_site'")
        self.target_site:str = target_site

    def load_config(self) -> Any:
        target_site:str = self.target_site

        site_settings:Any = settings.__getattr__("default")
        site_settings += settings.__getattr__(target_site)

        return site_settings


def _full_url(host: str, path: str) -> str:
    """Build a full URL using the configured base_url."""
    return Url(host=host, path=path).url


class BritecoreAPIClient:

    site_settings: Any = None
    http: urllib3.PoolManager = None
    token_class: OAuthToken = None
    use_api_key: bool = None
    web_retry: int = None
    web_timeout: int = None
    web_timeout_long: int = None
    base_url: str = None

    def __init__(self, target_site: Optional[str]) -> None:

        self.api_key: Optional[str] = None
        self.token_class: Optional[OAuthToken] = None
        self.use_api_key: Optional[bool] = None
        self.http: Optional[urllib3.PoolManager] = None
        self.web_retry: Optional[int] = None
        self.web_timeout_long: Optional[int] = None
        self.web_timeout: Optional[int] = None
        self.base_url: Optional[str] = None
        self.bad_url_error: Optional[str] = None
        self.enable_timers: Optional[bool] = None
        self.site_settings: Any = None
        self.target_site = target_site

    def init_client(self) -> None:
        """
        Initialize API Client
        :return:
        :rtype: None
        """
        target_site = self.target_site

        if not target_site:
            raise BritecoreError.NoSiteError("No site has been specified")

        self.site_settings = LoadClientSettings(target_site).load_config()
        BritecoreAPIClient.site_settings = self.site_settings

        self.enable_timers = True  # renamed from timers
        self.bad_url_error = "Invalid URL"  # renamed from bad_url_error

        if self.site_settings.base_url:
            self.base_url = self.site_settings.base_url
            self.base_url = Url(
                scheme="https", host=self.base_url, path=None
                ).url
            if self.base_url.endswith("/"):
                self.base_url = self.base_url[:-1]
        else:
            logger.critical(self.bad_url_error)
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

        timeout:Timeout = Timeout(self.web_timeout)
        retries:Retry = Retry(
            total=self.web_retry,
            status_forcelist=frozenset({502, 503, 504, 500}),
            backoff_factor=0.5,
            )
        self.http = urllib3.PoolManager(
            retries=retries, timeout=timeout, maxsize=5, num_pools=5
            )

        BritecoreAPIClient.http = self.http

        self.use_api_key = (
                self.site_settings.client_id == "" or
                self.site_settings.client_secret == ""
        )

        BritecoreAPIClient.use_api_key = self.use_api_key

        if self.use_api_key:
            LOGGER.info(
                "client_id and/or client_secret not found. Using api_key."
                )
            try:
                self.api_key = self.site_settings.api_key
            except AttributeError:
                raise BritecoreError.BritecoreKeyError(
                    "api_key not found. Please set the api_key in your "
                    ".secrets.toml "
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


    @classmethod
    def process_result(
        cls, response: urllib3.HTTPResponse, logs: bool = False
        ) -> Any:
        """Processes BriteCore response
        :param response: Request to parse
        :type response: HTTPResponse
        :param logs: Write full result to log
        :type logs: bool
        :return: Parsed data
        :rtype: Any
        """

        if response is None:
            LOGGER.error("Error - No response")
            raise BritecoreError.NoDataReturned("Error - No response")

        if response.status != 200:
            LOGGER.error(f"Error - {response.status} - {response.reason}")
            raise BritecoreError.NoDataReturned(
                f"Error - {response.status} - {response.reason}"
                )

        json_result:Any = loads(response.data.decode("utf-8"))

        result = json_result.get("success", None)
        message = json_result.get(
            "message", json_result.get("messages", "Unknown error")
            )

        if not result:
            LOGGER.error(f"Error - {message}")
            raise BritecoreError.NoDataReturned(
                f"Error - {message}"
                )

        data:Any = json_result["data"]
        if logs:
            LOGGER.debug(data)

        if not data:
            LOGGER.warning("No data returned")

        return data

    @classmethod
    def do_request(
        cls,
        path: str,
        json: Optional[dict[str, Any]] = None,
        request_timeout: urllib3.util.Timeout = None,
        request_retries: urllib3.util.Retry = None,
        request_headers: Optional[dict[str, Any]] = None,
        method: Optional[str] = "POST",
        ) -> Optional[urllib3.HTTPResponse | urllib3.BaseHTTPResponse | None]:
        """Do web request
        :param path: URL to request
        :type path: str
        :param json: Dictionary to convert to JSON
        :type json: dict[str, Any]
        :param request_timeout: urllib3 Timeout object
        :type request_timeout: urllib3.util.Timeout
        :param request_retries: urllib3 Retry object
        :type request_retries: urllib3.util.Retry
        :param request_headers: Headers (defaults to retrieving auth token)
        :type request_headers: dict[str,str]
        :param method: POST, GET, etc. (Defaults to POST)
        :type method: str
        :return: Request result
        :rtype: urllib3.HTTPResponse | urllib3.BaseHTTPResponse | None
        """

        if not request_timeout:
            request_timeout = BritecoreAPIClient.web_timeout
        if not request_retries:
            request_retries = BritecoreAPIClient.web_retry

        if request_headers is None or BritecoreAPIClient.use_api_key:
            request_headers = {}
        if not request_headers and not BritecoreAPIClient.use_api_key:
            request_headers = (
                BritecoreAPIClient.token_class.get_authorization_headers())

        request_url:str = _full_url(BritecoreAPIClient.base_url, path)

        try:
            if json:
                if BritecoreAPIClient.use_api_key:
                    json.update({"api_key": cls.site_settings.api_key})
                request_result:urllib3.BaseHTTPResponse = cls.http.request(
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
                        {"api_key": cls.site_settings.api_key}
                        ).encode("utf-8")
                request_result:urllib3.BaseHTTPResponse = cls.http.request(
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
            LOGGER.error(request_error)
            raise BritecoreError.NoDataReturned(request_error)

        if not request_result:
            LOGGER.error("Error getting request")
            raise BritecoreError.NoDataReturned("Error getting request")

        return request_result

    @classmethod
    def multiple_parameter_verification(cls,
        parameter_list: list[dict[str, str | None]], parameter_priority: list[str]
    ) -> dict[str, str | None]:
        """
        Returns single dictionary from list of competing parameters
        :param parameter_list: List of dictionaries with possible conflicting values
        :type parameter_list: list[dict[str,str]]
        :param parameter_priority: List of keys in priority order
        :type parameter_priority: list[str]]
        :return: Returns the first non-empty dictionary in parameter_priority order or the first priority if all values are None
        :rtype: dict[str, str | None]
        """

        multiple_found: bool = False
        non_empty_dict: dict[str, str] = {}
        parameter_used: str = ""
        correct_parameter: dict[str, str | None] = {}

        for each_parameter in parameter_list:
            for k, v in each_parameter.items():
                if v:
                    non_empty_dict.update({k: v})

        if len(non_empty_dict) > 1:
            multiple_found = True
        else:
            parameter_used = list(non_empty_dict.keys())[0]
            correct_parameter = non_empty_dict

        if multiple_found:
            for each_priority in parameter_priority:
                if non_empty_dict.get(each_priority, None):
                    parameter_used = each_priority
                    correct_parameter = {
                        each_priority: non_empty_dict.get(each_priority)
                    }
                    break

            if not correct_parameter:
                parameter_used = parameter_priority[0]
                correct_parameter = {parameter_used: None}

            print(f"Sending {parameter_used}")

        return correct_parameter


    @classmethod
    def json_dict_builder(cls, request_arguments:dict[str, Any]) \
            -> dict[str,Any]:
        """
        Takes all passed parameters and combines all non-empty values into
        one dictionary
        :param request_arguments: All arguments passed from a function
        :type request_arguments: dict[str,Any]
        """
        request_dict: dict[str,Any] = {}
        for _, (k,v) in enumerate(request_arguments.items()):
            if v:
                request_dict.update({k:v})

        return request_dict


class RequestParameters(TypedDict):
    """
    Optional keyword parameters for HTTP request
    Attributes:
        request_timeout (urllib3.util.Timeout): Timeout settings
        request_retries (urllib3.util.Retry): Retry settings
        request_headers (dict[str, Any]): Request headers
        method (str): Request method (Default: "POST")
    """
    request_timeout: NotRequired[urllib3.util.Timeout]
    request_retries: NotRequired[urllib3.util.Retry]
    request_headers: NotRequired[dict[str, Any]]
    method: NotRequired[str]