"""Unit tests for async API client caching support."""

import asyncio
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from britecore_libraries.api import (
    AsyncBritecoreAPIClient,
    RequestCache,
    build_cache_key,
)
from britecore_libraries.api.britecore_api_client import (
    BritecoreAPIClient,
    RequestParameters,
)


def _make_response(
    payload: bytes = b'{"success": true, "data": {"id": "1"}}',
) -> MagicMock:
    response = MagicMock()
    response.status = 200
    response.reason = "OK"
    response.data = payload
    return response


class TestRequestCacheHelpers:
    """Tests for cache-key generation and TTL storage."""

    @pytest.mark.unit
    def test_build_cache_key_normalizes_payload_and_ignores_auth_header(self):
        """Equivalent requests should generate identical cache keys."""
        key_one = build_cache_key(
            target_site="test_site",
            method="post",
            path="/api/v2/policies/retrieve",
            json_payload={"b": 2, "a": 1},
            request_headers={"Authorization": "Bearer token-one", "X-Test": "1"},
            cache_namespace="policies",
            cache_key_parts=["policy:123"],
        )
        key_two = build_cache_key(
            target_site="test_site",
            method="POST",
            path="/api/v2/policies/retrieve",
            json_payload={"a": 1, "b": 2},
            request_headers={"authorization": "Bearer token-two", "X-Test": "1"},
            cache_namespace="policies",
            cache_key_parts=["policy:123"],
        )

        assert key_one == key_two

    @pytest.mark.unit
    def test_request_cache_prunes_expired_entries_and_invalidates_namespace(self):
        """Cache should drop expired entries and support namespace invalidation."""
        cache = RequestCache()
        cache.set("expired", "first", ttl_seconds=60, namespace="policies")
        cache.set("active", "second", ttl_seconds=60, namespace="quotes")
        cache._entries["expired"].expires_at = datetime.now(UTC) - timedelta(seconds=1)

        assert cache.get("expired") is None
        assert cache.get("active") == "second"
        assert cache.invalidate_namespace("quotes") == 1
        assert len(cache) == 0

    @pytest.mark.unit
    def test_request_parameters_expose_cache_fields(self):
        """Typed request parameters should include async cache controls."""
        annotations = RequestParameters.__annotations__

        for field_name in (
            "cache_enabled",
            "cache_ttl_seconds",
            "cache_namespace",
            "cache_key_parts",
            "cache_bypass",
            "cache_invalidate_on_success",
            "dedupe_in_flight",
        ):
            assert field_name in annotations


class TestAsyncBritecoreAPIClient:
    """Tests for async request execution and caching."""

    @pytest.mark.unit
    def test_async_api_client_is_exported(self):
        """The new async client should be importable from the api package."""
        assert AsyncBritecoreAPIClient is not None

    @pytest.mark.unit
    def test_aget_client_initializes_sync_client_lazily(self):
        """aget_client should create and initialize the sync client on first use."""
        with patch.object(
            BritecoreAPIClient, "init_client", autospec=True
        ) as mock_init:
            adapter = AsyncBritecoreAPIClient(target_site="test_site")
            client = asyncio.run(adapter.aget_client())

        assert isinstance(client, BritecoreAPIClient)
        assert client.target_site == "test_site"
        mock_init.assert_called_once_with(client)

    @pytest.mark.unit
    def test_ado_request_returns_cached_response_on_second_call(self):
        """Repeated identical requests should hit the in-memory cache."""
        response = _make_response()
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        with patch.object(
            BritecoreAPIClient, "do_request", return_value=response
        ) as mock_request:
            first = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve",
                    json={"policy_id": "123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )
            second = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve",
                    json={"policy_id": "123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )

        assert first is response
        assert second is response
        mock_request.assert_called_once()

    @pytest.mark.unit
    def test_ado_request_cache_bypass_skips_read_and_write(self):
        """Cache bypass should force a fresh request without replacing existing cache."""
        first_response = _make_response(b'{"success": true, "data": {"id": "first"}}')
        second_response = _make_response(b'{"success": true, "data": {"id": "second"}}')
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        with patch.object(
            BritecoreAPIClient,
            "do_request",
            side_effect=[first_response, second_response],
        ) as mock_request:
            cached = asyncio.run(
                adapter.ado_request(
                    "/api/v2/quotes/retrieve",
                    json={"quote_id": "Q1"},
                    cache_enabled=True,
                    cache_namespace="quotes",
                )
            )
            bypassed = asyncio.run(
                adapter.ado_request(
                    "/api/v2/quotes/retrieve",
                    json={"quote_id": "Q1"},
                    cache_enabled=True,
                    cache_namespace="quotes",
                    cache_bypass=True,
                )
            )
            cached_again = asyncio.run(
                adapter.ado_request(
                    "/api/v2/quotes/retrieve",
                    json={"quote_id": "Q1"},
                    cache_enabled=True,
                    cache_namespace="quotes",
                )
            )

        assert cached is first_response
        assert bypassed is second_response
        assert cached_again is first_response
        assert mock_request.call_count == 2

    @pytest.mark.unit
    def test_ado_request_invalidates_namespace_after_successful_mutation(self):
        """Successful mutation requests should invalidate targeted cache namespaces."""
        initial_response = _make_response(
            b'{"success": true, "data": {"id": "cached"}}'
        )
        mutation_response = _make_response(
            b'{"success": true, "data": {"id": "updated"}}'
        )
        refreshed_response = _make_response(
            b'{"success": true, "data": {"id": "fresh"}}'
        )
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        with patch.object(
            BritecoreAPIClient,
            "do_request",
            side_effect=[initial_response, mutation_response, refreshed_response],
        ) as mock_request:
            first = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve",
                    json={"policy_id": "123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )
            mutation = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/update",
                    json={"policy_id": "123", "status": "bound"},
                    cache_invalidate_on_success=["policies"],
                )
            )
            second = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve",
                    json={"policy_id": "123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )

        assert first is initial_response
        assert mutation is mutation_response
        assert second is refreshed_response
        assert mock_request.call_count == 3

    @pytest.mark.unit
    def test_ado_request_deduplicates_inflight_requests(self):
        """Concurrent identical requests should share a single network call."""
        response = _make_response()
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))
        call_count = 0

        def slow_request(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            time.sleep(0.05)
            return response

        async def run_requests():
            return await asyncio.gather(
                *[
                    adapter.ado_request(
                        "/api/v2/contacts/get",
                        json={"contact_id": "ABC"},
                        cache_enabled=True,
                        cache_namespace="contacts",
                        dedupe_in_flight=True,
                    )
                    for _ in range(5)
                ]
            )

        with patch.object(BritecoreAPIClient, "do_request", side_effect=slow_request):
            results = asyncio.run(run_requests())

        assert call_count == 1
        assert results == [response] * 5

    @pytest.mark.unit
    def test_aprocess_result_uses_sync_result_processing(self, mock_http_response):
        """aprocess_result should mirror the sync client's result processing."""
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        result = asyncio.run(adapter.aprocess_result(mock_http_response))

        assert result["id"] == "test_id"
