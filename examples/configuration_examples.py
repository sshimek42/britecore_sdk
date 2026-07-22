"""
Example: Configuration Management

This example demonstrates:
- Different configuration approaches
- Environment variable usage
- File-based configuration
- Explicit credential passing
- Multi-site setup
"""

import os
from britecore_sdk.api.api_calls import init_api_client, get_api_client
from britecore_sdk.api.api_calls.v2 import policies


def example_1_environment_variables():
    """Example 1: Using environment variables for configuration."""
    print("Example 1: Environment Variable Configuration")
    print("-" * 50)

    # Set environment variables (in real usage, these would be set externally)
    # os.environ["BRITECORE_SDK_BASE_URL"] = "https://api.example.com"
    # os.environ["BRITECORE_SDK_API_KEY"] = "your_api_key"
    # os.environ["target_site"] = "production"

    print("Environment variables used:")
    print("  BRITECORE_SDK_BASE_URL - API base URL")
    print("  BRITECORE_SDK_API_KEY - API key")
    print("  BRITECORE_SDK_CLIENT_ID - OAuth client ID")
    print("  BRITECORE_SDK_CLIENT_SECRET - OAuth client secret")
    print("  target_site - Which site to use")
    print("\nSet these before initializing the client")


def example_2_file_configuration():
    """Example 2: File-based configuration (recommended)."""
    print("\n\nExample 2: File-Based Configuration")
    print("-" * 50)

    print("Create ~/.britecore/settings.toml:")
    print("""
[default]
target_site = "production"
""")

    print("\nCreate ~/.britecore/.secrets.toml:")
    print("""
[production]
base_url = "https://api.britecore.example.com"
api_key = "sk_live_your_api_key"

[staging]
base_url = "https://staging-api.britecore.example.com"
api_key = "sk_staging_your_api_key"
""")

    print("\nThen use lazy client (auto-loads config):")
    print("""
from britecore_sdk.api.api_calls import get_api_client

client = get_api_client()
""")


def example_3_explicit_credentials():
    """Example 3: Explicit credential passing (for serverless/containers)."""
    print("\n\nExample 3: Explicit Credential Passing")
    print("-" * 50)

    print("API Key authentication:")
    print("""
from britecore_sdk.api.api_calls import init_api_client

client = init_api_client(
    base_url="https://api.britecore.example.com",
    api_key="sk_live_your_api_key"
)
""")

    print("\nOAuth authentication:")
    print("""
from britecore_sdk.api.api_calls import init_api_client

client = init_api_client(
    base_url="https://api.britecore.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)
""")


def example_4_multi_site():
    """Example 4: Working with multiple sites."""
    print("\n\nExample 4: Multi-Site Configuration")
    print("-" * 50)

    print("Configuration for multiple sites:")
    print("""
# ~/.britecore/.secrets.toml
[production]
base_url = "https://prod-api.britecore.example.com"
api_key = "sk_live_prod_key"

[staging]
base_url = "https://staging-api.britecore.example.com"
api_key = "sk_staging_key"

[development]
base_url = "https://dev-api.britecore.example.com"
api_key = "sk_dev_key"
""")

    print("\nUsing different sites in code:")
    print("""
from britecore_sdk.api.api_calls import init_api_client, use_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Get from production
with use_api_client(init_api_client("production").init_client()):
    prod_policy = policies.retrieve_policy(policy_number="POL-123")

# Get from staging  
with use_api_client(init_api_client("staging").init_client()):
    staging_policy = policies.retrieve_policy(policy_number="POL-456")
""")


def example_5_context_manager():
    """Example 5: Using context manager for proper cleanup."""
    print("\n\nExample 5: Context Manager Pattern")
    print("-" * 50)

    print("Recommended pattern for resource cleanup:")
    print("""
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies

with BritecoreAPIClient("production").init_client() as client:
    policy = policies.retrieve_policy(policy_number="POL-123")
    # Work with policy
    print(policy)

# Connection automatically closed on exit
""")


def example_6_dry_run():
    """Example 6: Dry-run mode for testing."""
    print("\n\nExample 6: Dry-Run Testing")
    print("-" * 50)

    print("Test API interactions without sending real requests:")
    print("""
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Enable dry-run
init_api_client("production", client_dry_run=True)

# This logs the request but doesn't send it
result = policies.retrieve_policy(policy_number="POL-123")

print(result["dry_run"])  # True
print(result["auth_skipped"])  # True for OAuth
print(result["prepared_url"])  # URL that would be called
""")


def example_7_configuration_hierarchy():
    """Example 7: Configuration priority order."""
    print("\n\nExample 7: Configuration Priority (Lowest to Highest)")
    print("-" * 50)

    print("""
1. SDK package defaults
   → src/britecore_sdk/settings/settings.toml

2. User-level config
   → ~/.britecore/settings.toml
   → ~/.britecore/.secrets.toml

3. Project-local config
   → ./britecore.toml
   → ./.britecore_secrets.toml

4. Environment variable file
   → Path specified by BRITECORE_SDK_SETTINGS_FILE

5. Environment variables (HIGHEST PRIORITY)
   → BRITECORE_SDK_BASE_URL
   → BRITECORE_SDK_API_KEY
   → BRITECORE_SDK_CLIENT_ID
   → BRITECORE_SDK_CLIENT_SECRET
   → target_site

This means environment variables override all file-based config.
""")


def main():
    """Run all configuration examples."""
    print("=" * 50)
    print("BriteCore SDK - Configuration Examples")
    print("=" * 50)

    example_1_environment_variables()
    example_2_file_configuration()
    example_3_explicit_credentials()
    example_4_multi_site()
    example_5_context_manager()
    example_6_dry_run()
    example_7_configuration_hierarchy()

    print("\n" + "=" * 50)
    print("Next Steps:")
    print("1. Create ~/.britecore/.secrets.toml with your credentials")
    print("2. Set target_site in ~/.britecore/settings.toml")
    print("3. Run: britecore-check-config")
    print("4. Run: britecore-healthcheck")
    print("\nSee docs/CONFIGURATION.md for detailed information")


if __name__ == "__main__":
    main()

