"""Regression tests for api_calls client state and lazy proxy behavior."""

import importlib
import warnings
from unittest.mock import MagicMock

import pytest

import britecore_sdk.api.api_calls as api_calls_module


class TestApiCallsClientState:
    """Validate that explicit init_* calls seed the lazy global client proxies."""

    @pytest.mark.unit
    def test_init_api_client_sets_global_for_lazy_proxy(self, monkeypatch):
        """init_api_client(target_site) stores state used by api_client proxy."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        fake_client = MagicMock()
        fake_client.token = "ready"
        fake_ctor = MagicMock(return_value=fake_client)
        monkeypatch.setitem(module.__dict__, "BritecoreAPIClient", fake_ctor)

        with pytest.warns(DeprecationWarning, match=r"init_api_client\(\)"):
            returned = module.init_api_client("test-site")

        assert returned is fake_client
        assert module._api_client is fake_client
        fake_ctor.assert_called_once_with("test-site")
        fake_client.init_client.assert_called_once_with(
            client_dry_run=False, enable_rate_limiter=None
        )

        # Access through lazy proxy must reuse seeded global client.
        assert module.api_client.token == "ready"
        fake_ctor.assert_called_once()

    @pytest.mark.unit
    def test_init_api_client_emits_deprecation_warning(self, monkeypatch):
        """init_api_client should warn that explicit client construction is preferred."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        fake_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_client)
        monkeypatch.setitem(module.__dict__, "BritecoreAPIClient", fake_ctor)

        with pytest.warns(DeprecationWarning, match=r"init_api_client\(\)"):
            module.init_api_client("test-site")

    @pytest.mark.unit
    def test_init_api_client_forwards_client_dry_run(self, monkeypatch):
        """init_api_client(client_dry_run=True) forwards the client dry-run default."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        fake_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_client)
        monkeypatch.setitem(module.__dict__, "BritecoreAPIClient", fake_ctor)

        with pytest.warns(DeprecationWarning, match=r"init_api_client\(\)"):
            module.init_api_client("test-site", client_dry_run=True)

        fake_ctor.assert_called_once_with("test-site")
        fake_client.init_client.assert_called_once_with(
            client_dry_run=True, enable_rate_limiter=None
        )

    @pytest.mark.unit
    def test_init_async_api_client_sets_global_for_lazy_proxy(self, monkeypatch):
        """init_async_api_client(target_site) stores state used by async proxy."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        fake_async_client = MagicMock()
        fake_async_client.token = "async-ready"
        fake_ctor = MagicMock(return_value=fake_async_client)
        monkeypatch.setitem(module.__dict__, "AsyncBritecoreAPIClient", fake_ctor)

        with pytest.warns(DeprecationWarning, match=r"init_async_api_client\(\)"):
            returned = module.init_async_api_client("test-site")

        assert returned is fake_async_client
        assert module._async_api_client is fake_async_client
        fake_ctor.assert_called_once_with("test-site", client_dry_run=False)

        # Access through lazy proxy must reuse seeded global async client.
        assert module.async_api_client.token == "async-ready"
        fake_ctor.assert_called_once()

    @pytest.mark.unit
    def test_init_async_api_client_emits_deprecation_warning(self, monkeypatch):
        """init_async_api_client should warn that explicit async clients are preferred."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        fake_async_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_async_client)
        monkeypatch.setitem(module.__dict__, "AsyncBritecoreAPIClient", fake_ctor)

        with pytest.warns(DeprecationWarning, match=r"init_async_api_client\(\)"):
            module.init_async_api_client("test-site")

    @pytest.mark.unit
    def test_init_async_api_client_forwards_client_dry_run(self, monkeypatch):
        """init_async_api_client(client_dry_run=True) forwards async dry-run defaults."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        fake_async_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_async_client)
        monkeypatch.setitem(module.__dict__, "AsyncBritecoreAPIClient", fake_ctor)

        with pytest.warns(DeprecationWarning, match=r"init_async_api_client\(\)"):
            module.init_async_api_client("test-site", client_dry_run=True)

        fake_ctor.assert_called_once_with("test-site", client_dry_run=True)

    @pytest.mark.unit
    def test_init_api_client_requires_explicit_target_site(self, monkeypatch):
        """init_api_client rejects empty target_site values."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        with pytest.warns(DeprecationWarning, match=r"init_api_client\(\)"):
            with pytest.raises(module.BritecoreError.ConfigurationError):
                module.init_api_client(None)

    @pytest.mark.unit
    def test_init_async_api_client_requires_explicit_target_site(self, monkeypatch):
        """init_async_api_client rejects empty target_site values."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        with pytest.warns(DeprecationWarning, match=r"init_async_api_client\(\)"):
            with pytest.raises(module.BritecoreError.ConfigurationError):
                module.init_async_api_client(None)

    @pytest.mark.unit
    def test_getters_raise_when_clients_uninitialized(self):
        """Lazy getters raise config errors until init helpers seed client state."""
        module = importlib.reload(api_calls_module)

        with pytest.raises(module.BritecoreError.ConfigurationError):
            module.get_api_client()

        with pytest.raises(module.BritecoreError.ConfigurationError):
            module.get_async_api_client()

    @pytest.mark.unit
    def test_reset_api_client_emits_deprecation_warning(self):
        """reset_api_client should warn before clearing legacy module-level client state."""
        module = importlib.reload(api_calls_module)
        module._api_client = MagicMock()
        module._async_api_client = MagicMock()

        with pytest.warns(DeprecationWarning, match=r"reset_api_client\(\)"):
            module.reset_api_client()

        assert module._api_client is None
        assert module._async_api_client is None

    @pytest.mark.unit
    def test_use_api_client_overrides_global_within_context(self):
        """use_api_client should route proxy calls to the bound client in-context."""
        module = importlib.reload(api_calls_module)

        global_client = MagicMock()
        global_client.token = "global"
        context_client = MagicMock()
        context_client.token = "context"

        module._api_client = global_client

        assert module.api_client.token == "global"
        with module.use_api_client(context_client):
            assert module.api_client.token == "context"
            assert module.get_api_client() is context_client
        assert module.api_client.token == "global"
        assert module.get_api_client() is global_client

    @pytest.mark.unit
    def test_use_api_client_supports_nested_contexts(self):
        """Nested use_api_client contexts should restore prior override on exit."""
        module = importlib.reload(api_calls_module)

        outer = MagicMock()
        outer.token = "outer"
        inner = MagicMock()
        inner.token = "inner"

        with module.use_api_client(outer):
            assert module.api_client.token == "outer"
            with module.use_api_client(inner):
                assert module.api_client.token == "inner"
            assert module.api_client.token == "outer"

    @pytest.mark.unit
    def test_resolve_client_emits_warning_when_falling_back_to_global(self):
        """resolve_client should warn when wrappers rely on module-level sync fallback."""
        module = importlib.reload(api_calls_module)
        global_client = MagicMock()
        module._api_client = global_client

        with pytest.warns(
            DeprecationWarning,
            match="Implicit wrapper client fallback",
        ):
            resolved = module.resolve_client()

        assert resolved is global_client

    @pytest.mark.unit
    def test_resolve_client_does_not_warn_for_explicit_client(self):
        """resolve_client should not warn when the caller passes client= explicitly."""
        module = importlib.reload(api_calls_module)
        explicit_client = MagicMock()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            resolved = module.resolve_client(explicit_client)

        assert resolved is explicit_client
        assert caught == []

    @pytest.mark.unit
    def test_resolve_client_does_not_warn_inside_scoped_context(self):
        """resolve_client should not warn when use_api_client provides scoped sync state."""
        module = importlib.reload(api_calls_module)
        scoped_client = MagicMock()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with module.use_api_client(scoped_client):
                resolved = module.resolve_client()

        assert resolved is scoped_client
        assert caught == []

    @pytest.mark.unit
    def test_aresolve_client_emits_warning_when_falling_back_to_global(self):
        """aresolve_client should warn when wrappers rely on module-level async fallback."""
        module = importlib.reload(api_calls_module)
        global_async_client = MagicMock()
        module._async_api_client = global_async_client

        with pytest.warns(
            DeprecationWarning,
            match="Implicit async wrapper client fallback",
        ):
            resolved = module.aresolve_client()

        assert resolved is global_async_client

    @pytest.mark.unit
    def test_aresolve_client_does_not_warn_for_explicit_client(self):
        """aresolve_client should not warn when the caller passes client= explicitly."""
        module = importlib.reload(api_calls_module)
        explicit_async_client = MagicMock()

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            resolved = module.aresolve_client(explicit_async_client)

        assert resolved is explicit_async_client
        assert caught == []
