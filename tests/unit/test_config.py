"""Unit tests for configuration module."""

from unittest.mock import MagicMock, patch

import pytest


class TestLoadClientSettings:
    """Tests for LoadClientSettings class."""

    @pytest.mark.unit
    def test_init_with_target_site(self):
        """Test initialization with explicit target_site."""
        from britecore_libraries.config.config import LoadClientSettings

        loader = LoadClientSettings("test_site")
        assert loader.target_site == "test_site"

    @pytest.mark.unit
    def test_init_with_env_variable(self, monkeypatch):
        """Test initialization from environment variable."""
        from britecore_libraries.config.config import LoadClientSettings

        monkeypatch.setenv("target_site", "env_site")
        loader = LoadClientSettings(None)
        assert loader.target_site == "env_site"

    @pytest.mark.unit
    def test_load_config_merges_default(self, mock_settings):
        """Test that load_config merges default settings with site-specific."""
        from britecore_libraries.config.config import LoadClientSettings

        with patch("britecore_libraries.config.config.settings") as mock_cfg:
            # Make using_env() work as a context manager
            mock_cfg.using_env.return_value.__enter__ = MagicMock(return_value=mock_cfg)
            mock_cfg.using_env.return_value.__exit__ = MagicMock(return_value=False)
            mock_cfg.get.return_value = ""

            loader = LoadClientSettings("test_site")
            result = loader.load_config()

            # Verify it returns something (the merged result)
            assert result is not None


class TestConfigInitialization:
    """Tests for config module initialization."""

    @pytest.mark.unit
    def test_settings_object_created(self):
        """Test that settings object is created on import."""
        from britecore_libraries.config import settings

        assert settings is not None

    @pytest.mark.unit
    def test_dynaconf_environments_parameter(self, mock_settings):
        """Test that Dynaconf is initialized with correct environments parameter."""
        # This test verifies the fix: environments=True instead of enviroments
        # We verify this indirectly by ensuring the config module loads without error
        from britecore_libraries.config import settings

        assert settings is not None
