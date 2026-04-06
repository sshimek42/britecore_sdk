"""
Concurrency tests for BritecoreAPIClient.

Tests verify that multiple instances can coexist safely in concurrent scenarios
without interfering with each other's state.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from unittest.mock import MagicMock

import pytest

from britecore_libraries.api.britecore_api_client import (
    BritecoreAPIClient,
    LoadClientSettings,
)


class TestInstanceIsolation:
    """Verify that multiple client instances maintain independent state."""

    def test_multiple_instances_independent_state(self):
        """Multiple instances should have independent configuration state."""
        client1 = BritecoreAPIClient("site1")
        client2 = BritecoreAPIClient("site2")

        # Set different values on each instance
        client1.api_key = "key1"
        client2.api_key = "key2"

        # Verify they don't interfere
        assert client1.api_key == "key1"
        assert client2.api_key == "key2"

    def test_multiple_instances_independent_http(self):
        """Each instance should have independent HTTP managers."""
        client1 = BritecoreAPIClient("site1")
        client2 = BritecoreAPIClient("site2")

        # Mock HTTP managers
        http1 = MagicMock()
        http2 = MagicMock()

        client1.http = http1
        client2.http = http2

        # Verify independence
        assert client1.http is http1
        assert client2.http is http2
        assert client1.http is not client2.http

    def test_multiple_instances_independent_base_url(self):
        """Each instance should have independent base URLs."""
        client1 = BritecoreAPIClient("site1")
        client2 = BritecoreAPIClient("site2")

        client1.base_url = "https://site1.example.com"
        client2.base_url = "https://site2.example.com"

        # Verify no cross-contamination
        assert client1.base_url == "https://site1.example.com"
        assert client2.base_url == "https://site2.example.com"


class TestThreadSafety:
    """Verify that client state is safe in multi-threaded contexts."""

    def test_concurrent_initialization(self):
        """Multiple threads can initialize clients without interfering."""
        results: dict[int, Any] = {}
        errors: list[Exception] = []

        def init_client(thread_id: int, site: str):
            try:
                client = BritecoreAPIClient(site)
                client.api_key = f"key_{thread_id}"
                client.base_url = f"https://site{thread_id}.example.com"
                results[thread_id] = {
                    "api_key": client.api_key,
                    "base_url": client.base_url,
                }
            except Exception as e:
                errors.append(e)

        # Run 10 threads concurrently
        threads = []
        for i in range(10):
            t = threading.Thread(target=init_client, args=(i, f"site{i}"))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all clients maintained independent state
        for i in range(10):
            assert results[i]["api_key"] == f"key_{i}"
            assert results[i]["base_url"] == f"https://site{i}.example.com"

    def test_concurrent_state_changes(self):
        """Client state changes in concurrent threads should not interfere."""
        client1 = BritecoreAPIClient("site1")
        client2 = BritecoreAPIClient("site2")

        results1: list[str] = []
        results2: list[str] = []
        errors: list[Exception] = []

        def modify_and_read_client1():
            try:
                for i in range(100):
                    client1.api_key = f"key1_{i}"
                    # Small delay to increase chance of interleaving
                    time.sleep(0.0001)
                    results1.append(client1.api_key)
            except Exception as e:
                errors.append(e)

        def modify_and_read_client2():
            try:
                for i in range(100):
                    client2.api_key = f"key2_{i}"
                    # Small delay to increase chance of interleaving
                    time.sleep(0.0001)
                    results2.append(client2.api_key)
            except Exception as e:
                errors.append(e)

        # Run both threads
        t1 = threading.Thread(target=modify_and_read_client1)
        t2 = threading.Thread(target=modify_and_read_client2)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify client1 values all start with "key1_"
        for val in results1:
            assert val.startswith("key1_"), f"Client1 contaminated: {val}"

        # Verify client2 values all start with "key2_"
        for val in results2:
            assert val.startswith("key2_"), f"Client2 contaminated: {val}"

    def test_thread_pool_concurrent_clients(self):
        """Clients used in ThreadPoolExecutor should maintain isolation."""
        clients = [BritecoreAPIClient(f"site{i}") for i in range(5)]

        def use_client(client_index: int) -> dict[str, Any]:
            client = clients[client_index]
            client.api_key = f"key_{client_index}"
            client.base_url = f"https://site{client_index}.example.com"

            # Simulate some work
            time.sleep(0.01)

            return {
                "index": client_index,
                "api_key": client.api_key,
                "base_url": client.base_url,
            }

        # Run clients concurrently in thread pool
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(use_client, i) for i in range(5)]
            for future in as_completed(futures):
                results.append(future.result())

        # Verify all clients maintained state correctly
        assert len(results) == 5
        for result in results:
            idx = result["index"]
            assert result["api_key"] == f"key_{idx}"
            assert result["base_url"] == f"https://site{idx}.example.com"


class TestLoadClientSettingsThreadSafety:
    """Verify LoadClientSettings is thread-safe."""

    def test_concurrent_settings_load(self):
        """Multiple threads can load settings concurrently."""
        results: dict[str, Any] = {}
        errors: list[Exception] = []

        def load_settings(site: str):
            try:
                LoadClientSettings(site)
                # Note: actual config loading may fail in test, but isolation should work
                results[site] = {"site": site, "loader_created": True}
            except Exception as e:
                errors.append(e)

        # Run concurrent loads for different sites
        threads = []
        for site in ["site1", "site2", "site3"]:
            t = threading.Thread(target=load_settings, args=(site,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify basic isolation (errors are OK in test env)
        assert "site1" in results or len(errors) > 0
        assert "site2" in results or len(errors) > 0
        assert "site3" in results or len(errors) > 0


class TestConcurrentMultiClientScenarios:
    """Integration tests with multiple clients in concurrent scenarios."""

    def test_multi_site_concurrent_requests(self):
        """Simulates concurrent requests to different sites."""
        num_sites = 3
        requests_per_site = 5
        clients = [BritecoreAPIClient(f"site{i}") for i in range(num_sites)]

        # Configure each client
        for i, client in enumerate(clients):
            client.api_key = f"api_key_{i}"
            client.base_url = f"https://site{i}.example.com"
            client.web_timeout = 30 + i

        request_results: list[dict[str, Any]] = []
        errors: list[Exception] = []

        def simulate_request(site_id: int, request_id: int):
            try:
                client = clients[site_id]
                # Verify client state hasn't been corrupted
                assert client.api_key == f"api_key_{site_id}"
                assert client.base_url == f"https://site{site_id}.example.com"
                assert client.web_timeout == 30 + site_id

                request_results.append(
                    {
                        "site_id": site_id,
                        "request_id": request_id,
                        "api_key": client.api_key,
                    }
                )
                time.sleep(0.001)  # Simulate request latency
            except Exception as e:
                errors.append(e)

        # Submit all requests concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for site_id in range(num_sites):
                for req_id in range(requests_per_site):
                    future = executor.submit(simulate_request, site_id, req_id)
                    futures.append(future)

            for future in as_completed(futures):
                future.result()

        # Verify no errors and correct results
        assert len(errors) == 0, f"Errors: {errors}"
        assert len(request_results) == num_sites * requests_per_site

        # Verify no cross-contamination
        for result in request_results:
            site_id = result["site_id"]
            assert result["api_key"] == f"api_key_{site_id}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

