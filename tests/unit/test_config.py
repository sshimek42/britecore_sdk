"""Unit tests for configuration module."""

import importlib
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from britecore_sdk.settings.typed import build_typed_settings


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
            LoadClientSettings(None)  # type: ignore[arg-type]

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

    @pytest.mark.unit
    def test_load_config_logs_hybrid_warning_when_env_keys_missing(self):
        """load_config should warn when required credentials come from files, not env vars."""
        from britecore_sdk.settings.config import LoadClientSettings

        with (
            patch("britecore_sdk.settings.config.settings") as mock_cfg,
            patch("britecore_sdk.settings.config.LOGGER.warning") as mock_warning,
            patch("britecore_sdk.settings.config.os.environ.get", return_value=None),
        ):
            mock_cfg.using_env.return_value.__enter__ = MagicMock(return_value=mock_cfg)
            mock_cfg.using_env.return_value.__exit__ = MagicMock(return_value=False)

            def _get(key, default=None):
                values = {
                    "base_url": "https://api.example.com",
                    "client_id": "cid",
                    "client_secret": "secret",
                    "api_key": "key",
                }
                return values.get(key, default)

            mock_cfg.get.side_effect = _get

            loader = LoadClientSettings("test_site")
            loader.load_config()

            assert mock_warning.call_count == 1

    @pytest.mark.unit
    def test_load_config_wraps_unexpected_errors(self):
        """load_config should wrap unexpected exceptions in ConfigurationError."""
        from britecore_sdk.exceptions import BritecoreError
        from britecore_sdk.settings.config import LoadClientSettings

        with patch("britecore_sdk.settings.config.settings") as mock_cfg:
            mock_cfg.using_env.side_effect = RuntimeError("bad cfg")
            loader = LoadClientSettings("test_site")

            with pytest.raises(BritecoreError.ConfigurationError):
                loader.load_config()

    @pytest.mark.unit
    def test_load_config_returns_settings_when_target_site_missing(self):
        """Defensive fallback returns global settings when target_site is unset."""
        from britecore_sdk.settings import config as config_module

        loader = config_module.LoadClientSettings.__new__(
            config_module.LoadClientSettings
        )
        loader.target_site = None
        loader._warned_hybrid_config = False

        assert loader.load_config() is config_module.settings


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

        module.init_api_client(target_site="explicit_site")

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

    @pytest.mark.unit
    def test_get_typed_settings_exported(self):
        """get_typed_settings is exported from the settings package."""
        from britecore_sdk.settings import get_typed_settings

        assert callable(get_typed_settings)

    @pytest.mark.unit
    def test_get_typed_settings_delegates_builder(self):
        """get_typed_settings should call the typed builder with active settings."""
        from britecore_sdk.settings.config import get_typed_settings

        expected = {"ok": True}
        with patch(
            "britecore_sdk.settings.typed.build_typed_settings", return_value=expected
        ) as mock_build:
            result = get_typed_settings(site_names=["prod"])

        assert result == expected
        assert mock_build.call_count == 1

    @pytest.mark.unit
    def test_non_default_env_triggers_validator_check_on_reload(self, monkeypatch):
        """Reloading config with a non-default dynaconf env should call validate()."""
        import britecore_sdk.settings.config as config_module

        fake_settings = MagicMock()
        fake_settings.validators = MagicMock()
        fake_settings.get.return_value = None

        monkeypatch.setenv("ENV_FOR_DYNACONF", "staging")
        with patch("dynaconf.Dynaconf", return_value=fake_settings):
            importlib.reload(config_module)

        assert fake_settings.validators.validate.call_count == 1

        monkeypatch.setenv("ENV_FOR_DYNACONF", "default")
        importlib.reload(config_module)


class TestDefaultsHelpers:
    """Coverage tests for configuration defaults helper functions."""

    @pytest.mark.unit
    def test_get_default_returns_known_value(self):
        from britecore_sdk.settings.defaults import get_default

        assert get_default("write_policy") == "allow"

    @pytest.mark.unit
    def test_get_default_returns_fallback_for_unknown_key(self):
        from britecore_sdk.settings.defaults import get_default

        assert get_default("not_a_real_setting", default="fallback") == "fallback"

    def test_build_typed_settings_builds_site_and_sdk_models(self):
        """Typed settings models should include site values and active SDK defaults."""
        mock_settings = MagicMock()
        mock_settings.using_env.return_value = nullcontext()
        mock_settings.get.side_effect = lambda key, default=None: {
            "target_site": "prod",
            "base_url": "https://api.example.com",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "api_key": "api-key",
            "web_retry": 4,
            "web_timeout": 15,
            "web_timeout_long": 45,
        }.get(key, default)

        result = build_typed_settings(mock_settings, site_names=["prod"])

        assert result.target_site == "prod"
        assert result.default_web_retry == 4
        assert result.sites["prod"].base_url == "https://api.example.com"
        assert result.sites["prod"].client_id == "client-id"
        assert result.sites["prod"].api_key == "api-key"


