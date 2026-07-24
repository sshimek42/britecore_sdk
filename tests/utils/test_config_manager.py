"""
Focused tests for ConfigManager using real temp-file fixtures.

Top 4 code paths covered first:
  1. add_site  – OAuth success (writes file, site readable back)
  2. add_site  – API-key success (writes file, site readable back)
  3. delete_site – success (site removed from file)
  4. update_site – success (field persisted to file)

Additional paths for each method follow those four.
"""

import pytest

from britecore_sdk.utils.config_manager import ConfigManager
from britecore_sdk.utils.toml_compat import toml

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def empty_secrets(tmp_path):
    """Empty .secrets.toml file."""
    f = tmp_path / ".secrets.toml"
    f.write_text("")
    return str(f)


@pytest.fixture()
def empty_settings(tmp_path):
    """Empty settings.toml file."""
    f = tmp_path / "settings.toml"
    f.write_text("")
    return str(f)


@pytest.fixture()
def manager(empty_secrets, empty_settings):
    """ConfigManager pointed at isolated temp files."""
    return ConfigManager(config_path=empty_secrets, settings_path=empty_settings)


@pytest.fixture()
def secrets_with_oauth_site(tmp_path):
    """Secrets file that already contains one OAuth site."""
    data = {
        "prod": {
            "base_url": "https://prod.example.com",
            "client_id": "cid123",
            "client_secret": "csec456",
        }
    }
    f = tmp_path / ".secrets.toml"
    with open(f, "w") as fh:
        toml.dump(data, fh)
    return str(f)


@pytest.fixture()
def manager_with_oauth_site(secrets_with_oauth_site, empty_settings):
    """ConfigManager pre-loaded with one OAuth site."""
    return ConfigManager(
        config_path=secrets_with_oauth_site, settings_path=empty_settings
    )


@pytest.fixture()
def settings_with_section(tmp_path):
    """settings.toml file pre-populated with a [default] section."""
    data = {"default": {"web_timeout": 5, "target_site": "prod"}}
    f = tmp_path / "settings.toml"
    with open(f, "w") as fh:
        toml.dump(data, fh)
    return str(f)


@pytest.fixture()
def manager_with_settings(empty_secrets, settings_with_section):
    """ConfigManager pointing at a settings file that has a [default] section."""
    return ConfigManager(config_path=empty_secrets, settings_path=settings_with_section)


# ===========================================================================
# TOP 4 PATHS
# ===========================================================================


class TestAddSiteOAuth:
    """Path 1 – add_site with OAuth credentials."""

    def test_returns_success_tuple(self, manager):
        ok, msg = manager.add_site(
            "staging",
            "https://staging.example.com",
            "oauth",
            client_id="cid",
            client_secret="csec",
        )
        assert ok is True
        assert "staging" in msg

    def test_site_readable_back_via_get_site(self, manager):
        manager.add_site(
            "staging",
            "https://staging.example.com",
            "oauth",
            client_id="cid",
            client_secret="csec",
        )
        site = manager.get_site("staging")
        assert site is not None
        assert site["base_url"] == "https://staging.example.com"
        assert site["client_id"] == "cid"
        assert site["client_secret"] == "csec"

    def test_site_persisted_to_disk(self, manager):
        manager.add_site(
            "staging",
            "https://staging.example.com",
            "oauth",
            client_id="cid",
            client_secret="csec",
        )
        on_disk = toml.load(manager.config_path)
        assert "staging" in on_disk
        assert on_disk["staging"]["client_id"] == "cid"

    def test_missing_client_id_returns_error(self, manager):
        ok, msg = manager.add_site(
            "staging",
            "https://staging.example.com",
            "oauth",
            client_secret="csec",
        )
        assert ok is False
        assert "client_id" in msg or "OAuth" in msg

    def test_missing_client_secret_returns_error(self, manager):
        ok, msg = manager.add_site(
            "staging",
            "https://staging.example.com",
            "oauth",
            client_id="cid",
        )
        assert ok is False

    def test_duplicate_site_name_returns_error(self, manager):
        manager.add_site(
            "staging",
            "https://staging.example.com",
            "oauth",
            client_id="cid",
            client_secret="csec",
        )
        ok, msg = manager.add_site(
            "staging",
            "https://other.example.com",
            "oauth",
            client_id="cid2",
            client_secret="csec2",
        )
        assert ok is False
        assert "already exists" in msg


