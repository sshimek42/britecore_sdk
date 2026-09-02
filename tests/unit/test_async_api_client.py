"""Unit tests for async API client caching support."""

import asyncio
import builtins
import time
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from urllib3.util import Timeout

from britecore_sdk.api import (
    AsyncBritecoreAPIClient,
    RequestCache,
    build_cache_key,
)
from britecore_sdk.api.britecore_api_client import (
    BritecoreAPIClient,
    RequestParameters,
)
from britecore_sdk.api.britecore_async_api_client import (
    _has_header_case_insensitive,
    _sanitize_body_for_errors,
    _timeout_seconds,
)
from britecore_sdk.api.request_cache import _canonicalize
from britecore_sdk.exceptions import BritecoreError


def _make_response(
    payload: bytes = b'{"success": true, "data": {"id": "1"}}',
    status: int = 200,
) -> MagicMock:
    response = MagicMock()
    response.status = status
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
            "dry_run",
            "dry_run_include_sensitive_headers",
        ):
            assert field_name in annotations

    @pytest.mark.unit
    def test_canonicalize_handles_list_and_tuple(self):
        """_canonicalize should recurse into lists and tuples."""
        assert _canonicalize([3, 1, 2]) == [3, 1, 2]
        assert _canonicalize((1, "a")) == [1, "a"]

    @pytest.mark.unit
    def test_canonicalize_handles_set(self):
        """_canonicalize should sort set members into a stable list."""
        result = _canonicalize({3, 1, 2})
        assert result == [1, 2, 3]

    @pytest.mark.unit
    def test_cache_set_ignores_non_positive_ttl(self):
        """set() with ttl_seconds <= 0 must not store an entry."""
        cache = RequestCache()
        cache.set("key", "value", ttl_seconds=0)
        assert cache.get("key") is None

    @pytest.mark.unit
    def test_invalidate_namespace_empty_string_returns_zero(self):
        """invalidate_namespace('') should be a no-op returning 0."""
        cache = RequestCache()
        cache.set("k", "v", ttl_seconds=60, namespace="ns")
        assert cache.invalidate_namespace("") == 0

    @pytest.mark.unit
    def test_cache_clear_removes_all_entries(self):
        """clear() must empty the cache regardless of TTL."""
        cache = RequestCache()
        cache.set("a", 1, ttl_seconds=60)
        cache.set("b", 2, ttl_seconds=60)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    @pytest.mark.unit
    def test_prune_expired_removes_and_counts_expired_entries(self):
        """prune_expired() must remove stale entries and return the count."""
        cache = RequestCache()
        cache.set("old", "stale", ttl_seconds=60)
        cache.set("fresh", "ok", ttl_seconds=60)
        cache._entries["old"].expires_at = datetime.now(UTC) - timedelta(seconds=1)
        removed = cache.prune_expired()
        assert removed == 1
        assert cache.get("fresh") == "ok"


