"""Unit tests for ODBC configuration validation and lazy loading."""

from unittest.mock import MagicMock, patch

import pytest

from britecore_libraries.exceptions import BritecoreError


class TestLoadDatabaseConfig:
    """Tests for config.load_database_config helper."""

    @pytest.mark.unit
    def test_load_database_config_returns_values(self):
        """Returns validated DB settings when both keys are present."""
        from britecore_libraries.config import config

        with patch.object(config, "settings") as mock_settings:
            mock_settings.using_env.return_value.__enter__ = MagicMock(return_value=mock_settings)
            mock_settings.using_env.return_value.__exit__ = MagicMock(return_value=False)
            mock_settings.get.side_effect = ["Driver=ODBC", {"timeout": 30}]

            conn_string, conn_options = config.load_database_config("homestead")

            assert conn_string == "Driver=ODBC"
            assert conn_options == {"timeout": 30}

    @pytest.mark.unit
    def test_load_database_config_raises_for_missing_keys(self):
        """Raises configuration error when DB keys are missing."""
        from britecore_libraries.config import config

        with patch.object(config, "settings") as mock_settings:
            mock_settings.using_env.return_value.__enter__ = MagicMock(return_value=mock_settings)
            mock_settings.using_env.return_value.__exit__ = MagicMock(return_value=False)
            mock_settings.get.side_effect = [None, None]

            with pytest.raises(BritecoreError.ConfigurationError):
                config.load_database_config("homestead")

    @pytest.mark.unit
    def test_load_database_config_requires_target_site(self):
        """Raises configuration error when target_site is blank."""
        from britecore_libraries.config import config

        with pytest.raises(BritecoreError.ConfigurationError):
            config.load_database_config("")


class TestBritecoreOdbcLazyConfig:
    """Tests for lazy DB config behavior in britecore_odbc."""

    @pytest.mark.unit
    @patch("britecore_libraries.utils.britecore_odbc.pyodbc.connect")
    @patch("britecore_libraries.utils.britecore_odbc._resolve_db_config")
    def test_get_cursor_loads_config_when_args_missing(self, mock_resolve, mock_connect):
        """Uses resolved config when cursor args are not provided."""
        from britecore_libraries.utils.britecore_odbc import get_cursor

        mock_resolve.return_value = ("Driver=ODBC", {"timeout": 10})
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_connect.return_value = mock_conn

        result = get_cursor(target_site="wausau")

        assert result == mock_cursor
        mock_resolve.assert_called_once_with("wausau")
        mock_connect.assert_called_once_with("Driver=ODBC", timeout=10)

    @pytest.mark.unit
    @patch("britecore_libraries.utils.britecore_odbc._resolve_db_config")
    @patch("britecore_libraries.utils.britecore_odbc.pyodbc.connect")
    def test_get_cursor_prefers_explicit_args(self, mock_connect, mock_resolve):
        """Explicit cursor args bypass config resolution."""
        from britecore_libraries.utils.britecore_odbc import get_cursor

        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_connect.return_value = mock_conn

        result = get_cursor("ExplicitConn", {"autocommit": True})

        assert result == mock_cursor
        mock_resolve.assert_not_called()
        mock_connect.assert_called_once_with("ExplicitConn", autocommit=True)

    @pytest.mark.unit
    @patch("britecore_libraries.utils.britecore_odbc._resolve_db_config")
    def test_get_cursor_bubbles_config_errors(self, mock_resolve):
        """Config resolution errors are surfaced as configuration errors."""
        from britecore_libraries.utils.britecore_odbc import get_cursor

        mock_resolve.side_effect = BritecoreError.ConfigurationError("missing db config")

        with pytest.raises(BritecoreError.ConfigurationError):
            get_cursor(target_site="wausau")

    @pytest.mark.unit
    def test_get_cursor_requires_target_site_for_config_lookup(self):
        """Raises configuration error when target_site is not provided."""
        from britecore_libraries.utils.britecore_odbc import get_cursor

        with pytest.raises(BritecoreError.ConfigurationError):
            get_cursor()

    @pytest.mark.unit
    def test_get_cursor_requires_keyword_target_site(self):
        """Third positional arg is rejected to enforce explicit callsites."""
        from britecore_libraries.utils.britecore_odbc import get_cursor

        with pytest.raises(TypeError):
            get_cursor(None, None, "wausau")

