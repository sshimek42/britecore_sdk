"""Unit tests for the interactive configuration wizard."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from britecore_sdk.cli import config_wizard


class TestConfigWizard:
    """Tests for safe configuration wizard persistence behavior."""

    @pytest.mark.unit
    def test_main_does_not_persist_api_key_to_disk(self, monkeypatch, tmp_path, capsys):
        """API key auth stores non-sensitive settings only and prints env guidance."""

        def prompt(value: str) -> SimpleNamespace:
            return SimpleNamespace(ask=MagicMock(return_value=value))

        fake_questionary = SimpleNamespace(
            text=MagicMock(
                side_effect=[
                    prompt("sandbox"),
                    prompt("https://example.britecore.test"),
                ]
            ),
            select=MagicMock(
                side_effect=[
                    prompt("API Key"),
                    prompt("./britecore_secrets.toml (project-local)"),
                ]
            ),
            password=MagicMock(side_effect=[prompt("super-secret-api-key")]),
        )
        monkeypatch.setitem(__import__("sys").modules, "questionary", fake_questionary)
        monkeypatch.chdir(tmp_path)

        exit_code = config_wizard.main([])

        output = capsys.readouterr().out
        saved_content = (tmp_path / ".britecore_secrets.toml").read_text(
            encoding="utf-8"
        )

        assert exit_code == 0
        assert 'base_url = "https://example.britecore.test"' in saved_content
        assert "api_key" not in saved_content
        assert "super-secret-api-key" not in saved_content
        assert "Sensitive credentials were not written to disk." in output
        assert "BRITECORE_SDK_API_KEY" in output

    @pytest.mark.unit
    def test_main_does_not_persist_oauth_secret_to_disk(
        self, monkeypatch, tmp_path, capsys
    ):
        """OAuth auth stores non-sensitive settings only and prints env guidance."""

        def prompt(value: str) -> SimpleNamespace:
            return SimpleNamespace(ask=MagicMock(return_value=value))

        fake_questionary = SimpleNamespace(
            text=MagicMock(
                side_effect=[
                    prompt("production"),
                    prompt("https://example.britecore.test"),
                    prompt("client-id-123"),
                ]
            ),
            select=MagicMock(
                side_effect=[
                    prompt("OAuth (Client Credentials)"),
                    prompt("./britecore_secrets.toml (project-local)"),
                ]
            ),
            password=MagicMock(side_effect=[prompt("super-secret-client-secret")]),
        )
        monkeypatch.setitem(__import__("sys").modules, "questionary", fake_questionary)
        monkeypatch.chdir(tmp_path)

        exit_code = config_wizard.main([])

        output = capsys.readouterr().out
        saved_content = (tmp_path / ".britecore_secrets.toml").read_text(
            encoding="utf-8"
        )

        assert exit_code == 0
        assert 'base_url = "https://example.britecore.test"' in saved_content
        assert "client_id" not in saved_content
        assert "client_secret" not in saved_content
        assert "super-secret-client-secret" not in saved_content
        assert "Sensitive credentials were not written to disk." in output
        assert "BRITECORE_SDK_CLIENT_ID" in output
        assert "BRITECORE_SDK_CLIENT_SECRET" in output
