"""Unit tests for interactive line menu utilities."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from britecore_libraries.api.api_calls.v2 import lines as lines_module
from britecore_libraries.utils import interactive_menu


class TestLineMenu:
    """Tests for line menu selection formatting and output contract."""

    @pytest.mark.unit
    def test_line_menu_returns_kwargs_ready_dict(self, monkeypatch):
        """line_menu returns kwargs that pass directly to get_export_line_file."""
        ask_mock = MagicMock(return_value="2026-01-01")
        select_mock = MagicMock(return_value=SimpleNamespace(ask=ask_mock))
        fake_questionary = SimpleNamespace(select=select_mock)
        monkeypatch.setitem(__import__("sys").modules, "questionary", fake_questionary)

        fake_client = MagicMock()
        fake_client.do_request.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        fake_client.process_result.side_effect = [
            [
                {"description": "2026-01-01", "id": "date-1"},
                {"description": "2026-07-01", "id": "date-2"},
            ],
            [{"name": "WI", "id": "state-1"}],
            [{"name": "Homeowners", "id": "line-1"}],
        ]
        monkeypatch.setattr(interactive_menu, "API_CLIENT", fake_client)

        result = interactive_menu.line_menu()

        assert result == {
            "line": ("date-1", "state-1", "line-1"),
            "line_name": "Homeowners",
        }
        select_mock.assert_called_once()
        call_kwargs = select_mock.call_args.kwargs
        assert call_kwargs["choices"] == ["2026-01-01", "2026-07-01"]

    @pytest.mark.unit
    def test_line_menu_prefers_effective_date_label(self, monkeypatch):
        """Date menu labels prefer effective_date over description text."""
        fake_questionary = SimpleNamespace(
            select=MagicMock(
                return_value=SimpleNamespace(ask=MagicMock(return_value="2026-01-01"))
            )
        )
        monkeypatch.setitem(__import__("sys").modules, "questionary", fake_questionary)

        fake_client = MagicMock()
        fake_client.do_request.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        fake_client.process_result.side_effect = [
            [
                {
                    "effective_date": "2026-01-01",
                    "description": "Long deployment note",
                    "id": "date-1",
                }
            ],
            [{"name": "WI", "id": "state-1"}],
            [{"name": "Homeowners", "id": "line-1"}],
        ]
        monkeypatch.setattr(interactive_menu, "API_CLIENT", fake_client)

        result = interactive_menu.line_menu()

        assert result["line"][0] == "date-1"
        # line_type is no longer present

    @pytest.mark.unit
    def test_line_menu_falls_back_when_questionary_console_unavailable(
        self, monkeypatch
    ):
        """When questionary fails to init a console, stdin fallback still works."""
        select_mock = MagicMock(side_effect=RuntimeError("No Windows console found"))
        fake_questionary = SimpleNamespace(select=select_mock)
        monkeypatch.setitem(__import__("sys").modules, "questionary", fake_questionary)

        # Date, state, and line selections for the fallback path.
        responses = iter(["2", "1", "1"])
        monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

        fake_client = MagicMock()
        fake_client.do_request.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        fake_client.process_result.side_effect = [
            [
                {"effective_date": "2026-01-01", "id": "date-1"},
                {"effective_date": "2026-07-01", "id": "date-2"},
            ],
            [{"name": "WI", "id": "state-1"}],
            [{"name": "Homeowners", "id": "line-1"}],
        ]
        monkeypatch.setattr(interactive_menu, "API_CLIENT", fake_client)

        result = interactive_menu.line_menu()

        assert result == {
            "line": ("date-2", "state-1", "line-1"),
            "line_name": "Homeowners",
        }

    @pytest.mark.unit
    def test_select_option_raises_keyboard_interrupt_when_selection_is_none(
        self, monkeypatch
    ):
        """None from questionary.ask maps to KeyboardInterrupt."""
        fake_questionary = SimpleNamespace(
            select=MagicMock(
                return_value=SimpleNamespace(ask=MagicMock(return_value=None))
            )
        )
        monkeypatch.setitem(__import__("sys").modules, "questionary", fake_questionary)

        with pytest.raises(KeyboardInterrupt):
            interactive_menu._select_option("Date", ["A", "B"])

    @pytest.mark.unit
    def test_select_option_falls_back_when_questionary_returns_non_string(
        self, monkeypatch
    ):
        """Non-string questionary selections trigger fallback stdin menu flow."""
        fake_questionary = SimpleNamespace(
            select=MagicMock(
                return_value=SimpleNamespace(ask=MagicMock(return_value=123))
            )
        )
        monkeypatch.setitem(__import__("sys").modules, "questionary", fake_questionary)
        monkeypatch.setattr("builtins.input", lambda _prompt: "1")

        selected = interactive_menu._select_option("Date", ["A", "B"])

        assert selected == "A"


class TestLinesExports:
    """Tests for line export wrapper compatibility inputs."""

    @pytest.mark.unit
    def test_v2_lines_module_no_longer_exposes_line_menu(self):
        """Interactive menu entry point lives in utils.interactive_menu only."""
        assert not hasattr(lines_module, "line_menu")

    @pytest.mark.unit
    def test_get_export_line_file_accepts_line_tuple(self, monkeypatch):
        """get_export_line_file accepts a line tuple and returns parsed result."""
        fake_client = MagicMock()
        fake_client.do_request.return_value = MagicMock()
        fake_client.process_result.return_value = '{"ok": true}'
        monkeypatch.setattr(lines_module, "API_CLIENT", fake_client)

        result = lines_module.get_export_line_file(
            line=("date-1", "state-1", "line-1"),
        )

        assert result == {"ok": True}
