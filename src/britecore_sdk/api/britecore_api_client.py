"""Wrapper for BriteCore API calls"""

import time
import uuid
from json import JSONDecodeError, dumps, loads
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Any, NotRequired, Self, TypedDict  # added typing

if TYPE_CHECKING:
    import types

import urllib3
from urllib3.exceptions import (
    ProtocolError,
    RequestError,
    ResponseError,
)
from urllib3.exceptions import TimeoutError as urlTimeoutError
from urllib3.util import Retry, Timeout, Url

from britecore_sdk.api.britecore_oauth_token_manager import OAuthToken
from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.settings import settings
from britecore_sdk.settings.defaults import DEFAULTS, calculate_long_timeout

LOGGER: Logger = getLogger("britecore_sdk")


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

        This constructor sets up the target site for the object. The target site must be
        provided explicitly; no environment variable fallback is allowed.

        Args:
            target_site: The target site to be set. Must not be None or empty.

        Raises:
            ValueError: If no target_site is provided during initialization.
        """
        if not target_site:
            raise ValueError(
                "target_site must be specified explicitly; environment fallback is not allowed."
            )
        self.target_site: str = target_site

    def load_config(self) -> Any:
        """
        Load and return configuration settings for the target site.

        Switches Dynaconf into the target-site environment (which automatically
        inherits ``[default]`` values) and snapshots all needed keys into a
        plain ``SimpleNamespace`` so the result remains valid after the context
        exits.

        Returns:
            SimpleNamespace: Combined configuration settings for the target site.
        """
        from types import SimpleNamespace

        target_site: str = self.target_site

        with settings.using_env(target_site):
            return SimpleNamespace(
                base_url=settings.get("base_url", default=""),
                client_id=settings.get("client_id", default=""),
                client_secret=settings.get("client_secret", default=""),
                api_key=settings.get("api_key", default=""),
                web_retry=settings.get("web_retry"),
                web_timeout=settings.get("web_timeout"),
                web_timeout_long=settings.get("web_timeout_long"),
            )


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

    All state is instance-level; multiple clients can coexist in the same
    process without interfering with each other.
    """

    def __init__(self, target_site: str) -> None:
        """
        Initialize client state; call ``init_client`` before making requests.

        Args:
            target_site: The target site to be set. Must not be None or empty.

        Raises:
            ValueError: If no target_site is provided during initialization.
        """
        if not target_site:
            raise ValueError(
                "target_site must be specified explicitly; environment fallback is not allowed."
            )
        self.api_key: str | None = None
        self.token_class: OAuthToken | None = None
        self.use_api_key: bool | None = None
        self.http: urllib3.PoolManager | None = None
        self.web_retry: int | None = None
        self.web_timeout_long: int | None = None
        self.web_timeout: int | None = None
        self.base_url: str | None = None
        self.bad_url_error: str | None = None
        self.enable_timers: bool | None = None
        self.site_settings: Any = None
        self.default_dry_run: bool = False
        self.target_site = target_site

    def init_client(self, *, default_dry_run: bool = False) -> Self:
        """
        Initializes the Britecore API client with configuration settings and HTTP components.

        This method sets up the client by loading site-specific settings, configuring
        HTTP timeouts and retries, and initializing authentication components. It ensures
        that all necessary configuration parameters are present and valid before proceeding
        with client initialization.

        Returns:
            Self: The initialized client instance, allowing fluent one-liner construction::

                client = BritecoreAPIClient("my_site").init_client()

        Args:
            default_dry_run: When ``True``, requests inherit dry-run behavior unless a
                specific call passes ``dry_run=False``. This is useful for testing SDK
                wrapper flow and payload shaping without sending requests.

        Raises:
            BritecoreError.NoSiteError: If no target site has been specified.
            BritecoreError.BritecoreKeyError: If base_url or api_key is not found when required.
            ValueError: If target_site is not specified.
        """
        target_site = self.target_site
        if not target_site:
            raise ValueError(
                "target_site must be specified explicitly; environment fallback is not allowed."
            )
        self.site_settings = LoadClientSettings(target_site).load_config()
        self.default_dry_run = default_dry_run

        self.enable_timers = True
        self.bad_url_error = "Invalid URL"

        if self.site_settings.base_url:
            self.base_url = self.site_settings.base_url
            self.base_url = Url(scheme="https", host=self.base_url, path=None).url
            if self.base_url.endswith("/"):
                self.base_url = self.base_url[:-1]
        else:
            raise BritecoreError.BritecoreKeyError(
                "base_url not configured. Please set base_url in your "
                "settings.toml or .secrets.toml file.\n"
                "Tip: To check your site configuration, run: python -m britecore_sdk.utils.check_site_configs"
            )

        self.web_timeout = self.site_settings.web_timeout
        if not self.web_timeout:
            self.web_timeout = self.site_settings.web_timeout = DEFAULTS["web_timeout"]
        web_timeout = self.web_timeout
        assert web_timeout is not None

        self.web_timeout_long = self.site_settings.web_timeout_long
        if not self.web_timeout_long:
            self.web_timeout_long = self.site_settings.web_timeout_long = (
                calculate_long_timeout(web_timeout)
            )

        self.web_retry = self.site_settings.web_retry
        if not self.web_retry:
            self.web_retry = DEFAULTS["web_retry"]

        timeout: Timeout = Timeout(self.web_timeout)
        retries: Retry = Retry(
            total=self.web_retry,
            status_forcelist=frozenset({502, 503, 504, 500}),
            backoff_factor=0.5,
        )
        self.http = urllib3.PoolManager(
            retries=retries, timeout=timeout, maxsize=5, num_pools=5
        )

        self.use_api_key = (
            self.site_settings.client_id == "" or self.site_settings.client_secret == ""
        )

        if self.use_api_key:
            LOGGER.info("client_id and/or client_secret not found. Using api_key.")
            try:
                self.api_key = self.site_settings.api_key
            except AttributeError as attribute_error:
                raise BritecoreError.BritecoreKeyError(
                    "api_key not found. Please set the api_key in your "
                    ".secrets.toml file.\n"
                    "Tip: To check your site configuration, run: python -m britecore_sdk.utils.check_site_configs"
                ) from attribute_error
            self.token_class = None
        else:
            self.token_class = OAuthToken(
                self.site_settings.client_id,
                self.site_settings.client_secret,
                self.site_settings.base_url,
            )
        return self

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> Self:
        """Support ``with BritecoreAPIClient(...) as client:`` usage."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: "types.TracebackType | None",
    ) -> None:
        """Close the underlying urllib3 PoolManager on context-manager exit."""
        if self.http is not None:
            self.http.clear()
            self.http = None

    # ------------------------------------------------------------------
    # Developer-friendly repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        auth_mode = "api_key" if self.use_api_key else "oauth"
        initialized = self.http is not None
        return (
            f"BritecoreAPIClient("
            f"site={self.target_site!r}, "
            f"base_url={self.base_url!r}, "
            f"auth={auth_mode!r}, "
            f"initialized={initialized})"
        )

    @staticmethod
    def _extract_error_message(raw_message: Any) -> str:
        """Normalize API error payloads into a readable message string."""
        if isinstance(raw_message, list):
            return "; ".join(str(item) for item in raw_message)
        if isinstance(raw_message, dict):
            return str(raw_message)
        if raw_message is None:
            return "Unknown error"
        return str(raw_message)

    @staticmethod
    def _timeout_seconds(request_timeout: Any) -> int | float | None:
        """Extract a numeric timeout value from urllib3 timeout objects or scalars."""
        if isinstance(request_timeout, int | float):
            return request_timeout
        if isinstance(request_timeout, Timeout):
            for attr in ("total", "connect_timeout", "read_timeout"):
                value = getattr(request_timeout, attr, None)
                if isinstance(value, int | float):
                    return value
        return None

    @staticmethod
    def _with_hint(message: str, hint: str) -> str:
        """Append a short, actionable hint to an error message."""
        return f"{message}\nHint: {hint}"

    @staticmethod
    def _sanitize_dry_run_headers(
        headers: dict[str, Any], include_sensitive: bool = False
    ) -> dict[str, Any]:
        """Return dry-run-safe headers, redacting sensitive values by default."""
        if include_sensitive:
            return dict(headers)

        redacted_headers: dict[str, Any] = {}
        sensitive_markers = (
            "authorization",
            "token",
            "cookie",
            "secret",
            "password",
            "api-key",
            "apikey",
            "key",
        )
        for header_name, header_value in headers.items():
            normalized = header_name.strip().lower()
            if any(marker in normalized for marker in sensitive_markers):
                redacted_headers[header_name] = "***redacted***"
            else:
                redacted_headers[header_name] = header_value
        return redacted_headers

    @classmethod
    def _sanitize_dry_run_body(cls, body: Any) -> Any:
        """Return dry-run-safe request body with sensitive fields redacted."""
        sensitive_markers = (
            "authorization",
            "token",
            "secret",
            "password",
            "api-key",
            "apikey",
            "api_key",
            "key",
        )

        if isinstance(body, dict):
            redacted: dict[str, Any] = {}
            for key, value in body.items():
                normalized_key = str(key).strip().lower()
                if any(marker in normalized_key for marker in sensitive_markers):
                    redacted[key] = "***redacted***"
                else:
                    redacted[key] = cls._sanitize_dry_run_body(value)
            return redacted

        if isinstance(body, list):
            return [cls._sanitize_dry_run_body(item) for item in body]

        if isinstance(body, tuple):
            return [cls._sanitize_dry_run_body(item) for item in body]

        return body

    @staticmethod
    def _has_header(headers: dict[str, Any], header_name: str) -> bool:
        """Return ``True`` when a header exists using case-insensitive matching."""
        target = header_name.strip().lower()
        return any(existing.strip().lower() == target for existing in headers)

    @classmethod
    def _raise_for_http_status(
        cls,
        response: urllib3.HTTPResponse | urllib3.BaseHTTPResponse,
        endpoint: str | None = None,
    ) -> None:
        """Raise SDK exceptions for non-success HTTP statuses with endpoint context."""
        if response.status in {401, 403}:
            LOGGER.error(
                "Authentication error - %s - %s", response.status, response.reason
            )
            raise BritecoreError.AuthenticationError(
                cls._with_hint(
                    response.reason or "Unauthorized",
                    "Verify base_url and auth settings, then run: "
                    "python -m britecore_sdk.utils.healthcheck "
                    "(or add --site <site> to override).",
                ),
                http_status=response.status,
                endpoint=endpoint,
            )

        if response.status == 429:
            LOGGER.error("Rate limit exceeded")
            retry_after = None
            if hasattr(response, "headers") and response.headers:
                retry_after_val = response.headers.get("Retry-After")
                if retry_after_val is not None:
                    try:
                        retry_after = int(retry_after_val)
                    except (ValueError, TypeError):
                        pass
            raise BritecoreError.RateLimitError(
                cls._with_hint(
                    response.reason or "Too Many Requests",
                    "Retry with backoff and reduce request burst rate.",
                ),
                retry_after=retry_after,
            )

        if response.status >= 500:
            LOGGER.error("Server error - %s - %s", response.status, response.reason)
            raise BritecoreError.ServerError(
                cls._with_hint(
                    response.reason or "Internal Server Error",
                    "Retry shortly. If persistent, verify endpoint availability.",
                ),
                http_status=response.status,
                endpoint=endpoint,
            )

        if response.status == 404:
            LOGGER.error("Not found - %s", response.reason)
            raise BritecoreError.NotFoundError(
                cls._with_hint(
                    f"Error - {response.status} - {response.reason}",
                    "Confirm identifiers and endpoint path values.",
                ),
                http_status=response.status,
                endpoint=endpoint,
            )

        if response.status == 409:
            LOGGER.error("Conflict - %s", response.reason)
            raise BritecoreError.ConflictError(
                cls._with_hint(
                    f"Error - {response.status} - {response.reason}",
                    "Check for duplicate or conflicting resource updates.",
                ),
                http_status=response.status,
                endpoint=endpoint,
            )

        if response.status in {400, 422}:
            LOGGER.error("Validation error - %s - %s", response.status, response.reason)
            raise BritecoreError.ValidationError(
                cls._with_hint(
                    f"Error - {response.status} - {response.reason}",
                    "Validate request payload fields and required parameters.",
                ),
                http_status=response.status,
                endpoint=endpoint,
            )

        if response.status != 200:
            LOGGER.error("Error - %s - %s", response.status, response.reason)
            raise BritecoreError.NoDataReturned(
                cls._with_hint(
                    f"Error - {response.status} - {response.reason}",
                    "Review response status and run healthcheck for baseline validation.",
                ),
                http_status=response.status,
                endpoint=endpoint,
            )

    @staticmethod
    def _load_json_payload(
        response: urllib3.HTTPResponse | urllib3.BaseHTTPResponse,
    ) -> Any:
        """Decode and parse the JSON payload from a response object."""
        return loads(response.data.decode("utf-8"))

    @classmethod
    def _extract_success_data(cls, json_result: Any) -> Any:
        """Validate API success flag and return normalized data payload."""
        result = json_result.get("success")
        message = cls._extract_error_message(
            json_result.get("message", json_result.get("messages", "Unknown error"))
        )

        if not result:
            LOGGER.error("Error - %s", message)
            raise BritecoreError.NoDataReturned(
                cls._with_hint(
                    f"Error - {message}",
                    "Inspect API response payload and required request parameters.",
                )
            )

        return json_result.get("data")

    @classmethod
    def process_result(
        cls,
        response: urllib3.HTTPResponse | urllib3.BaseHTTPResponse | None,
        logs: bool = False,
        endpoint: str | None = None,
    ) -> Any:
        """
        Process HTTP response and extract data from successful API calls.

        This class method handles the processing of HTTP responses from API calls,
        validating the response status, parsing JSON data, and raising appropriate
        exceptions for errors or missing data.

        Parameters:
            response: HTTPResponse object containing the API response
            logs: Boolean flag to enable debug logging of the response data
            endpoint: Optional endpoint path for error context and diagnostics

        Returns:
            Parsed data from the API response if successful

        Raises:
            BritecoreError.NoDataReturned: When response is None, status code is not 200,
                                           or the API returns a failure status
        """
        if response is None:
            LOGGER.error("Error - No response")
            raise BritecoreError.NoDataReturned(
                cls._with_hint(
                    "Error - No response",
                    "Check network reachability, base_url, and client initialization.",
                ),
                endpoint=endpoint,
            )
        cls._raise_for_http_status(response, endpoint=endpoint)

        try:
            json_result: Any = cls._load_json_payload(response)
        except (JSONDecodeError, UnicodeDecodeError, AttributeError) as parse_error:
            LOGGER.error("Error parsing API response: %s", parse_error)
            raise BritecoreError.NoDataReturned(
                cls._with_hint(
                    f"Error parsing API response: {parse_error}",
                    "Enable debug logging and verify endpoint response content-type.",
                ),
                endpoint=endpoint,
            ) from parse_error

        data: Any = cls._extract_success_data(json_result)
        if logs:
            LOGGER.debug(data)

        if data is None:
            LOGGER.warning("No data returned")

        return data

    def do_request(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        request_timeout: Timeout | int | float | None = None,
        request_retries: Retry | int | None = None,
        request_headers: dict[str, Any] | None = None,
        method: str = "POST",
        cache_enabled: bool = False,
        cache_ttl_seconds: int | None = None,
        cache_namespace: str | None = None,
        cache_key_parts: list[str] | tuple[str, ...] | None = None,
        cache_bypass: bool = False,
        cache_invalidate_on_success: list[str] | tuple[str, ...] | None = None,
        dedupe_in_flight: bool = True,
        dry_run: bool | None = None,
        dry_run_include_sensitive_headers: bool = False,
    ) -> urllib3.HTTPResponse | urllib3.BaseHTTPResponse | None:
        """
        Execute an HTTP request to the specified path with optional JSON payload and headers.

        Parameters:
            path (str): The endpoint path to which the request is sent.
            json (Optional[dict[str, Any]]): The JSON payload to send with the request.
            request_timeout (Optional[Timeout]): The timeout configuration for the request.
            request_retries (Optional[Retry]): The retry configuration for the request.
            request_headers (Optional[dict[str, Any]]): Custom headers to include in the request.
            method (Optional[str]): The HTTP method to use for the request, defaults to "POST".
            dry_run (bool | None): If ``True``, log the full request details and return a
                synthetic successful response without sending the request. If ``None``,
                inherit the client's ``default_dry_run`` setting.
            dry_run_include_sensitive_headers (bool): If ``True``, include unredacted
                headers in dry-run logs/response. Defaults to ``False`` for safety.

        Returns:
            Optional[urllib3.HTTPResponse | urllib3.BaseHTTPResponse]: The response from the
            HTTP request.

        Raises:
            BritecoreError.RequestTimeoutError: If the request exceeds the configured timeout.
            BritecoreError.NoDataReturned: If the request fails due to other network issues.
        """
        if request_timeout is None:
            request_timeout = self.web_timeout
        if request_retries is None:
            request_retries = self.web_retry

        client_default_dry_run = bool(getattr(self, "default_dry_run", False))
        effective_dry_run = client_default_dry_run if dry_run is None else dry_run

        resolved_request_headers: dict[str, Any] = dict(request_headers or {})
        auth_mode = "api_key" if self.use_api_key else "oauth"
        caller_supplied_authorization = self._has_header(
            resolved_request_headers,
            "Authorization",
        )
        if (
            not effective_dry_run
            and not self.use_api_key
            and not caller_supplied_authorization
        ):
            token_manager = self.token_class
            if token_manager is None:
                raise BritecoreError.ConfigurationError(
                    "OAuth token manager not initialized"
                )
            resolved_request_headers.update(token_manager.get_authorization_headers())

        if not self.base_url:
            raise BritecoreError.ConfigurationError("base_url not configured")
        request_url: str = _full_url(self.base_url, path)

        # --- structured tracing -------------------------------------------------
        request_id: str = uuid.uuid4().hex[:8]
        _start: float = time.monotonic()
        LOGGER.debug(
            "[%s] → %s %s",
            request_id,
            method,
            path,
        )
        # Attach correlation ID to outbound headers so it appears in server logs
        resolved_request_headers["X-SDK-Request-ID"] = request_id

        request_body: dict[str, Any] = dict(json or {})
        if self.use_api_key:
            request_body.update({"api_key": self.site_settings.api_key})

        if effective_dry_run:
            dry_run_headers = self._sanitize_dry_run_headers(
                resolved_request_headers,
                include_sensitive=dry_run_include_sensitive_headers,
            )
            dry_run_body = self._sanitize_dry_run_body(request_body)
            auth_skipped = auth_mode == "oauth" and not caller_supplied_authorization
            LOGGER.info(
                "[%s] DRY-RUN %s %s  body=%s  headers=%s",
                request_id,
                method,
                request_url,
                dumps(dry_run_body),
                dry_run_headers,
            )
            dry_run_envelope = {
                "success": True,
                "data": {
                    "dry_run": True,
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "url": request_url,
                    "auth_mode": auth_mode,
                    "auth_skipped": auth_skipped,
                    "authorization_header_source": (
                        "caller-provided"
                        if caller_supplied_authorization
                        else (
                            "skipped-for-dry-run"
                            if auth_mode == "oauth"
                            else "request-body-api-key"
                        )
                    ),
                    "body": dry_run_body,
                    "headers": dry_run_headers,
                },
                "message": "Dry run: request was not sent.",
            }
            return urllib3.HTTPResponse(
                body=dumps(dry_run_envelope).encode("utf-8"),
                status=200,
                reason="DRY-RUN",
                headers={
                    "Content-Type": "application/json",
                    "X-SDK-Dry-Run": "true",
                    "X-SDK-Request-ID": request_id,
                },
                preload_content=True,
            )
        # ------------------------------------------------------------------------

        try:
            body_bytes: bytes | None = None
            if request_body:
                body_bytes = dumps(request_body).encode("utf-8")

            http_client = self.http
            if http_client is None:
                raise BritecoreError.ConfigurationError("HTTP client not initialized")

            request_result: urllib3.BaseHTTPResponse = http_client.request(
                method=method,
                url=request_url,
                headers=resolved_request_headers,
                body=body_bytes,
                timeout=request_timeout,
                retries=request_retries,
            )
        except urlTimeoutError as timeout_error:
            _elapsed_ms = (time.monotonic() - _start) * 1000
            LOGGER.error(
                "[%s] ✗ timeout after %.1fms — %s",
                request_id,
                _elapsed_ms,
                timeout_error,
            )
            raise BritecoreError.RequestTimeoutError(
                self._with_hint(
                    str(timeout_error),
                    "Increase request_timeout or retry settings for slow endpoints.",
                ),
                timeout_seconds=self._timeout_seconds(request_timeout),
            ) from timeout_error
        except (
            ProtocolError,
            ResponseError,
            RequestError,
        ) as request_error:
            _elapsed_ms = (time.monotonic() - _start) * 1000
            LOGGER.error(
                "[%s] ✗ request error after %.1fms — %s",
                request_id,
                _elapsed_ms,
                request_error,
            )
            raise BritecoreError.NoDataReturned(str(request_error)) from request_error

        if not request_result:
            LOGGER.error("[%s] ✗ no result object returned", request_id)
            raise BritecoreError.NoDataReturned("Error getting request")

        _elapsed_ms = (time.monotonic() - _start) * 1000
        LOGGER.debug(
            "[%s] ← HTTP %s  %.1fms",
            request_id,
            request_result.status,
            _elapsed_ms,
        )

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
        non_empty_dict: dict[str, str | None] = {}
        parameter_used: str = ""
        correct_parameter: dict[str, str | None] = {}

        for each_parameter in parameter_list:
            for k, v in each_parameter.items():
                if v:
                    non_empty_dict.update({k: v})

        if len(non_empty_dict) > 1:
            multiple_found = True
        elif not non_empty_dict:
            parameter_used = parameter_priority[0]
            correct_parameter = {parameter_used: None}
        else:
            parameter_used = list(non_empty_dict.keys())[0]
            correct_parameter = dict(non_empty_dict)

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

            LOGGER.debug("Sending %s", parameter_used)

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
    cache_enabled: NotRequired[bool]
    cache_ttl_seconds: NotRequired[int]
    cache_namespace: NotRequired[str]
    cache_key_parts: NotRequired[list[str] | tuple[str, ...]]
    cache_bypass: NotRequired[bool]
    cache_invalidate_on_success: NotRequired[list[str] | tuple[str, ...]]
    dedupe_in_flight: NotRequired[bool]
    dry_run: NotRequired[bool]
    dry_run_include_sensitive_headers: NotRequired[bool]
