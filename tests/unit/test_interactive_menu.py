"""Unit tests for interactive line menu utilities."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from britecore_libraries.utils import interactive_menu


class TestLineMenu:
    """Tests for line menu selection formatting and compatibility output."""

    @pytest.mark.unit
    def test_line_menu_returns_kwargs_ready_dict(self, monkeypatch):
        """line_menu returns kwargs that pass directly to get_export_line_file."""
        fake_pyinputplus = SimpleNamespace(inputMenu=MagicMock(return_value="2026-01-01"))
        monkeypatch.setitem(__import__("sys").modules, "pyinputplus", fake_pyinputplus)

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
            "line_type": "Line",
            "line_name": "Homeowners",
        }

    @pytest.mark.unit
    def test_line_menu_legacy_tuple_mode(self, monkeypatch):
        """line_menu(legacy_tuple=True) keeps backward-compatible tuple output."""
        fake_pyinputplus = SimpleNamespace(inputMenu=MagicMock(return_value="2026-01-01"))
        monkeypatch.setitem(__import__("sys").modules, "pyinputplus", fake_pyinputplus)

        fake_client = MagicMock()
        fake_client.do_request.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        fake_client.process_result.side_effect = [
            [{"description": "2026-01-01", "id": "date-1"}],
            [{"name": "WI", "id": "state-1"}],
            [{"name": "Homeowners", "id": "line-1"}],
        ]
        monkeypatch.setattr(interactive_menu, "API_CLIENT", fake_client)

        result = interactive_menu.line_menu(legacy_tuple=True)

        assert result == ("date-1", "state-1", "line-1", "2026-01-01", "WI", "Homeowners")

