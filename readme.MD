### **Core Components**

1.  **`britecore_api_client.py`**:
    *   **Main Client Class**: `BritecoreAPIClient` is the central class managing API interactions.
    *   **Initialization (`init_client`)**:
        *   Loads configuration settings for the specified `target_site` (from environment or parameter).
        *   Sets up `urllib3.PoolManager` with retry logic and timeout settings.
        *   Determines authentication method (API Key vs OAuth2) based on credentials.
        *   Initializes `OAuthToken` manager if OAuth is needed.
    *   **Core Methods**:
        *   `do_request`: Handles the actual HTTP request (POST/GET) using `urllib3`, including authentication headers and error handling.
        *   `process_result`: Parses the HTTP response, checks for errors, and returns the data payload.
        *   `multiple_parameter_verification`: Resolves conflicts when multiple parameters are provided, prioritizing based on a defined list.
        *   `json_dict_builder`: Constructs a clean dictionary from function arguments, filtering out `None` values.

2.  **`britecore_oauth_token_manager.py`**:
    *   **OAuth2 Token Handling**: Manages retrieving and refreshing OAuth2 access tokens.
    *   **Key Features**:
        *   Stores token and its expiry time.
        *   Automatically requests a new token if expired or missing.
        *   Provides `get_authorization_headers()` for including the token in API requests.

3.  **`api_calls` Directory**:
    *   **Versioned API Endpoints**: Contains modules for different API versions (`v1`, `v2`).
    *   **`__init__.py`**: Exposes functions from `v2` by default, making them easily importable.
    *   **`v2` Module**: Houses specific API call functions organized by category (e.g., `policies`, `quotes`, `reports`, `utils`).
        *   **Example Functions**:
            *   `policies.create_risk`, `policies.update_property_location`, `policies.new_revision_contact`
            *   `quotes.create_full_quote`, `quotes.get_quote`
            *   `reports.retrieve_reports`, `reports.retrieve_report`
            *   `utils.get_available_function_names`, `utils.rebuild_search_index`
        *   **Usage Pattern**: Each function constructs a request dictionary, calls `api_client.do_request` with the appropriate path and JSON data, and processes the result using `api_client.process_result`.

4.  **`__init__.py` (Top-Level)**:
    *   **API Client Initialization**: `init_api_client()` function initializes the `BritecoreAPIClient` with a specified site and stores it in `api_client`.
    *   **Exports**: Exports `RequestParameters` type for optional request configuration.

### **Key Features and Design Patterns**

1.  **Authentication Management**:
    *   Supports both API Key and OAuth2 authentication methods, automatically selecting the appropriate one based on configuration.
    *   Uses `urllib3` for robust HTTP handling with retries and timeouts.

2.  **Modular API Endpoints**:
    *   Functions are grouped logically by API resource (e.g., policies, quotes, reports).
    *   Each function abstracts the complexity of constructing the request and handling the response.

3.  **Error Handling**:
    *   Leverages `urllib3` exceptions for network issues.
    *   Uses a custom `BritecoreError` exception class for API-specific errors (e.g., no data returned, no token returned).

4.  **Configuration Management**:
    *   Uses `britecore_libraries.config.settings` to load configuration from environment variables or `.toml` files.

5.  **Type Hinting and Typing**:
    *   Extensive use of Python typing (`typing`, `TypedDict`) for better code documentation and IDE support.

6.  **Reusability**:
    *   Centralized `BritecoreAPIClient` and `OAuthToken` classes ensure consistent authentication and HTTP handling across all API calls.

### **Example Usage**

```python
# Initialize the client (usually done once at application startup)
from britecore_libraries import api_client # This sets up the client
# Or manually: from britecore_libraries.api import init_api_client
# api_client = init_api_client(target_site="my_site")

# Import specific API functions
from britecore_libraries.api.api_calls.v2 import policies, quotes

# Create a quote
quote_data = {
    # ... quote data ...
}
quote_json, quote_id = quotes.create_full_quote(quote_data)

# Get a policy snapshot
snapshot = policies.retrieve_policy_snapshot(
    policy_number="POL123456",
    snapshot_date="2023-10-01"
)

# Use custom request parameters (e.g., custom timeout)
from urllib3.util import Timeout
custom_timeout = Timeout(connect=10, read=20)
result = policies.retrieve_policy_snapshot(
    policy_number="POL123456",
    snapshot_date="2023-10-01",
    request_timeout=custom_timeout
)
```


This structure provides a clean, maintainable, and extensible way to interact with the BriteCore API, abstracting away the underlying HTTP details and offering a high-level interface for developers.