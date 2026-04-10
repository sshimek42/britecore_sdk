"""Regression tests for api_calls client state and lazy proxy behavior."""

import importlib
from unittest.mock import MagicMock

import pytest

import britecore_libraries.api.api_calls as api_calls_module


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
        monkeypatch.setattr(module, "BritecoreAPIClient", fake_ctor)

        returned = module.init_api_client("test-site")

        assert returned is fake_client
        assert module._api_client is fake_client
        fake_ctor.assert_called_once_with("test-site")
        fake_client.init_client.assert_called_once_with()

        # Access through lazy proxy must reuse seeded global client.
        assert module.api_client.token == "ready"
        fake_ctor.assert_called_once()

    @pytest.mark.unit
    def test_init_async_api_client_sets_global_for_lazy_proxy(self, monkeypatch):
        """init_async_api_client(target_site) stores state used by async proxy."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        fake_async_client = MagicMock()
        fake_async_client.token = "async-ready"
        fake_ctor = MagicMock(return_value=fake_async_client)
        monkeypatch.setattr(module, "AsyncBritecoreAPIClient", fake_ctor)

        returned = module.init_async_api_client("test-site")

        assert returned is fake_async_client
        assert module._async_api_client is fake_async_client
        fake_ctor.assert_called_once_with("test-site")

        # Access through lazy proxy must reuse seeded global async client.
        assert module.async_api_client.token == "async-ready"
        fake_ctor.assert_called_once()

    @pytest.mark.unit
    def test_init_api_client_requires_explicit_target_site(self, monkeypatch):
        """init_api_client rejects empty target_site values."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

        with pytest.raises(module.BritecoreError.ConfigurationError):
            module.init_api_client(None)

    @pytest.mark.unit
    def test_init_async_api_client_requires_explicit_target_site(self, monkeypatch):
        """init_async_api_client rejects empty target_site values."""
        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)

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