# ---------------------------------------------------------------------------
# New: layered settings file discovery
# ---------------------------------------------------------------------------
class TestDiscoverSettingsFiles:
    """Tests for _discover_settings_files()."""

    @pytest.mark.unit
    def test_always_includes_sdk_defaults(self):
        """SDK package settings files are discovered when they exist.

        Note: these files are in .gitignore and may not exist in CI.
        This test verifies they are captured by the discovery mechanism
        when present in the local development environment.
        """
        from britecore_sdk.settings.config import _discover_settings_files

        files = _discover_settings_files()
        # Verify discovery succeeds (even if it returns empty list in CI)
        assert isinstance(files, list)

        # Check if SDK defaults exist in the source (development environment)
        sdk_dir = (
            Path(__file__).parent.parent.parent / "src" / "britecore_sdk" / "settings"
        )
        settings_toml_exists = (sdk_dir / "settings.toml").exists()
        secrets_toml_exists = (sdk_dir / ".secrets.toml").exists()

        # If they exist, they should be in discovered files
        if settings_toml_exists or secrets_toml_exists:
            sdk_files = [p for p in files if p.parent.name == "settings"]
            assert len(sdk_files) > 0, "SDK defaults should be discovered if they exist"

    @pytest.mark.unit
    def test_includes_user_level_files_when_present(self, tmp_path, monkeypatch):
        """User-level ~/.britecore/ files are included when they exist."""
        from britecore_sdk.settings.config import _discover_settings_files

        fake_home = tmp_path / "home"
        britecore_dir = fake_home / ".britecore"
        britecore_dir.mkdir(parents=True)
        (britecore_dir / "settings.toml").write_text("[default]\n")
        (britecore_dir / ".secrets.toml").write_text("[default]\n")

        monkeypatch.setattr(Path, "home", lambda: fake_home)

        files = _discover_settings_files()
        file_paths = [str(p) for p in files]
        assert any(".britecore" in fp and "settings.toml" in fp for fp in file_paths)
        assert any(".britecore" in fp and ".secrets.toml" in fp for fp in file_paths)

    @pytest.mark.unit
    def test_includes_project_local_files_when_present(self, tmp_path, monkeypatch):
        """CWD britecore.toml / .britecore_secrets.toml are included when they exist."""
        from britecore_sdk.settings.config import _discover_settings_files

        (tmp_path / "britecore.toml").write_text("[default]\n")
        (tmp_path / ".britecore_secrets.toml").write_text("[default]\n")
        monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

        files = _discover_settings_files()
        file_paths = [str(p) for p in files]
        assert any("britecore.toml" in fp for fp in file_paths)
        assert any(".britecore_secrets.toml" in fp for fp in file_paths)

    @pytest.mark.unit
    def test_env_var_file_included_when_exists(self, tmp_path, monkeypatch):
        """BRITECORE_SDK_SETTINGS_FILE is appended when the path exists."""
        from britecore_sdk.settings.config import _discover_settings_files

        custom_cfg = tmp_path / "my_settings.toml"
        custom_cfg.write_text("[default]\n")
        monkeypatch.setenv("BRITECORE_SDK_SETTINGS_FILE", str(custom_cfg))

        files = _discover_settings_files()
        assert custom_cfg in files

    @pytest.mark.unit
    def test_env_var_missing_file_excluded(self, tmp_path, monkeypatch):
        """BRITECORE_SDK_SETTINGS_FILE pointing to non-existent file is excluded."""
        from britecore_sdk.settings.config import _discover_settings_files

        missing = tmp_path / "does_not_exist.toml"
        monkeypatch.setenv("BRITECORE_SDK_SETTINGS_FILE", str(missing))

        files = _discover_settings_files()
        assert missing not in files

    @pytest.mark.unit
    def test_env_var_not_set_excluded(self, monkeypatch):
        """BRITECORE_SDK_SETTINGS_FILE env var is not included when unset.

        Verifies that discovery returns a valid list and doesn't attempt to
        add a file when the env var is not set. SDK defaults may or may not
        exist depending on environment (they are in .gitignore).
        """
        from britecore_sdk.settings.config import _discover_settings_files

        monkeypatch.delenv("BRITECORE_SDK_SETTINGS_FILE", raising=False)
        files = _discover_settings_files()

        # Verify the result is a valid list of Path objects
        assert isinstance(files, list)
        for f in files:
            assert isinstance(f, Path)

    @pytest.mark.unit
    def test_sdk_defaults_appear_before_project_local(self, tmp_path, monkeypatch):
        """SDK defaults appear before project-local files (lower priority)."""
        from britecore_sdk.settings.config import _discover_settings_files

        (tmp_path / "britecore.toml").write_text("[default]\n")
        monkeypatch.setattr(Path, "cwd", lambda: tmp_path)
        monkeypatch.delenv("BRITECORE_SDK_SETTINGS_FILE", raising=False)

        files = _discover_settings_files()
        sdk_dir = (
            Path(__file__).parent.parent.parent / "src" / "britecore_sdk" / "settings"
        )
        sdk_indices = [
            i for i, p in enumerate(files) if p.parent.resolve() == sdk_dir.resolve()
        ]
        project_indices = [i for i, p in enumerate(files) if p.name == "britecore.toml"]
        if sdk_indices and project_indices:
            assert max(sdk_indices) < min(project_indices)


