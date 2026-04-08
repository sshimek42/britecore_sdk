"""Unit tests for selenium utility config and browser behavior."""

from unittest.mock import MagicMock, patch

import pytest

from britecore_libraries.exceptions import BritecoreError


class TestSeleniumSettingsCompatibility:
    """Tests that selenium utility reads flat settings.toml keys safely."""

    @pytest.mark.unit
    def test_module_imports_with_flat_settings(self):
        """Module import succeeds when using flat settings keys."""
        from britecore_libraries.utils import britecore_selenium

        assert britecore_selenium is not None
        assert hasattr(britecore_selenium, "web_browser")


class TestGetDriver:
    """Tests for browser selection and override behavior."""

    @pytest.mark.unit
    @patch("britecore_libraries.utils.britecore_selenium.webdriver.Edge")
    def test_get_driver_uses_default_browser(self, mock_edge):
        """No argument uses configured/default browser value."""
        from britecore_libraries.utils.britecore_selenium import get_driver

        mock_driver = MagicMock()
        mock_edge.return_value = mock_driver

        result = get_driver()

        assert result == mock_driver
        mock_driver.maximize_window.assert_called_once()

    @pytest.mark.unit
    @patch("britecore_libraries.utils.britecore_selenium.webdriver.Firefox")
    def test_get_driver_explicit_browser_overrides_config(self, mock_firefox):
        """Explicit browser argument takes precedence over config default."""
        from britecore_libraries.utils.britecore_selenium import get_driver

        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        result = get_driver("firefox")

        assert result == mock_driver
        mock_driver.maximize_window.assert_called_once()

    @pytest.mark.unit
    def test_get_driver_invalid_browser_raises(self):
        """Unsupported browser names raise a BritecoreError.Base."""
        from britecore_libraries.utils.britecore_selenium import get_driver

        with pytest.raises(BritecoreError.Base):
            get_driver("netscape")


class TestBcLoginDefaults:
    """Tests for bc_login usage of flat setting defaults."""

    @pytest.mark.unit
    def test_bc_login_uses_passed_user_in_logs(self):
        """Logger should use function user parameter, not direct settings attr."""
        from britecore_libraries.utils.britecore_selenium import bc_login

        mock_driver = MagicMock()
        user_box = MagicMock()
        pass_box = MagicMock()
        mock_driver.find_elements.return_value = [user_box, pass_box]
        mock_driver.title = "Dashboard"

        with patch("britecore_libraries.utils.britecore_selenium.logger") as mock_logger:
            bc_login(
                driver=mock_driver,
                url="https://example.com",
                user="test_user",
                password="test_pass",
            )

            mock_logger.debug.assert_called_once_with(
                "Logging into BriteCore as %s", "test_user"
            )

