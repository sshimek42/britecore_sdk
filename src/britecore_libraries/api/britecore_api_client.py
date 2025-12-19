"""Wrapper for BriteCore API calls"""

import os
import sys
from json import dumps, loads
from logging import Logger
from typing import Any, NotRequired, Optional, TypedDict  # added typing

import urllib3
from urllib3.exceptions import (
    ProtocolError,
    RequestError,
    ResponseError,
)
from urllib3.exceptions import (
    TimeoutError as urlTimeoutError,
)
from urllib3.util import Retry, Timeout, Url

from britecore_libraries import logger
from britecore_libraries.api.britecore_oauth_token_manager import OAuthToken
from britecore_libraries.config import settings
from britecore_libraries.exceptions import BritecoreError

LOGGER: Logger = logger


class LoadClientSettings:
    """
    Loads and manages client configuration settings for a specified target site.

    This class is responsible for initializing with a target site and loading
    configuration settings that combine default settings with site-specific
    overrides. It retrieves the target site from either constructor argument or
    environment variable and uses it to fetch appropriate settings.
    """

    def __init__(self, target_site: str) -> None:
        """
        Initialize the object with a target site.

        This constructor sets up the target site for the object. If no target site is
        provided during initialization, it attempts to retrieve the site from the
        environment variable 'target_site'. If the environment variable is not found,
        an error will be logged.

        Args:
            target_site: The target site to be set. If None or empty, the value will be
                retrieved from the 'target_site' environment variable.

        Raises:
            KeyError: If the 'target_site' environment variable is not set and no
                target_site is provided during initialization.
        """

        if not target_site:
            try:
                target_site = os.environ.get("target_site")
            except KeyError:
                LOGGER.error("Missing environment variable 'target_site'")
        self.target_site: str = target_site

    def load_config(self) -> Any:
        """
        Load and return configuration settings for the target site.

        This method retrieves the default configuration settings and merges them
        with site-specific settings based on the target site identifier.

        Returns:
            Any: Combined configuration settings for the target site
        """

        target_site: str = self.target_site

        site_settings: Any = settings.__getattr__("default")
        site_settings += settings.__getattr__(target_site)

        return site_settings


def _full_url(host: str, path: str) -> str:
    """
    Constructs a full URL from a host and path.

    This function takes a host string and a path string and combines them to
    form a complete URL using the Url class.

    Parameters:
        host (str): The host portion of the URL.
        path (str): The path portion of the URL.

    Returns:
        str: The complete URL formed by combining the host and path.
    """

    return Url(host=host, path=path).url