class TestAddSiteApiKey:
    """Path 2 – add_site with API-key credentials."""

    def test_returns_success_tuple(self, manager):
        ok, msg = manager.add_site(
            "dev",
            "https://dev.example.com",
            "api_key",
            api_key="my-api-key",
        )
        assert ok is True
        assert "dev" in msg

    def test_site_readable_back_via_get_site(self, manager):
        manager.add_site(
            "dev",
            "https://dev.example.com",
            "api_key",
            api_key="my-api-key",
        )
        site = manager.get_site("dev")
        assert site is not None
        assert site["api_key"] == "my-api-key"

    def test_site_persisted_to_disk(self, manager):
        manager.add_site(
            "dev",
            "https://dev.example.com",
            "api_key",
            api_key="my-api-key",
        )
        on_disk = toml.load(manager.config_path)
        assert on_disk["dev"]["api_key"] == "my-api-key"

    def test_missing_api_key_returns_error(self, manager):
        ok, msg = manager.add_site("dev", "https://dev.example.com", "api_key")
        assert ok is False
        assert "api_key" in msg or "API Key" in msg

    def test_unknown_auth_type_returns_error(self, manager):
        ok, msg = manager.add_site(
            "dev",
            "https://dev.example.com",
            "magic_token",  # type: ignore[arg-type]
        )
        assert ok is False
        assert "Unknown auth_type" in msg


class TestDeleteSite:
    """Path 3 – delete_site."""

    def test_returns_success_tuple(self, manager_with_oauth_site):
        ok, msg = manager_with_oauth_site.delete_site("prod")
        assert ok is True
        assert "prod" in msg

    def test_site_gone_from_in_memory_config(self, manager_with_oauth_site):
        manager_with_oauth_site.delete_site("prod")
        assert manager_with_oauth_site.get_site("prod") is None

    def test_site_gone_from_disk(self, manager_with_oauth_site):
        manager_with_oauth_site.delete_site("prod")
        on_disk = toml.load(manager_with_oauth_site.config_path)
        assert "prod" not in on_disk

    def test_nonexistent_site_returns_error(self, manager):
        ok, msg = manager.delete_site("ghost")
        assert ok is False
        assert "ghost" in msg


class TestUpdateSite:
    """Path 4 – update_site."""

    def test_returns_success_tuple(self, manager_with_oauth_site):
        ok, msg = manager_with_oauth_site.update_site(
            "prod", base_url="https://new.example.com"
        )
        assert ok is True
        assert "prod" in msg

    def test_updated_field_visible_via_get_site(self, manager_with_oauth_site):
        manager_with_oauth_site.update_site("prod", base_url="https://new.example.com")
        site = manager_with_oauth_site.get_site("prod")
        assert site is not None
        assert site["base_url"] == "https://new.example.com"

    def test_updated_field_persisted_to_disk(self, manager_with_oauth_site):
        manager_with_oauth_site.update_site("prod", client_id="new-cid")
        on_disk = toml.load(manager_with_oauth_site.config_path)
        assert on_disk["prod"]["client_id"] == "new-cid"

    def test_unmodified_fields_preserved(self, manager_with_oauth_site):
        manager_with_oauth_site.update_site("prod", base_url="https://new.example.com")
        site = manager_with_oauth_site.get_site("prod")
        assert site is not None
        assert site["client_id"] == "cid123"
        assert site["client_secret"] == "csec456"

    def test_nonexistent_site_returns_error(self, manager):
        ok, msg = manager.update_site("ghost", base_url="https://x.example.com")
        assert ok is False
        assert "ghost" in msg


# ===========================================================================
# ADDITIONAL METHOD COVERAGE
# ===========================================================================


