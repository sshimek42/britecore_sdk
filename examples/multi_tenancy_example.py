"""Multi-tenancy example for britecore_sdk.

This example demonstrates patterns for managing multiple BriteCore sites/tenants
in a single application.

Usage:
    python examples/multi_tenancy_example.py
"""

from __future__ import annotations

import os

from britecore_sdk.api.api_calls import init_api_client, use_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Configuration for multiple sites
SITES_CONFIG: dict[str, dict[str, str]] = {
    "production": {
        "base_url": os.environ.get("PROD_BASE_URL", "api.prod.example.com"),
        "api_key": os.environ.get("PROD_API_KEY", "prod-key-xxx"),
    },
    "staging": {
        "base_url": os.environ.get("STAGING_BASE_URL", "api.staging.example.com"),
        "api_key": os.environ.get("STAGING_API_KEY", "staging-key-yyy"),
    },
    "qa": {
        "base_url": os.environ.get("QA_BASE_URL", "api.qa.example.com"),
        "api_key": os.environ.get("QA_API_KEY", "qa-key-zzz"),
    },
}


def example_1_sequential_site_processing() -> None:
    """Example 1: Process multiple sites sequentially (Pattern 2)."""
    print("\n=== Example 1: Sequential Multi-Site Processing ===\n")

    for site_name, creds in SITES_CONFIG.items():
        print(f"Processing site: {site_name}")

        # Initialize independent client for each site
        client = init_api_client(
            site_name,
            base_url=creds["base_url"],
            api_key=creds["api_key"],
            client_dry_run=True,  # Dry-run to avoid real API calls in example
        )

        # Make API call (dry-run doesn't send request)
        with use_api_client(client):
            result = policies.retrieve_policy(policy_number="POL001")
        print(f"  → Dry-run result: {result.get('dry_run', False)}")
        print(f"  → Client: {client!r}")
        print()


def example_2_context_manager_isolation() -> None:
    """Example 2: Use context manager for isolated operations (Pattern 3)."""
    print("=== Example 2: Context Manager for Isolation ===\n")

    sites = {
        "prod": (
            os.environ.get("PROD_BASE_URL", "api.prod.example.com"),
            os.environ.get("PROD_API_KEY", "prod-key"),
        ),
        "staging": (
            os.environ.get("STAGING_BASE_URL", "api.staging.example.com"),
            os.environ.get("STAGING_API_KEY", "staging-key"),
        ),
    }

    for site_name, (base_url, api_key) in sites.items():
        print(f"Processing {site_name}:")

        client = init_api_client(
            site_name, base_url=base_url, api_key=api_key, client_dry_run=True
        )
        with client:
            with use_api_client(client):
                result = policies.retrieve_policy(policy_number="POL001")
            print(f"  → Client: {client!r}")
            print(f"  → Dry-run: {result.get('dry_run', False)}")

        print("  → Connection pool closed on context exit")
        print()


def example_3_site_registry() -> None:
    """Example 3: Service registry pattern for long-lived clients (Pattern 4)."""
    print("=== Example 3: Service Registry (Long-Lived) ===\n")

    class SiteRegistry:
        """Manage clients for multiple sites."""

        def __init__(self):
            self._clients = {}

        def get(self, site_name: str) -> object:
            """Get or create a client for a site."""
            if site_name not in self._clients:
                creds = SITES_CONFIG[site_name]
                self._clients[site_name] = init_api_client(
                    site_name,
                    base_url=creds["base_url"],
                    api_key=creds["api_key"],
                    client_dry_run=True,
                )
            return self._clients[site_name]

        def cleanup(self) -> None:
            """Cleanup all clients."""
            for client in self._clients.values():
                client.__exit__(None, None, None)
            self._clients.clear()

    registry = SiteRegistry()

    # Reuse clients for multiple operations
    for site_name in SITES_CONFIG.keys():
        client = registry.get(site_name)
        print(f"{site_name}: Client reused ({client!r})")

    # Cleanup
    registry.cleanup()
    print("All clients cleaned up")
    print()


def example_4_bulk_operations() -> None:
    """Example 4: Bulk operations across sites."""
    print("=== Example 4: Bulk Operations ===\n")

    policy_numbers = ["POL001", "POL002", "POL003"]
    results_by_site = {}

    for site_name, creds in SITES_CONFIG.items():
        results_by_site[site_name] = {}

        client = init_api_client(
            site_name,
            base_url=creds["base_url"],
            api_key=creds["api_key"],
            client_dry_run=True,
        )

        with use_api_client(client):
            for policy_num in policy_numbers:
                result = policies.retrieve_policy(policy_number=policy_num)
                results_by_site[site_name][policy_num] = result.get("dry_run", False)
                print(
                    f"  {site_name}/{policy_num}: dry_run={result.get('dry_run', False)}"
                )

    print()


def example_5_error_handling() -> None:
    """Example 5: Handle errors gracefully across sites."""
    print("=== Example 5: Error Handling ===\n")

    # Simulate error by using invalid credentials
    invalid_sites = {
        "prod": ("https://invalid.example.com", "invalid-key"),
    }

    for site_name, (base_url, api_key) in invalid_sites.items():
        print(f"Attempting {site_name}...")
        try:
            client = init_api_client(
                site_name,
                base_url=base_url,
                api_key=api_key,
                client_dry_run=True,  # Dry-run avoids actual errors
            )
            with use_api_client(client):
                _ = policies.retrieve_policy(policy_number="POL001")
            print("  ✓ Success")
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")

    print()


def main() -> None:
    """Run all examples."""
    print("BriteCore SDK Multi-Tenancy Examples")
    print("=" * 50)

    # All examples use dry-run=True to avoid real API calls
    print("\nNote: All examples use dry_run=True (no real API calls)")

    example_1_sequential_site_processing()
    example_2_context_manager_isolation()
    example_3_site_registry()
    example_4_bulk_operations()
    example_5_error_handling()

    print("\n" + "=" * 50)
    print("Examples complete!\n")
    print("For production usage:")
    print("1. Set environment variables (PROD_BASE_URL, PROD_API_KEY, etc.)")
    print("2. Remove client_dry_run=True")
    print("3. Add logging (logging.getLogger('britecore_sdk').setLevel(logging.DEBUG))")
    print("4. See docs/MULTI_TENANCY.md for detailed patterns")


if __name__ == "__main__":
    main()