# ---------------------------------------------------------------------------
# New: explicit kwargs on init_client / init_api_client
# ---------------------------------------------------------------------------
class TestExplicitCredentials:
    """Tests for explicit base_url/api_key/client_id/client_secret kwargs."""

    @pytest.mark.unit
    def test_init_client_explicit_api_key_skips_load_client_settings(self):
        """When base_url is given, LoadClientSettings is never called."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with (
            patch(
                "britecore_sdk.api.britecore_api_client.LoadClientSettings"
            ) as mock_loader,
            patch("britecore_sdk.api.britecore_api_client.urllib3.PoolManager"),
        ):
            client = BritecoreAPIClient("mysite")
            client.init_client(
                base_url="https://api.example.com",
                api_key="test-key",
            )
            mock_loader.assert_not_called()
            assert client.base_url is not None
            assert client.use_api_key is True

    @pytest.mark.unit
    def test_init_client_explicit_oauth_selects_oauth_mode(self):
        """Explicit client_id + client_secret triggers OAuth auth mode."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with (
            patch("britecore_sdk.api.britecore_api_client.LoadClientSettings"),
            patch("britecore_sdk.api.britecore_api_client.urllib3.PoolManager"),
            patch("britecore_sdk.api.britecore_api_client.OAuthToken") as mock_oauth,
        ):
            client = BritecoreAPIClient("mysite")
            client.init_client(
                base_url="https://api.example.com",
                client_id="cid",
                client_secret="csecret",
            )
            assert client.use_api_key is False
            mock_oauth.assert_called_once()

    @pytest.mark.unit
    def test_init_api_client_explicit_base_url_no_target_site(self, monkeypatch):
        """init_api_client with base_url and no target_site uses 'explicit' as label."""
        import importlib

        import britecore_sdk.api.api_calls as api_calls_module

        module = importlib.reload(api_calls_module)

        fake_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_client)
        monkeypatch.setattr(module, "BritecoreAPIClient", fake_ctor)

        result = module.init_api_client(base_url="https://api.example.com", api_key="k")

        fake_ctor.assert_called_once_with("explicit")
        fake_client.init_client.assert_called_once_with(
            client_dry_run=False,
            base_url="https://api.example.com",
            api_key="k",
            client_id=None,
            client_secret=None,
            enable_rate_limiter=None,
        )
        assert result is fake_client

    @pytest.mark.unit
    def test_init_api_client_explicit_with_named_site(self, monkeypatch):
        """init_api_client with base_url and explicit target_site keeps site name."""
        import importlib

        import britecore_sdk.api.api_calls as api_calls_module

        module = importlib.reload(api_calls_module)

        fake_client = MagicMock()
        fake_ctor = MagicMock(return_value=fake_client)
        monkeypatch.setattr(module, "BritecoreAPIClient", fake_ctor)

        module.init_api_client(
            "production",
            base_url="https://prod.example.com",
            api_key="prod-key",
        )

        fake_ctor.assert_called_once_with("production")

    @pytest.mark.unit
    def test_init_api_client_no_base_url_still_requires_target_site(self, monkeypatch):
        """Without base_url, missing target_site still raises ConfigurationError."""
        import importlib

        import britecore_sdk.api.api_calls as api_calls_module

        module = importlib.reload(api_calls_module)
        monkeypatch.setattr(module, "get_target_site", lambda: None)

        with pytest.raises(module.BritecoreError.ConfigurationError):
            module.init_api_client()