class TestListSites:
    def test_empty_config_returns_empty_list(self, manager):
        assert manager.list_sites() == []

    def test_returns_one_entry_per_site(self, manager_with_oauth_site):
        sites = manager_with_oauth_site.list_sites()
        assert len(sites) == 1
        assert sites[0]["name"] == "prod"

    def test_status_ok_for_complete_oauth_site(self, manager_with_oauth_site):
        sites = manager_with_oauth_site.list_sites()
        assert sites[0]["status"] == "OK"

    def test_status_incomplete_for_missing_auth(self, empty_settings, tmp_path):
        data = {"half": {"base_url": "https://half.example.com"}}
        f = tmp_path / ".secrets.toml"
        with open(f, "w") as fh:
            toml.dump(data, fh)
        m = ConfigManager(config_path=str(f), settings_path=empty_settings)
        sites = m.list_sites()
        assert sites[0]["status"] == "INCOMPLETE"

    def test_secrets_masked_by_default(self, manager_with_oauth_site):
        sites = manager_with_oauth_site.list_sites(mask_secrets=True)
        assert sites[0]["client_secret"] != "csec456"
        assert "****" in sites[0]["client_secret"]

    def test_mask_false_not_in_output_keys(self, manager_with_oauth_site):
        # mask_secrets=False omits the masked credential keys from the result
        sites = manager_with_oauth_site.list_sites(mask_secrets=False)
        assert "client_secret" not in sites[0]


class TestGetSite:
    def test_existing_site_returns_dict(self, manager_with_oauth_site):
        site = manager_with_oauth_site.get_site("prod")
        assert isinstance(site, dict)

    def test_missing_site_returns_none(self, manager):
        assert manager.get_site("no-such-site") is None


class TestReload:
    def test_reload_picks_up_external_change(self, manager):
        """After an external write to the file, reload() refreshes in-memory state."""
        new_data = {
            "external": {
                "base_url": "https://external.example.com",
                "api_key": "ext-key",
            }
        }
        with open(manager.config_path, "w") as fh:
            toml.dump(new_data, fh)

        assert manager.get_site("external") is None  # stale
        manager.reload()
        assert manager.get_site("external") is not None


class TestExportBackup:
    def test_export_creates_file(self, manager_with_oauth_site, tmp_path):
        backup = str(tmp_path / "backup.toml")
        ok, msg = manager_with_oauth_site.export_backup(backup)
        assert ok is True
        assert "backup.toml" in msg
        assert (tmp_path / "backup.toml").exists()

    def test_exported_file_matches_current_config(
        self, manager_with_oauth_site, tmp_path
    ):
        backup = str(tmp_path / "backup.toml")
        manager_with_oauth_site.export_backup(backup)
        on_disk = toml.load(backup)
        assert "prod" in on_disk


class TestOsErrorRevertPaths:
    """Every mutating method must revert in-memory state on OSError."""

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _raise_os(*a, **kw):
        raise OSError("disk full")

    # ── secrets mutations ─────────────────────────────────────────────────

    def test_add_site_reverts_on_save_failure(self, manager, monkeypatch):
        monkeypatch.setattr(
            "britecore_sdk.utils.config_manager.save_secrets", self._raise_os
        )
        ok, msg = manager.add_site(
            "site1", "https://site1.example.com", "api_key", api_key="key1"
        )
        assert ok is False
        assert "Failed to save" in msg
        assert manager.get_site("site1") is None

    def test_delete_site_reverts_on_save_failure(
        self, manager_with_oauth_site, monkeypatch
    ):
        monkeypatch.setattr(
            "britecore_sdk.utils.config_manager.save_secrets", self._raise_os
        )
        ok, msg = manager_with_oauth_site.delete_site("prod")
        assert ok is False
        assert "Failed to save" in msg
        assert manager_with_oauth_site.get_site("prod") is not None

    def test_update_site_reverts_on_save_failure(
        self, manager_with_oauth_site, monkeypatch
    ):
        monkeypatch.setattr(
            "britecore_sdk.utils.config_manager.save_secrets", self._raise_os
        )
        ok, msg = manager_with_oauth_site.update_site(
            "prod", base_url="https://new.example.com"
        )
        assert ok is False
        assert "Failed to save" in msg
        site = manager_with_oauth_site.get_site("prod")
        assert site is not None
        assert site["base_url"] == "https://prod.example.com"

    # ── settings mutations ────────────────────────────────────────────────

    def test_add_setting_reverts_on_save_failure(
        self, manager_with_settings, monkeypatch
    ):
        monkeypatch.setattr(
            "britecore_sdk.utils.config_manager.save_settings", self._raise_os
        )
        ok, msg = manager_with_settings.add_setting("default", "new_key", "val")
        assert ok is False
        assert "Failed to save" in msg
        assert manager_with_settings.get_setting("default", "new_key") is None

    def test_update_setting_reverts_on_save_failure(
        self, manager_with_settings, monkeypatch
    ):
        monkeypatch.setattr(
            "britecore_sdk.utils.config_manager.save_settings", self._raise_os
        )
        ok, msg = manager_with_settings.update_setting("default", "web_timeout", 999)
        assert ok is False
        assert "Failed to save" in msg
        assert manager_with_settings.get_setting("default", "web_timeout") == 5

    def test_delete_setting_reverts_on_save_failure(
        self, manager_with_settings, monkeypatch
    ):
        monkeypatch.setattr(
            "britecore_sdk.utils.config_manager.save_settings", self._raise_os
        )
        ok, msg = manager_with_settings.delete_setting("default", "web_timeout")
        assert ok is False
        assert "Failed to save" in msg
        assert manager_with_settings.get_setting("default", "web_timeout") == 5


