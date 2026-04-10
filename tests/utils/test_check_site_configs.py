import importlib.util
import os

import pytest

# Path to the utility
UTIL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "src",
    "britecore_libraries",
    "utils",
    "check_site_configs.py",
)

spec = importlib.util.spec_from_file_location("check_site_configs", UTIL_PATH)
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
            "site_ok": {"base_url": "https://example", "api_key": "token"},
            "site_bad": {"base_url": "https://example"},
            "_meta": "ignore-me",
        }

    monkeypatch.setattr(check_site_configs, "warn_if_secrets_in_settings", fake_warn)
    monkeypatch.setattr(check_site_configs, "load_secrets", fake_load)

    check_site_configs.main()
    output = capsys.readouterr().out

    assert calls[0] == ("warn", check_site_configs.SETTINGS_PATH)
    assert calls[1] == ("load", check_site_configs.CONFIG_PATH)
    assert "Checking API config for 2 site(s)" in output
    assert "Site" in output and "Status" in output and "Missing Keys" in output
    assert "site_ok" in output and "OK" in output
    assert "site_bad" in output and "INCORRECT" in output
    assert "client_id, client_secret, api_key" in output
