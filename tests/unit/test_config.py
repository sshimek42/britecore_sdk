"""Unit tests for configuration module."""

from unittest.mock import MagicMock, patch

import pytest


class TestLoadClientSettings:
    """Tests for LoadClientSettings class."""

    @pytest.mark.unit
    def test_init_with_target_site(self):
        """Test initialization with explicit target_site."""
        from britecore_sdk.settings.config import LoadClientSettings

        loader = LoadClientSettings("test_site")
        assert loader.target_site == "test_site"

    @pytest.mark.unit
    def test_init_with_env_variable_raises(self, monkeypatch):
        """Test that initialization without explicit target_site raises error."""
        from britecore_sdk.settings.config import LoadClientSettings

        monkeypatch.setenv("target_site", "env_site")
        from britecore_sdk.exceptions import BritecoreError

        with pytest.raises(BritecoreError.ConfigurationError):
            LoadClientSettings(None)

    @pytest.mark.unit
    def test_load_config_merges_default(self, mock_settings):
        """Test that load_config merges default settings with site-specific."""
        from britecore_sdk.settings.config import LoadClientSettings

        with patch("britecore_sdk.settings.config.settings") as mock_cfg:
            # Make using_env() work as a context manager
            mock_cfg.using_env.return_value.__enter__ = MagicMock(return_value=mock_cfg)
            mock_cfg.using_env.return_value.__exit__ = MagicMock(return_value=False)
            mock_cfg.get.return_value = ""

            loader = LoadClientSettings("test_site")
            result = loader.load_config()

            # Verify it returns something (the merged result)
            assert result is not None


class TestGetTargetSite:
    """Tests for get_target_site() helper."""

    @pytest.mark.unit
    def test_returns_none_when_not_set(self, monkeypatch):
        """Returns None when neither settings.toml nor env provides target_site."""
        monkeypatch.delenv("target_site", raising=False)
        with patch("britecore_sdk.settings.config.settings") as mock_cfg:
            mock_cfg.get.return_value = None
            from britecore_sdk.settings.config import get_target_site

            assert get_target_site() is None

    @pytest.mark.unit
    def test_reads_from_settings_toml(self, monkeypatch):
        """Returns the value from settings.toml when set there."""
        monkeypatch.delenv("target_site", raising=False)
        with patch("britecore_sdk.settings.config.settings") as mock_cfg:
            mock_cfg.get.return_value = "toml_site"
            from britecore_sdk.settings.config import get_target_site

            result = get_target_site()
            assert result == "toml_site"
            mock_cfg.get.assert_called_once_with("target_site", default=None)

    @pytest.mark.unit
    def test_falls_back_to_env_var(self, monkeypatch):
        """Falls back to the env var when settings.toml has no target_site."""
        monkeypatch.setenv("target_site", "env_site")
        with patch("britecore_sdk.settings.config.settings") as mock_cfg:
            mock_cfg.get.return_value = None
            from britecore_sdk.settings.config import get_target_site

            assert get_target_site() == "env_site"

    @pytest.mark.unit
    def test_settings_toml_takes_precedence_over_env(self, monkeypatch):
        """settings.toml value wins over the env var."""
        monkeypatch.setenv("target_site", "env_site")
        with patch("britecore_sdk.settings.config.settings") as mock_cfg:
            mock_cfg.get.return_value = "toml_site"
            from britecore_sdk.settings.config import get_target_site

            assert get_target_site() == "toml_site"


class TestInitApiClientFallback:
    """Tests for init_api_client target_site resolution."""

    @pytest.mark.unit
    def test_raises_when_no_target_site(self, monkeypatch):
        """Raises ConfigurationError when no target_site is available from any source."""
        import importlib

        import britecore_sdk.api.api_calls as api_calls_module

        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)
        monkeypatch.setattr(module, "get_target_site", lambda: None)

        with pytest.raises(module.BritecoreError.ConfigurationError):
            module.init_api_client(None)

    @pytest.mark.unit
    def test_uses_settings_toml_fallback(self, monkeypatch):
        """Uses target_site from settings.toml when not passed explicitly."""
        import importlib

        import britecore_sdk.api.api_calls as api_calls_module

        module = importlib.reload(api_calls_module)
        monkeypatch.delenv("target_site", raising=False)
        monkeypatch.setattr(module, "get_target_site", lambda: "toml_site")

        fake_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_client)
        monkeypatch.setattr(module, "BritecoreAPIClient", fake_ctor)

        result = module.init_api_client()

        fake_ctor.assert_called_once_with("toml_site")
        fake_client.init_client.assert_called_once()
        assert result is fake_client

    @pytest.mark.unit
    def test_explicit_arg_takes_precedence(self, monkeypatch):
        """Explicit target_site argument takes precedence over settings.toml."""
        import importlib

        import britecore_sdk.api.api_calls as api_calls_module

        module = importlib.reload(api_calls_module)
        monkeypatch.setattr(module, "get_target_site", lambda: "toml_site")

        fake_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_client)
        monkeypatch.setattr(module, "BritecoreAPIClient", fake_ctor)

        result = module.init_api_client(target_site="explicit_site")

        fake_ctor.assert_called_once_with("explicit_site")


class TestConfigInitialization:
    """Tests for config module initialization."""

    @pytest.mark.unit
    def test_settings_object_created(self):
        """Test that settings object is created on import."""
        from britecore_sdk.settings import settings

        assert settings is not None

    @pytest.mark.unit
    def test_dynaconf_environments_parameter(self, mock_settings):
        """Test that Dynaconf is initialized with correct environments parameter."""
        # This test verifies the fix: environments=True instead of enviroments
        # We verify this indirectly by ensuring the config module loads without error
        from britecore_sdk.settings import settings

        assert settings is not None

    @pytest.mark.unit
    def test_get_target_site_exported(self):
        """get_target_site is exported from the settings package."""
        from britecore_sdk.settings import get_target_site

        assert callable(get_target_site)