class TestSettingsManagement:
    def test_add_setting_success(self, manager_with_settings):
        ok, msg = manager_with_settings.add_setting("default", "web_retry", 3)
        assert ok is True
        assert "web_retry" in msg

    def test_add_setting_persisted_to_disk(self, manager_with_settings):
        manager_with_settings.add_setting("default", "web_retry", 3)
        on_disk = toml.load(manager_with_settings.settings_path)
        assert on_disk["default"]["web_retry"] == 3

    def test_add_setting_creates_new_section(self, manager):
        ok, _ = manager.add_setting("custom_section", "some_key", "val")
        assert ok is True
        assert manager.get_setting("custom_section", "some_key") == "val"

    def test_add_setting_rejects_forbidden_key(self, manager):
        ok, msg = manager.add_setting("default", "api_key", "should-be-rejected")
        assert ok is False
        assert "secret" in msg.lower() or ".secrets.toml" in msg

    def test_update_setting_modifies_value(self, manager_with_settings):
        manager_with_settings.update_setting("default", "web_timeout", 30)
        assert manager_with_settings.get_setting("default", "web_timeout") == 30

    def test_update_setting_nonexistent_section_returns_error(self, manager):
        ok, msg = manager.update_setting("ghost", "key", "value")
        assert ok is False
        assert "ghost" in msg

    def test_update_setting_nonexistent_key_returns_error(self, manager_with_settings):
        ok, msg = manager_with_settings.update_setting("default", "no_such_key", 99)
        assert ok is False
        assert "no_such_key" in msg

    def test_delete_setting_removes_key(self, manager_with_settings):
        manager_with_settings.delete_setting("default", "web_timeout")
        assert manager_with_settings.get_setting("default", "web_timeout") is None

    def test_delete_setting_removes_empty_section(self, manager):
        manager.add_setting("temp_section", "only_key", "value")
        manager.delete_setting("temp_section", "only_key")
        assert "temp_section" not in manager.list_settings()

    def test_delete_setting_nonexistent_key_returns_error(self, manager_with_settings):
        ok, msg = manager_with_settings.delete_setting("default", "missing_key")
        assert ok is False
        assert "missing_key" in msg

    def test_list_settings_returns_dict(self, manager_with_settings):
        result = manager_with_settings.list_settings()
        assert isinstance(result, dict)
        assert "default" in result

    def test_get_setting_missing_section_returns_none(self, manager):
        assert manager.get_setting("no_section", "no_key") is None

    def test_get_setting_missing_key_returns_none(self, manager_with_settings):
        assert manager_with_settings.get_setting("default", "nonexistent") is None

    def test_get_available_defaults_returns_dict(self, manager):
        defaults = manager.get_available_defaults()
        assert isinstance(defaults, dict)
        assert len(defaults) > 0


def test_update_site_interactive_does_not_echo_raw_base_url(
    manager_with_oauth_site, monkeypatch, capsys
):
    """Interactive update flow should not print the configured base_url value."""
    from britecore_sdk.utils.config_manager import _update_site_interactive

    site_config = manager_with_oauth_site.config["prod"]
    site_config["base_url"] = "https://user:pass@example.com/path?token=secret-token"
    user_inputs = iter(["prod", "5"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(user_inputs))

    _update_site_interactive(manager_with_oauth_site)

    output = capsys.readouterr().out
    assert "Base URL: configured" in output
    assert "user:pass" not in output
    assert "secret-token" not in output