class TestAsyncTransportHelpers:
    """Tests for helper behavior used by the native async transport."""

    @pytest.mark.unit
    def test_has_header_case_insensitive_matches_ignoring_case_and_whitespace(self):
        """Authorization header detection should not depend on casing or padding."""
        headers = {" authorization ": "Bearer token", "X-Test": "1"}

        assert _has_header_case_insensitive(headers, "Authorization") is True
        assert _has_header_case_insensitive(headers, "authorization") is True
        assert _has_header_case_insensitive(headers, "X-Missing") is False

    @pytest.mark.unit
    def test_timeout_seconds_handles_scalars_timeout_objects_and_unknown_values(self):
        """Timeout helper should normalize numbers and urllib3 Timeout instances."""
        assert _timeout_seconds(7) == 7
        assert _timeout_seconds(2.5) == 2.5
        assert _timeout_seconds(Timeout(total=9)) == 9
        assert _timeout_seconds(Timeout(total=None, connect=4, read=6)) == 4
        assert _timeout_seconds(object()) is None

    @pytest.mark.unit
    def test_sanitize_body_for_errors_redacts_nested_sensitive_values(self):
        """Sensitive keys should be redacted recursively across dict/list/tuple payloads."""
        body = {
            "api_key": "top-secret",
            "nested": {
                "token": "abc123",
                "safe": [{"password": "hidden"}, {"value": 5}],
                "tuple_data": ("keep", {"authorization": "Bearer x"}),
            },
        }

        sanitized = _sanitize_body_for_errors(body)

        assert sanitized["api_key"] == "***redacted***"
        assert sanitized["nested"]["token"] == "***redacted***"
        assert sanitized["nested"]["safe"][0]["password"] == "***redacted***"
        assert sanitized["nested"]["safe"][1]["value"] == 5
        assert sanitized["nested"]["tuple_data"][0] == "keep"
        assert sanitized["nested"]["tuple_data"][1]["authorization"] == "***redacted***"
        assert _sanitize_body_for_errors("plain") == "plain"


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
        mock_init.assert_called_once_with(client, client_dry_run=False)

    @pytest.mark.unit
    def test_aget_client_forwards_client_dry_run_to_sync_client(self):
        """aget_client should seed the sync client with the async dry-run default."""
        with patch.object(
            BritecoreAPIClient, "init_client", autospec=True
        ) as mock_init:
            adapter = AsyncBritecoreAPIClient(
                target_site="test_site",
                client_dry_run=True,
            )
            client = asyncio.run(adapter.aget_client())

        assert isinstance(client, BritecoreAPIClient)
        mock_init.assert_called_once_with(client, client_dry_run=True)

    @pytest.mark.unit
    def test_aget_client_forwards_explicit_credentials_to_sync_client(self):
        """Explicit async constructor credentials should be passed to sync init_client."""
        with patch.object(
            BritecoreAPIClient, "init_client", autospec=True
        ) as mock_init:
            adapter = AsyncBritecoreAPIClient(
                target_site="test_site",
                client_dry_run=True,
                base_url="https://api.example.com",
                api_key="api-key",
                client_id="client-id",
                client_secret="client-secret",
            )
            client = asyncio.run(adapter.aget_client())

        assert isinstance(client, BritecoreAPIClient)
        mock_init.assert_called_once_with(
            client,
            client_dry_run=True,
            base_url="https://api.example.com",
            api_key="api-key",
            client_id="client-id",
            client_secret="client-secret",
        )

    @pytest.mark.unit
    def test_constructor_rejects_unknown_async_transport(self):
        """Constructor should validate async transport selection."""
        with pytest.raises(ValueError):
            AsyncBritecoreAPIClient(
                target_site="test_site",
                async_transport="invalid",  # type: ignore[arg-type]
            )

    @pytest.mark.unit
    def test_ado_request_uses_httpx_transport_when_configured(self):
        """httpx mode should route request execution through native async transport."""
        response = _make_response()
        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with (
            patch.object(
                adapter,
                "_perform_request_httpx",
                new=AsyncMock(return_value=response),
            ) as mock_httpx_request,
            patch.object(client, "do_request") as mock_sync_request,
        ):
            result = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve", json={"policy_id": "123"}
                )
            )

        assert result is response
        mock_httpx_request.assert_awaited_once()
        mock_sync_request.assert_not_called()

    @pytest.mark.unit
    def test_httpx_transport_reuses_single_client_when_not_injected(self):
        """Native async mode should lazily create one httpx client and reuse it."""

        class _FakeAsyncClient:
            def __init__(self, timeout=None):
                self.timeout = timeout
                self.request_calls = 0
                self.closed = False

            async def request(self, **_kwargs):
                self.request_calls += 1
                return SimpleNamespace(
                    status_code=200,
                    reason_phrase="OK",
                    headers={},
                    content=b'{"success": true, "data": {"id": "ok"}}',
                )

            async def aclose(self):
                self.closed = True

        created_clients: list[_FakeAsyncClient] = []

        class _FakeHttpx:
            TimeoutException = Exception
            HTTPError = Exception

            @staticmethod
            def AsyncClient(timeout=None):
                client = _FakeAsyncClient(timeout=timeout)
                created_clients.append(client)
                return client

        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        client.base_url = "https://api.example.com"
        client.use_api_key = True
        client.site_settings = SimpleNamespace(api_key="k")
        client.rate_limiter = None

        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with patch.object(adapter, "_import_httpx", return_value=_FakeHttpx):
            first = asyncio.run(adapter.ado_request("/api/v2/test", cache_bypass=True))
            second = asyncio.run(adapter.ado_request("/api/v2/test", cache_bypass=True))

        assert first is not None
        assert second is not None
        assert len(created_clients) == 1
        assert created_clients[0].request_calls == 2

    @pytest.mark.unit
    def test_httpx_transport_aclose_closes_owned_client(self):
        """aclose() should close the lazily-created native async client."""

        class _FakeAsyncClient:
            def __init__(self, timeout=None):
                self.timeout = timeout
                self.closed = False

            async def request(self, **_kwargs):
                return SimpleNamespace(
                    status_code=200,
                    reason_phrase="OK",
                    headers={},
                    content=b'{"success": true, "data": {"id": "ok"}}',
                )

            async def aclose(self):
                self.closed = True

        created_clients: list[_FakeAsyncClient] = []

        class _FakeHttpx:
            TimeoutException = Exception
            HTTPError = Exception

            @staticmethod
            def AsyncClient(timeout=None):
                client = _FakeAsyncClient(timeout=timeout)
                created_clients.append(client)
                return client

        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        client.base_url = "https://api.example.com"
        client.use_api_key = True
        client.site_settings = SimpleNamespace(api_key="k")
        client.rate_limiter = None

        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with patch.object(adapter, "_import_httpx", return_value=_FakeHttpx):
            _ = asyncio.run(adapter.ado_request("/api/v2/test", cache_bypass=True))
            asyncio.run(adapter.aclose())

        assert len(created_clients) == 1
        assert created_clients[0].closed is True

    @pytest.mark.unit
    def test_async_context_manager_closes_owned_httpx_client_on_exit(self):
        """Async context-manager exit should delegate cleanup to aclose()."""

        class _ClosableAsyncClient:
            def __init__(self):
                self.closed = False

            async def aclose(self):
                self.closed = True

        closable_client = _ClosableAsyncClient()
        adapter = AsyncBritecoreAPIClient(async_transport="httpx")
        adapter._httpx_client = closable_client

        async def run_context() -> AsyncBritecoreAPIClient:
            async with adapter as entered:
                return entered

        entered = asyncio.run(run_context())

        assert entered is adapter
        assert closable_client.closed is True
        assert adapter._httpx_client is None

    @pytest.mark.unit
    def test_aclose_is_noop_for_injected_httpx_client(self):
        """Cleanup should not close an httpx client owned by the caller."""

        class _InjectedAsyncClient:
            def __init__(self):
                self.closed = False

            async def aclose(self):
                self.closed = True

        injected_client = _InjectedAsyncClient()
        adapter = AsyncBritecoreAPIClient(
            async_transport="httpx",
            httpx_client=injected_client,
        )

        asyncio.run(adapter.aclose())

        assert injected_client.closed is False
        assert adapter._httpx_client is injected_client

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
        assert second is not response
        assert getattr(second, "status", None) == 200
        mock_request.assert_called_once()

    @pytest.mark.unit
    def test_ado_request_caches_201_response_as_success(self):
        """2xx responses (for example 201) should be eligible for cache writes."""
        response = _make_response(status=201)
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        with patch.object(
            BritecoreAPIClient, "do_request", return_value=response
        ) as mock_request:
            first = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/create",
                    json={"policy_number": "POL-123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )
            second = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/create",
                    json={"policy_number": "POL-123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )

        assert first is response
        assert second is not response
        assert getattr(second, "status", None) == 201
        mock_request.assert_called_once()

    @pytest.mark.unit
    def test_snapshot_response_for_cache_none(self):
        """Snapshot helper should return None when no response exists."""
        assert AsyncBritecoreAPIClient._snapshot_response_for_cache(None) is None

    @pytest.mark.unit
    def test_restore_response_from_cache_none(self):
        """Restore helper should return None for empty cached values."""
        assert AsyncBritecoreAPIClient._restore_response_from_cache(None) is None

    @pytest.mark.unit
    def test_restore_response_from_cache_passthrough_non_snapshot(self):
        """Restore helper should passthrough values not marked as cache snapshots."""
        raw_value = {"plain": True}
        restored = AsyncBritecoreAPIClient._restore_response_from_cache(raw_value)
        assert restored is raw_value

    @pytest.mark.unit
    def test_restore_response_from_cache_returns_http_response(self):
        """Restore helper should rebuild a fresh urllib3 HTTPResponse from snapshot data."""
        cached_value = {
            "_cached_http_response": True,
            "status": 204,
            "reason": "No Content",
            "headers": {"X-SDK-Request-ID": "abc123"},
            "body": b"",
        }
        restored = AsyncBritecoreAPIClient._restore_response_from_cache(cached_value)
        assert restored is not None
        assert getattr(restored, "status", None) == 204
        assert getattr(restored, "reason", None) == "No Content"

    @pytest.mark.unit
    def test_request_with_optional_dedupe_returns_cached_value_before_task(self):
        """In-flight dedupe path should return cached value when available."""
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        async def run_once():
            return await adapter._request_with_optional_dedupe(
                path="/api/v2/test",
                json={"x": 1},
                request_timeout=None,
                request_retries=None,
                request_headers=None,
                method="POST",
                rate_limiter_bypass=False,
                dry_run=False,
                dry_run_include_sensitive_headers=False,
                dedupe_in_flight=True,
                cache_bypass=False,
                cache_enabled=True,
                cache_key="k1",
            )

        with (
            patch.object(
                adapter._cache, "get", return_value={"cached": True}
            ) as mock_get,
            patch.object(adapter, "_perform_request", new=AsyncMock()) as mock_perform,
        ):
            result = asyncio.run(run_once())

        assert result == {"cached": True}
        mock_get.assert_called_once_with("k1")
        mock_perform.assert_not_awaited()

    @pytest.mark.unit
    def test_cache_response_on_success_skips_non_2xx(self):
        """Cache writer should skip invalidation/writes when response is not HTTP-success."""
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))
        response = _make_response(status=500)

        with (
            patch.object(adapter._cache, "invalidate_namespaces") as mock_invalidate,
            patch.object(adapter._cache, "set") as mock_set,
        ):
            adapter._cache_response_on_success(
                response=response,
                cache_enabled=True,
                cache_bypass=False,
                cache_key="k2",
                cache_ttl_seconds=60,
                cache_namespace="policies",
                cache_invalidate_on_success=["policies"],
            )

        mock_invalidate.assert_not_called()
        mock_set.assert_not_called()

    @pytest.mark.unit
    def test_clear_cache_and_invalidate_delegate_to_request_cache(self):
        """Cache convenience methods should forward to the underlying RequestCache."""
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        with (
            patch.object(adapter._cache, "clear") as mock_clear,
            patch.object(
                adapter._cache, "invalidate_namespaces", return_value=2
            ) as mock_invalidate,
        ):
            adapter.clear_cache()
            invalidated = adapter.invalidate_cache_namespaces(["policies", "quotes"])

        mock_clear.assert_called_once_with()
        mock_invalidate.assert_called_once_with(["policies", "quotes"])
        assert invalidated == 2

    @pytest.mark.unit
    def test_cached_response_is_immutable_snapshot(self):
        """Mutating a live response should not mutate future cache hits."""
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))
        response = _make_response()

        with patch.object(BritecoreAPIClient, "do_request", return_value=response):
            first = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve",
                    json={"policy_id": "123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )
            first.status = 599
            second = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve",
                    json={"policy_id": "123"},
                    cache_enabled=True,
                    cache_namespace="policies",
                )
            )

        assert getattr(second, "status", None) == 200

    @pytest.mark.unit
    def test_ado_request_inherits_client_dry_run_and_bypasses_cache(self):
        """Default async dry-run should skip cache reads/writes and return synthetic payloads."""
        client = BritecoreAPIClient("test_site")
        client.client_dry_run = True
        client.base_url = "https://example.com"
        client.use_api_key = True

        class DummySettings:
            api_key = "test-key"

        client.site_settings = DummySettings()
        adapter = AsyncBritecoreAPIClient(client=client)

        with patch.object(
            client, "do_request", wraps=client.do_request
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

        assert mock_request.call_count == 2
        first_payload = client.process_result(first)
        second_payload = client.process_result(second)
        assert first_payload["dry_run"] is True
        assert second_payload["dry_run"] is True
        assert first_payload["request_id"] != second_payload["request_id"]

    @pytest.mark.unit
    def test_ado_request_explicit_false_overrides_client_dry_run(self):
        """Per-call dry_run=False should disable inherited async dry-run."""
        response = _make_response()
        client = BritecoreAPIClient("test_site")
        client.client_dry_run = True
        adapter = AsyncBritecoreAPIClient(client=client)

        with patch.object(
            BritecoreAPIClient, "do_request", return_value=response
        ) as mock_request:
            result = asyncio.run(
                adapter.ado_request(
                    "/api/v2/policies/retrieve",
                    json={"policy_id": "123"},
                    dry_run=False,
                )
            )

        assert result is response
        mock_request.assert_called_once()
        assert mock_request.call_args.kwargs["dry_run"] is False

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
        assert cached_again is not first_response
        assert getattr(cached_again, "status", None) == 200
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
    def test_async_oauth_dry_run_skips_token_acquisition(self, mock_settings_oauth):
        """Async dry-run should inherit sync OAuth auth-skip behavior."""
        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = mock_settings_oauth
            adapter = AsyncBritecoreAPIClient(
                target_site="test_site", client_dry_run=True
            )
            client = asyncio.run(adapter.aget_client())

        token_manager = client.token_class
        assert token_manager is not None

        with patch.object(token_manager, "get_authorization_headers") as mock_auth:
            response = asyncio.run(adapter.ado_request("/api/v2/test"))

        mock_auth.assert_not_called()
        payload = client.process_result(response)
        assert payload["dry_run"] is True
        assert payload["auth_mode"] == "oauth"
        assert payload["auth_skipped"] is True

    @pytest.mark.unit
    def test_import_httpx_raises_clear_error_when_dependency_is_missing(self):
        """Optional dependency failures should surface as SDK configuration errors."""
        original_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "httpx":
                raise ImportError("missing httpx")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            with pytest.raises(
                BritecoreError.ConfigurationError, match="httpx transport"
            ):
                AsyncBritecoreAPIClient._import_httpx()

    @pytest.mark.unit
    def test_import_httpx_returns_imported_module_when_available(self):
        """Lazy importer should return the resolved httpx module on success."""
        fake_httpx = SimpleNamespace(AsyncClient=object)
        original_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "httpx":
                return fake_httpx
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            imported = AsyncBritecoreAPIClient._import_httpx()

        assert imported is fake_httpx

    @pytest.mark.unit
    def test_httpx_transport_dry_run_delegates_to_sync_client(self):
        """Native async transport should still defer to sync dry-run behavior."""
        response = _make_response()
        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with (
            patch.object(client, "do_request", return_value=response) as mock_request,
            patch.object(adapter, "_import_httpx") as mock_import,
        ):
            result = asyncio.run(
                adapter._perform_request_httpx(
                    path="/api/v2/test",
                    json={"value": 1},
                    request_timeout=None,
                    request_retries=None,
                    request_headers=None,
                    method="POST",
                    rate_limiter_bypass=False,
                    dry_run=True,
                    dry_run_include_sensitive_headers=False,
                )
            )

        assert result is response
        mock_request.assert_called_once()
        mock_import.assert_not_called()

    @pytest.mark.unit
    def test_httpx_transport_requires_base_url(self):
        """Live httpx transport should fail fast when base_url is missing."""
        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        client.base_url = None
        client.use_api_key = True
        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with pytest.raises(
            BritecoreError.ConfigurationError, match="base_url not configured"
        ):
            asyncio.run(
                adapter._perform_request_httpx(
                    path="/api/v2/test",
                    json={"value": 1},
                    request_timeout=None,
                    request_retries=None,
                    request_headers=None,
                    method="POST",
                    rate_limiter_bypass=False,
                    dry_run=False,
                    dry_run_include_sensitive_headers=False,
                )
            )

    @pytest.mark.unit
    def test_httpx_transport_requires_oauth_token_manager_when_no_auth_header(self):
        """OAuth httpx mode should require a token manager when caller omits auth headers."""
        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        client.base_url = "https://api.example.com"
        client.use_api_key = False
        client.token_class = None
        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with pytest.raises(
            BritecoreError.ConfigurationError,
            match="OAuth token manager not initialized",
        ):
            asyncio.run(
                adapter._perform_request_httpx(
                    path="/api/v2/test",
                    json={"value": 1},
                    request_timeout=None,
                    request_retries=None,
                    request_headers={},
                    method="POST",
                    rate_limiter_bypass=False,
                    dry_run=False,
                    dry_run_include_sensitive_headers=False,
                )
            )

    @pytest.mark.unit
    def test_httpx_transport_acquires_rate_limiter_before_request(self):
        """Rate limiter should be consulted before issuing a live httpx request."""

        class _FakeAsyncClient:
            async def request(self, **_kwargs):
                return SimpleNamespace(
                    status_code=200,
                    reason_phrase="OK",
                    headers={},
                    content=b'{"success": true, "data": {"id": "ok"}}',
                )

        class _FakeHttpx:
            TimeoutException = Exception
            HTTPError = Exception

        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        client.base_url = "https://api.example.com"
        client.use_api_key = True
        client.site_settings = SimpleNamespace(api_key="secret")
        client.rate_limiter = MagicMock()
        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with (
            patch.object(adapter, "_import_httpx", return_value=_FakeHttpx),
            patch.object(
                adapter,
                "_get_or_create_httpx_client",
                new=AsyncMock(return_value=_FakeAsyncClient()),
            ),
        ):
            response = asyncio.run(
                adapter._perform_request_httpx(
                    path="/api/v2/test",
                    json={"value": 1},
                    request_timeout=Timeout(total=7),
                    request_retries=None,
                    request_headers=None,
                    method="POST",
                    rate_limiter_bypass=False,
                    dry_run=False,
                    dry_run_include_sensitive_headers=False,
                )
            )

        assert getattr(response, "status", None) == 200
        client.rate_limiter.acquire.assert_called_once_with(timeout=7)

    @pytest.mark.unit
    def test_httpx_transport_timeout_error_redacts_sensitive_body(self):
        """Timeout errors should include a redacted copy of the request payload."""

        class _FakeTimeoutError(Exception):
            pass

        class _FakeHttpx:
            TimeoutException = _FakeTimeoutError
            HTTPError = Exception

        class _TimeoutingAsyncClient:
            async def request(self, **_kwargs):
                raise _FakeTimeoutError("too slow")

        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        client.base_url = "https://api.example.com"
        client.use_api_key = True
        client.site_settings = SimpleNamespace(api_key="site-key")
        client.rate_limiter = None
        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with (
            patch.object(adapter, "_import_httpx", return_value=_FakeHttpx),
            patch.object(
                adapter,
                "_get_or_create_httpx_client",
                new=AsyncMock(return_value=_TimeoutingAsyncClient()),
            ),
        ):
            with pytest.raises(BritecoreError.RequestTimeoutError) as exc_info:
                asyncio.run(
                    adapter._perform_request_httpx(
                        path="/api/v2/test",
                        json={"password": "secret", "nested": {"token": "abc"}},
                        request_timeout=Timeout(total=5),
                        request_retries=None,
                        request_headers=None,
                        method="POST",
                        rate_limiter_bypass=False,
                        dry_run=False,
                        dry_run_include_sensitive_headers=False,
                    )
                )

        assert exc_info.value.timeout_seconds == 5
        assert exc_info.value.sanitized_body == {
            "password": "***redacted***",
            "nested": {"token": "***redacted***"},
            "api_key": "***redacted***",
        }

    @pytest.mark.unit
    def test_httpx_transport_http_error_redacts_sensitive_body(self):
        """Non-timeout httpx errors should raise NoDataReturned with redacted context."""

        class _FakeTimeoutError(Exception):
            pass

        class _FakeHTTPError(Exception):
            pass

        class _FakeHttpx:
            TimeoutException = _FakeTimeoutError
            HTTPError = _FakeHTTPError

        class _FailingAsyncClient:
            async def request(self, **_kwargs):
                raise _FakeHTTPError("network boom")

        client = BritecoreAPIClient("test_site")
        client.client_dry_run = False
        client.base_url = "https://api.example.com"
        client.use_api_key = False
        client.token_class = SimpleNamespace(
            get_authorization_headers=lambda: {"Authorization": "Bearer token"}
        )
        client.rate_limiter = None
        adapter = AsyncBritecoreAPIClient(client=client, async_transport="httpx")

        with (
            patch.object(adapter, "_import_httpx", return_value=_FakeHttpx),
            patch.object(
                adapter,
                "_get_or_create_httpx_client",
                new=AsyncMock(return_value=_FailingAsyncClient()),
            ),
        ):
            with pytest.raises(BritecoreError.NoDataReturned) as exc_info:
                asyncio.run(
                    adapter._perform_request_httpx(
                        path="/api/v2/test",
                        json={"secret_answer": "42", "payload": [1, 2, 3]},
                        request_timeout=Timeout(total=3),
                        request_retries=None,
                        request_headers=None,
                        method="POST",
                        rate_limiter_bypass=False,
                        dry_run=False,
                        dry_run_include_sensitive_headers=False,
                    )
                )

        assert exc_info.value.sanitized_body == {
            "secret_answer": "***redacted***",
            "payload": [1, 2, 3],
        }

    @pytest.mark.unit
    def test_aprocess_result_uses_sync_result_processing(self, mock_http_response):
        """aprocess_result should mirror the sync client's result processing."""
        adapter = AsyncBritecoreAPIClient(client=BritecoreAPIClient("test_site"))

        result = asyncio.run(adapter.aprocess_result(mock_http_response))

        assert result["id"] == "test_id"

    @pytest.mark.unit
    def test_acreate_contacts_batch_delegates_to_workflow_module(self):
        """acreate_contacts_batch should delegate to async workflow helper."""
        expected = {"total": 1, "succeeded": 1, "failed": 0, "results": []}
        mocked_helper = AsyncMock(return_value=expected)
        module = SimpleNamespace(acreate_contacts_batch=mocked_helper)

        with patch("importlib.import_module", return_value=module):
            result = asyncio.run(
                AsyncBritecoreAPIClient.acreate_contacts_batch([{"name": "A"}])
            )

        assert result == expected
        mocked_helper.assert_awaited_once()

    @pytest.mark.unit
    def test_acreate_policies_batch_delegates_to_workflow_module(self):
        """acreate_policies_batch should delegate to async workflow helper."""
        expected = {"total": 1, "succeeded": 1, "failed": 0, "results": []}
        mocked_helper = AsyncMock(return_value=expected)
        module = SimpleNamespace(acreate_policies_batch=mocked_helper)

        with patch("importlib.import_module", return_value=module):
            result = asyncio.run(
                AsyncBritecoreAPIClient.acreate_policies_batch(
                    [{"policy_number": "P1"}]
                )
            )

        assert result == expected
        mocked_helper.assert_awaited_once()

    @pytest.mark.unit
    def test_acreate_risks_batch_delegates_to_workflow_module(self):
        """acreate_risks_batch should delegate to async workflow helper."""
        expected = {"total": 1, "succeeded": 1, "failed": 0, "results": []}
        mocked_helper = AsyncMock(return_value=expected)
        module = SimpleNamespace(acreate_risks_batch=mocked_helper)

        with patch("importlib.import_module", return_value=module):
            result = asyncio.run(
                AsyncBritecoreAPIClient.acreate_risks_batch([{"revision_id": "R1"}])
            )

        assert result == expected
        mocked_helper.assert_awaited_once()

    @pytest.mark.unit
    def test_acreate_full_quotes_batch_delegates_to_workflow_module(self):
        """acreate_full_quotes_batch should delegate to async workflow helper."""
        expected = {"total": 1, "succeeded": 1, "failed": 0, "results": []}
        mocked_helper = AsyncMock(return_value=expected)
        module = SimpleNamespace(acreate_full_quotes_batch=mocked_helper)

        with patch("importlib.import_module", return_value=module):
            result = asyncio.run(
                AsyncBritecoreAPIClient.acreate_full_quotes_batch(
                    [{"quote_number": "Q1"}]
                )
            )

        assert result == expected
        mocked_helper.assert_awaited_once()
