"""Unit tests for regex maps module."""

import os
from unittest.mock import patch

import pytest


class TestLoadRegexes:
    """Tests for load_regexes function."""

    @pytest.mark.unit
    def test_load_regexes_with_mips_system(self, monkeypatch):
        """Test load_regexes with mips system."""
        monkeypatch.setenv("system", "mips")
        
        from britecore_libraries.maps.britecore_policy_name_map import load_regexes
        
        compiled_regexes, naming_groups = load_regexes()
        
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)
        assert len(compiled_regexes) > 0
        assert "reg_name" in compiled_regexes
        assert "multi" in naming_groups

    @pytest.mark.unit
    def test_load_regexes_with_spectrum_v1_system(self, monkeypatch):
        """Test load_regexes with spectrum_v1 system."""
        monkeypatch.setenv("system", "spectrum_v1")
        
        from britecore_libraries.maps.britecore_policy_name_map import load_regexes
        
        compiled_regexes, naming_groups = load_regexes()
        
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)
        assert "search_name_single" in compiled_regexes

    @pytest.mark.unit
    def test_load_regexes_with_spectrum_v2_system(self, monkeypatch):
        """Test load_regexes with spectrum_v2 system."""
        monkeypatch.setenv("system", "spectrum_v2")
        
        from britecore_libraries.maps.britecore_policy_name_map import load_regexes
        
        compiled_regexes, naming_groups = load_regexes()
        
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)

    @pytest.mark.unit
    def test_load_regexes_fallback_empty_system(self, monkeypatch):
        """Test load_regexes defaults to mips when system is empty."""
        monkeypatch.delenv("system", raising=False)
        
        from britecore_libraries.maps.britecore_policy_name_map import load_regexes
        
        compiled_regexes, naming_groups = load_regexes()
        
        # Should fallback to mips defaults
        assert isinstance(compiled_regexes, dict)
        assert len(compiled_regexes) > 0

    @pytest.mark.unit
    def test_load_regexes_fallback_invalid_system(self, monkeypatch):
        """Test load_regexes defaults to mips when system is invalid."""
        monkeypatch.setenv("system", "invalid_system")
        
        from britecore_libraries.maps.britecore_policy_name_map import load_regexes
        
        compiled_regexes, naming_groups = load_regexes()
        
        # Should fallback to mips even with invalid system
        assert isinstance(compiled_regexes, dict)
        assert len(compiled_regexes) > 0

    @pytest.mark.unit
    def test_load_regexes_contains_common_patterns(self, monkeypatch):
        """Test that compiled regexes contain expected common patterns."""
        monkeypatch.setenv("system", "mips")
        
        from britecore_libraries.maps.britecore_policy_name_map import load_regexes
        
        compiled_regexes, _ = load_regexes()
        
        # Verify common patterns are present
        expected_patterns = [
            "reg_name",
            "reg_email",
            "reg_phone",
            "reg_address",
            "reg_zip",
            "reg_business_name",
        ]
        
        for pattern_name in expected_patterns:
            assert pattern_name in compiled_regexes, f"Missing pattern: {pattern_name}"