class BritecoreAPIClient:
    """
    Client for interacting with the Britecore API.

    This class provides functionality to initialize an API client with
    configuration settings, handle authentication using either API keys or
    OAuth tokens, and execute HTTP requests to Britecore API endpoints.
    """

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
        Initializes the Britecore API client with configuration settings and HTTP components.

        This method sets up the client by loading site-specific settings, configuring
        HTTP timeouts and retries, and initializing authentication components. It ensures
        that all necessary configuration parameters are present and valid before proceeding
        with client initialization.

        Raises:
            BritecoreError.NoSiteError: If no target site has been specified.
            BritecoreError.BritecoreKeyError: If api_key is not found when required.
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
            self.base_url = Url(scheme="https", host=self.base_url, path=None).url
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

        timeout: Timeout = Timeout(self.web_timeout)
        retries: Retry = Retry(
            total=self.web_retry,
            status_forcelist=frozenset({502, 503, 504, 500}),
            backoff_factor=0.5,
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
            LOGGER.info("client_id and/or client_secret not found. Using api_key.")
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
    def process_result(cls, response: urllib3.HTTPResponse, logs: bool = False) -> Any:
        """
        Process HTTP response and extract data from successful API calls.

        This class method handles the processing of HTTP responses from API calls,
        validating the response status, parsing JSON data, and raising appropriate
        exceptions for errors or missing data.

        Parameters:
            response: HTTPResponse object containing the API response
            logs: Boolean flag to enable debug logging of the response data

        Returns:
            Parsed data from the API response if successful

        Raises:
            BritecoreError.NoDataReturned: When response is None, status code is not 200,
                                           or the API returns a failure status
        """

        if response is None:
            LOGGER.error("Error - No response")
            raise BritecoreError.NoDataReturned("Error - No response")

        if response.status != 200:
            LOGGER.error(f"Error - {response.status} - {response.reason}")
            raise BritecoreError.NoDataReturned(
                f"Error - {response.status} - {response.reason}"
            )

        json_result: Any = loads(response.data.decode("utf-8"))

        result = json_result.get("success")
        message = json_result.get(
            "message", json_result.get("messages", "Unknown error")
        )

        if not result:
            LOGGER.error(f"Error - {message}")
            raise BritecoreError.NoDataReturned(f"Error - {message}")

        data: Any = json_result["data"]
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
        request_timeout: Optional[Timeout] = None,
        request_retries: Optional[Retry] = None,
        request_headers: Optional[dict[str, Any]] = None,
        method: Optional[str] = "POST",
    ) -> Optional[urllib3.HTTPResponse | urllib3.BaseHTTPResponse]:
        """
        Execute an HTTP request to the specified path with optional JSON payload and headers.

        This method constructs a full URL using the base URL and the provided path, then
        sends an HTTP request using the configured HTTP client. It handles API key
        injection into the JSON payload when required and manages request headers
        appropriately based on authentication settings.

        Parameters:
            path (str): The endpoint path to which the request is sent.
            json (Optional[dict[str, Any]]): The JSON payload to send with the request.
            request_timeout (Optional[Timeout]): The timeout configuration for the request.
            request_retries (Optional[Retry]): The retry configuration for the request.
            request_headers (Optional[dict[str, Any]]): Custom headers to include in the request.
            method (Optional[str]): The HTTP method to use for the request, defaults to "POST".

        Returns:
            Optional[urllib3.HTTPResponse | urllib3.BaseHTTPResponse]: The response from the HTTP request,
            or None if no response is received.

        Raises:
            BritecoreError.NoDataReturned: If the request fails due to network issues or if no response is returned from the server.
        """

        if not request_timeout:
            request_timeout = BritecoreAPIClient.web_timeout
        if not request_retries:
            request_retries = BritecoreAPIClient.web_retry

        if request_headers is None or BritecoreAPIClient.use_api_key:
            request_headers = {}
        if not request_headers and not BritecoreAPIClient.use_api_key:
            request_headers = BritecoreAPIClient.token_class.get_authorization_headers()

        request_url: str = _full_url(BritecoreAPIClient.base_url, path)

        try:
            if json:
                if BritecoreAPIClient.use_api_key:
                    json.update({"api_key": cls.site_settings.api_key})
                request_result: urllib3.BaseHTTPResponse = cls.http.request(
                    method=method,
                    url=request_url,
                    headers=request_headers,
                    body=dumps(json).encode("utf-8"),
                    timeout=request_timeout,
                    retries=request_retries,
                )
            else:
                if BritecoreAPIClient.use_api_key:
                    json = dumps({"api_key": cls.site_settings.api_key}).encode("utf-8")
                request_result: urllib3.BaseHTTPResponse = cls.http.request(
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
    def multiple_parameter_verification(
        cls, parameter_list: list[dict[str, str | None]], parameter_priority: list[str]
    ) -> dict[str, str | None]:
        """
        Verify multiple parameters and return the correct one based on priority.

        This method takes a list of parameter dictionaries and a priority list to determine
        which parameter should be used when multiple parameters are present. If multiple
        parameters are found, the method selects the one with the highest priority.
        If no parameters are found, it returns the first parameter from the priority list.

        :param parameter_list: List of dictionaries containing parameters
        :type parameter_list: list[dict[str, str | None]]
        :param parameter_priority: List of parameter names in order of priority
        :type parameter_priority: list[str]
        :return: Dictionary containing the selected parameter
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
                if non_empty_dict.get(each_priority):
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
    def json_dict_builder(cls, request_arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Takes all passed parameters and combines all non-empty values into
        one dictionary
        :param request_arguments: All arguments passed from a function
        :type request_arguments: dict[str,Any]
        """

        request_dict: dict[str, Any] = {}
        for _, (k, v) in enumerate(request_arguments.items()):
            if v:
                request_dict.update({k: v})

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
