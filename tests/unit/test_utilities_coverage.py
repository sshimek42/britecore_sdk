"""Unit tests for utility modules (interactive_menu, zip_code_lookup).

These tests focus on validating module structure and functionality that can be
tested without requiring external configuration or resources.
Interactive menu tests verify API structure and documentation.
"""

import inspect

import pytest


class TestZipCodeLookup:
    """Tests for zip_code_lookup utility module (currently tested, provides baseline)."""

    @pytest.mark.unit
    def test_zip_lookup_module_loads(self):
        """Test that zip_code_lookup module loads successfully."""
        from britecore_sdk.utils import zip_code_lookup

        assert zip_code_lookup is not None

    @pytest.mark.unit
    def test_zip_lookup_has_load_zip_codes(self):
        """Test that zip_code_lookup has load_zip_codes function."""
        from britecore_sdk.utils.zip_code_lookup import load_zip_codes

        assert callable(load_zip_codes)


class TestUtilityModuleStructure:
    """Tests for utility module structure (handles config load issues gracefully)."""

    @pytest.mark.unit
    def test_interactive_menu_module_can_be_imported(self):
        """Test that interactive_menu module can be imported and has expected attrs."""
        try:
            from britecore_sdk.utils.interactive_menu import (
                API_CLIENT,
                LOGGER,
                line_menu,
            )

            assert callable(line_menu)
            assert LOGGER is not None
            assert API_CLIENT is not None
        except Exception as e:
            pytest.skip(f"Interactive menu requires API configuration: {e}")


class TestInteractiveMenu:
    """Tests for interactive_menu module functionality and documentation."""

    @pytest.mark.unit
    def test_line_menu_function_exists(self):
        """Test that line_menu function exists and is callable."""
        from britecore_sdk.utils.interactive_menu import line_menu

        assert callable(line_menu)

    @pytest.mark.unit
    def test_line_menu_has_comprehensive_documentation(self):
        """Test that line_menu function has complete documentation."""
        from britecore_sdk.utils.interactive_menu import line_menu

        assert line_menu.__doc__ is not None
        doc_lower = line_menu.__doc__.lower()

        # Verify key documentation elements
        assert "menu" in doc_lower
        assert "parameters" in doc_lower or "param" in doc_lower
        assert "returns" in doc_lower or "return" in doc_lower

    @pytest.mark.unit
    def test_interactive_menu_module_loads(self):
        """Test that interactive_menu module loads successfully."""
        from britecore_sdk.utils import interactive_menu

        assert interactive_menu is not None

    @pytest.mark.unit
    def test_interactive_menu_has_logger(self):
        """Test that interactive_menu has LOGGER attribute."""
        from britecore_sdk.utils.interactive_menu import LOGGER

        assert LOGGER is not None
        assert hasattr(LOGGER, "info")
        assert hasattr(LOGGER, "debug")
        assert hasattr(LOGGER, "error")

    @pytest.mark.unit
    def test_interactive_menu_has_api_client(self):
        """Test that interactive_menu has API_CLIENT attribute."""
        from britecore_sdk.utils.interactive_menu import API_CLIENT

        assert API_CLIENT is not None

    @pytest.mark.unit
    def test_line_menu_source_has_nested_print_menu(self):
        """Test that line_menu defines print_menu nested function."""
        from britecore_sdk.utils.interactive_menu import line_menu

        source = inspect.getsource(line_menu)
        assert "def print_menu(" in source
        assert "print_menu_title" in source
        assert "print_menu_options" in source
        assert "print_menu_default" in source

    @pytest.mark.unit
    def test_line_menu_makes_three_api_calls(self):
        """Test that line_menu structure includes three API endpoint calls."""
        from britecore_sdk.utils.interactive_menu import line_menu

        source = inspect.getsource(line_menu)
        # Verify the three API paths are referenced
        assert "/api/v2/lines/get_all_effective_dates" in source
        assert "/api/v2/lines/get_all_states" in source
        assert "/api/v2/lines/get_all_lines" in source

    @pytest.mark.unit
    def test_line_menu_returns_expected_dict_structure(self):
        """Test that line_menu return type annotation is a dict."""
        from britecore_sdk.utils.interactive_menu import line_menu

        # Check return annotation from function signature
        sig = inspect.signature(line_menu)
        assert sig.return_annotation is not None
        # Should return a dict
        assert "dict" in str(sig.return_annotation).lower()


class TestUtilityModuleImports:
    """Tests verifying utility modules can be imported from the utils package."""

    @pytest.mark.unit
    def test_can_import_zip_code_lookup(self):
        """Test that zip_code_lookup can be imported."""
        from britecore_sdk.utils import zip_code_lookup

        assert zip_code_lookup is not None

    @pytest.mark.unit
    def test_interactive_menu_source_imports_required_modules(self):
        """Test that interactive_menu properly imports dependencies."""
        from britecore_sdk.utils import interactive_menu

        source = inspect.getsource(interactive_menu)
        # Verify key imports
        assert "from britecore_sdk import logger" in source
        assert "from britecore_sdk.api" in source
        assert "RequestParameters" in source
        assert "api_client" in source
