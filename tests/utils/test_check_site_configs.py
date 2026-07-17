import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import pytest

# Path to the utility
UTIL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "src",
    "britecore_sdk",
    "utils",
    "check_site_configs.py",
)

spec = importlib.util.spec_from_file_location("check_site_configs", UTIL_PATH)
assert spec is not None
assert spec.loader is not None
check_site_configs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_site_configs)


def test_load_secrets_missing_file_exits(monkeypatch, capsys):
    monkeypatch.setattr(check_site_configs.os.path, "exists", lambda _path: False)

    with pytest.raises(SystemExit) as exc:
        check_site_configs.load_secrets("missing.toml")

    assert exc.value.code == 1
    assert "Config file not found: missing.toml" in capsys.readouterr().out


def test_load_secrets_existing_file_returns_loaded_toml(monkeypatch):
    expected = {"dev": {"base_url": "https://example"}}
    monkeypatch.setattr(check_site_configs.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(check_site_configs.toml, "load", lambda _path: expected)

    assert check_site_configs.load_secrets("present.toml") == expected


@pytest.mark.parametrize(
    ("config", "ok", "missing"),
    [
        ({"base_url": "x", "client_id": "id", "client_secret": "secret"}, True, []),
        ({"base_url": "x", "api_key": "key"}, True, []),
        ({"api_key": "key"}, False, ["base_url"]),
        (
            {"base_url": "x"},
            False,
            ["client_id", "client_secret", "api_key"],
        ),
        (
            {"base_url": "x", "client_id": "id"},
            False,
            ["client_secret", "api_key"],
        ),
    ],
)
def test_check_site_reports_expected_missing_keys(config, ok, missing):
    actual_ok, actual_missing = check_site_configs.check_site("dev", config)
    assert actual_ok is ok
    assert actual_missing == missing


def test_warn_if_secrets_in_settings_no_file_no_output(monkeypatch, capsys):
    monkeypatch.setattr(check_site_configs.os.path, "exists", lambda _path: False)

    check_site_configs.warn_if_secrets_in_settings("settings.toml")

    assert capsys.readouterr().out == ""


def test_warn_if_secrets_in_settings_nested_key_warning(monkeypatch, capsys):
    monkeypatch.setattr(check_site_configs.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(
        check_site_configs.toml,
        "load",
        lambda _path: {"dev": {"api_key": "abc"}},
    )

    check_site_configs.warn_if_secrets_in_settings("settings.toml")
    output = capsys.readouterr().out

    assert "Sensitive keys found in settings.toml" in output
    assert "Section: dev, Key: api_key" in output


def test_warn_if_secrets_in_settings_top_level_key_warning(monkeypatch, capsys):
    monkeypatch.setattr(check_site_configs.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(
        check_site_configs.toml, "load", lambda _path: {"client_secret": "xyz"}
    )

    check_site_configs.warn_if_secrets_in_settings("settings.toml")
    output = capsys.readouterr().out

    assert "Sensitive keys found in settings.toml" in output
    assert "Section: [top-level], Key: client_secret" in output


def test_warn_if_secrets_in_settings_ignores_falsy_values(monkeypatch, capsys):
    monkeypatch.setattr(check_site_configs.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(
        check_site_configs.toml,
        "load",
        lambda _path: {"dev": {"api_key": ""}, "client_secret": ""},
    )

    check_site_configs.warn_if_secrets_in_settings("settings.toml")

    assert capsys.readouterr().out == ""


def test_main_prints_status_table_and_filters_non_site_sections(monkeypatch, capsys):
    calls = []

    def fake_warn(path):
        calls.append(("warn", path))

    def fake_load(path):
        calls.append(("load", path))
        return {
            "site_ok": {"base_url": "https://example.com", "api_key": "token"},
            "site_bad": {"base_url": "https://example.com"},
            "_meta": "ignore-me",
        }

    monkeypatch.setattr(check_site_configs, "warn_if_secrets_in_settings", fake_warn)
    monkeypatch.setattr(check_site_configs, "load_secrets", fake_load)
    monkeypatch.setattr(
        check_site_configs,
        "_print_config_source_diagnostics",
        lambda: calls.append(("diag", None)),
    )

    check_site_configs.main()
    output = capsys.readouterr().out

    assert calls[0] == ("load", check_site_configs.CONFIG_PATH)
    assert calls[1] == ("diag", None)
    assert calls[2] == ("warn", check_site_configs.SETTINGS_PATH)
    assert "Checking API config for 2 site(s)" in output
    assert "Site" in output and "Status" in output and "Missing Keys" in output
    assert "Auth" in output and "URL" in output
    assert "site_ok" in output and "OK" in output
    assert "API Key" in output
    assert any(urlparse(w).netloc == "example.com" for w in output.split())
    assert "site_bad" in output and "INCORRECT" in output
    assert "client_id, client_secret, api_key" in output


@pytest.mark.parametrize(
    ("config", "expected_auth"),
    [
        ({"client_id": "id", "client_secret": "secret"}, "OAuth"),
        ({"client_id": "id", "client_secret": "secret", "api_key": "k"}, "OAuth"),
        ({"api_key": "key"}, "API Key"),
        ({"base_url": "https://x"}, "-"),
        ({}, "-"),
    ],
)
def test_get_auth_mode(config, expected_auth):
    assert check_site_configs.get_auth_mode(config) == expected_auth


def test_main_shows_oauth_auth_mode(monkeypatch, capsys):
    monkeypatch.setattr(
        check_site_configs, "_print_config_source_diagnostics", lambda: None
    )
    monkeypatch.setattr(
        check_site_configs, "warn_if_secrets_in_settings", lambda _: None
    )
    monkeypatch.setattr(
        check_site_configs,
        "load_secrets",
        lambda _: {
            "prod": {
                "base_url": "https://prod.example.com",
                "client_id": "cid",
                "client_secret": "csecret",
            }
        },
    )
    check_site_configs.main()
    output = capsys.readouterr().out
    assert "OAuth" in output
    assert any(urlparse(w).netloc == "prod.example.com" for w in output.split())


def test_main_json_output_includes_precedence_and_sites(monkeypatch, capsys):
    monkeypatch.setattr(
        check_site_configs,
        "load_secrets",
        lambda _: {
            "prod": {
                "base_url": "https://prod.example.com",
                "api_key": "token",
            },
            "_meta": "ignore",
        },
    )
    monkeypatch.setattr(
        check_site_configs,
        "_find_sensitive_keys_in_settings",
        lambda _path: [{"section": "default", "key": "api_key"}],
    )
    monkeypatch.setattr(
        check_site_configs,
        "setting_files_full",
        [Path("C:/work/repo/britecore.toml")],
    )

    check_site_configs.main(["--json"])
    payload = json.loads(capsys.readouterr().out)

    assert payload["config_precedence"][-1] == "envvar_britecore_sdk_prefix"
    assert payload["resolved_settings_files"]
    assert payload["active_paths"]["secrets_file"]
    assert payload["warnings"]["sensitive_keys_in_settings"] == [
        {"section": "default", "key": "api_key"}
    ]
    assert payload["sites"] == [
        {
            "site": "prod",
            "ok": True,
            "status": "OK",
            "auth_mode": "API Key",
            "url": "https://prod.example.com",
            "missing_keys": [],
        }
    ]


def test_main_json_mode_does_not_call_text_warning_output(monkeypatch, capsys):
    called: list[str] = []
    monkeypatch.setattr(
        check_site_configs,
        "warn_if_secrets_in_settings",
        lambda _: called.append("warn"),
    )
    monkeypatch.setattr(
        check_site_configs,
        "load_secrets",
        lambda _: {"prod": {"base_url": "https://x", "api_key": "k"}},
    )

    check_site_configs.main(["--json"])
    _ = json.loads(capsys.readouterr().out)

    assert called == []


def test_main_honors_sys_argv_json_mode(monkeypatch, capsys):
    monkeypatch.setattr(
        check_site_configs.sys,
        "argv",
        ["check_site_configs", "--json"],
    )
    monkeypatch.setattr(
        check_site_configs,
        "load_secrets",
        lambda _: {"prod": {"base_url": "https://x", "api_key": "k"}},
    )

    check_site_configs.main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["sites"][0]["site"] == "prod"


def test_display_path_aliases_home_and_cwd(monkeypatch):
    import os

    fake_home = Path("C:/Users/tester")
    fake_cwd = Path("C:/work/repo")

    monkeypatch.setattr(
        check_site_configs.Path, "home", staticmethod(lambda: fake_home)
    )
    monkeypatch.setattr(check_site_configs.Path, "cwd", staticmethod(lambda: fake_cwd))

    in_home = fake_home / ".britecore" / "settings.toml"
    in_cwd = fake_cwd / "britecore.toml"
    external = Path("D:/shared/settings.toml")

    # Expected output should be OS-normalized
    home_result = check_site_configs._display_path(in_home)
    assert home_result == f"~{os.sep}.britecore{os.sep}settings.toml"

    cwd_result = check_site_configs._display_path(in_cwd)
    assert cwd_result == f".{os.sep}britecore.toml"

    external_result = check_site_configs._display_path(external)
    assert external_result.endswith(f"D:{os.sep}shared{os.sep}settings.toml")


def test_print_config_source_diagnostics_includes_resolved_files(monkeypatch, capsys):
    fake_files = [
        Path("C:/work/repo/britecore.toml"),
        Path("C:/Users/tester/.britecore/settings.toml"),
    ]
    monkeypatch.setattr(check_site_configs, "setting_files_full", fake_files)
    monkeypatch.setattr(
        check_site_configs,
        "_display_path",
        lambda path: f"display::{Path(path).name}",
    )

    check_site_configs._print_config_source_diagnostics()
    output = capsys.readouterr().out

    assert "Configuration source precedence" in output
    assert "BRITECORE_SDK_* environment variables" in output
    assert "Resolved settings files (load order):" in output
    assert "1. display::britecore.toml" in output
    assert "2. display::settings.toml" in output
