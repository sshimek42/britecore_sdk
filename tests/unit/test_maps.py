"""Unit tests for regex maps module."""

import importlib
import sys

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


# ---------------------------------------------------------------------------
# Built-in fallback implementation
# ---------------------------------------------------------------------------


class TestBuiltinLoadRegexes:
    """Tests for the inline _builtin_load_regexes fallback function."""

    @pytest.mark.unit
    def test_builtin_returns_tuple(self, monkeypatch):
        """_builtin_load_regexes returns a (dict, dict) tuple."""
        monkeypatch.setenv("system", "mips")
        from britecore_libraries.maps import _builtin_load_regexes

        result = _builtin_load_regexes()
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.unit
    def test_builtin_mips_regexes(self, monkeypatch):
        """Built-in mips regexes contain the expected common patterns."""
        monkeypatch.setenv("system", "mips")
        from britecore_libraries.maps import _builtin_load_regexes

        regexes, groups = _builtin_load_regexes()

        for key in ("reg_name", "reg_email", "reg_phone", "reg_address", "reg_zip"):
            assert key in regexes, f"Missing builtin pattern: {key}"
        assert "multi" in groups

    @pytest.mark.unit
    def test_builtin_spectrum_v1(self, monkeypatch):
        """Built-in spectrum_v1 regexes override search_name_* patterns."""
        monkeypatch.setenv("system", "spectrum_v1")
        from britecore_libraries.maps import _builtin_load_regexes

        regexes, groups = _builtin_load_regexes()

        assert "search_name_single" in regexes
        assert "search_name_mult" in regexes
        assert "multi" in groups

    @pytest.mark.unit
    def test_builtin_spectrum_v2(self, monkeypatch):
        """Built-in spectrum_v2 regexes override search_name_* patterns."""
        monkeypatch.setenv("system", "spectrum_v2")
        from britecore_libraries.maps import _builtin_load_regexes

        regexes, groups = _builtin_load_regexes()

        assert "search_name_single" in regexes
        assert "multi" in groups

    @pytest.mark.unit
    def test_builtin_unknown_system_defaults_to_mips(self, monkeypatch):
        """Built-in falls back to mips for unknown system env value."""
        monkeypatch.setenv("system", "nonexistent_system")
        from britecore_libraries.maps import _builtin_load_regexes

        regexes, groups = _builtin_load_regexes()

        assert "reg_name" in regexes
        assert "multi" in groups


# ---------------------------------------------------------------------------
# Public exports shape / type checks
# ---------------------------------------------------------------------------


class TestMapsPublicExports:
    """Smoke tests – every symbol in __all__ is importable and correctly typed."""

    @pytest.mark.unit
    def test_load_regexes_exported(self):
        from britecore_libraries.maps import load_regexes

        assert callable(load_regexes)

    @pytest.mark.unit
    def test_agency_is_dict(self):
        from britecore_libraries.maps import agency

        assert isinstance(agency, dict)

    @pytest.mark.unit
    def test_policy_map_is_dict(self):
        from britecore_libraries.maps import policy_map

        assert isinstance(policy_map, dict)

    @pytest.mark.unit
    def test_britecore_policy_type_map_is_dict(self):
        from britecore_libraries.maps import britecore_policy_type_map

        assert isinstance(britecore_policy_type_map, dict)

    @pytest.mark.unit
    def test_field_map_to_britecore_is_dict(self):
        from britecore_libraries.maps import field_map_to_britecore

        assert isinstance(field_map_to_britecore, dict)

    @pytest.mark.unit
    def test_field_map_to_named_insured_is_dict(self):
        from britecore_libraries.maps import field_map_to_named_insured

        assert isinstance(field_map_to_named_insured, dict)

    @pytest.mark.unit
    def test_field_map_to_risk_location_is_dict(self):
        from britecore_libraries.maps import field_map_to_risk_location

        assert isinstance(field_map_to_risk_location, dict)

    @pytest.mark.unit
    def test_all_exports_present(self):
        import britecore_libraries.maps as maps_mod

        for name in maps_mod.__all__:
            assert hasattr(maps_mod, name), f"__all__ entry missing from module: {name}"


# ---------------------------------------------------------------------------
# ImportError fallback — simulate absent private map files
# ---------------------------------------------------------------------------


def _reload_maps_with_blocked(blocked_module: str):
    """Reload britecore_libraries.maps with *blocked_module* set to None in
    sys.modules so that the try/except ImportError branch is exercised."""
    maps_key = "britecore_libraries.maps"
    saved_maps = sys.modules.get(maps_key)
    saved_blocked = sys.modules.get(blocked_module, ...)  # sentinel

    try:
        sys.modules[blocked_module] = None  # type: ignore[assignment]
        # Remove the cached maps package so it re-executes on next import
        sys.modules.pop(maps_key, None)
        reloaded = importlib.import_module(maps_key)
        return reloaded
    finally:
        # Restore original state
        if saved_maps is not None:
            sys.modules[maps_key] = saved_maps
        else:
            sys.modules.pop(maps_key, None)

        if saved_blocked is ...:
            sys.modules.pop(blocked_module, None)
        else:
            sys.modules[blocked_module] = saved_blocked  # type: ignore[assignment]


class TestImportErrorFallbacks:
    """Verify that each *_map.py falling back via ImportError yields safe defaults."""

    @pytest.mark.unit
    def test_agency_map_absent_yields_empty_dict(self):
        """agency falls back to {} when britecore_agency_map.py is absent."""
        reloaded = _reload_maps_with_blocked(
            "britecore_libraries.maps.britecore_agency_map"
        )
        assert reloaded.agency == {}

    @pytest.mark.unit
    def test_policy_map_absent_yields_empty_dicts(self):
        """policy_map and britecore_policy_type_map fall back to {} when absent."""
        reloaded = _reload_maps_with_blocked(
            "britecore_libraries.maps.britecore_policy_map"
        )
        assert reloaded.policy_map == {}
        assert reloaded.britecore_policy_type_map == {}

    @pytest.mark.unit
    def test_field_map_absent_yields_empty_dicts(self):
        """All field maps fall back to {} when britecore_field_map.py is absent."""
        reloaded = _reload_maps_with_blocked(
            "britecore_libraries.maps.britecore_field_map"
        )
        assert reloaded.field_map_to_britecore == {}
        assert reloaded.field_map_to_named_insured == {}
        assert reloaded.field_map_to_risk_location == {}

    @pytest.mark.unit
    def test_policy_name_map_absent_uses_builtin_load_regexes(self, monkeypatch):
        """load_regexes falls back to _builtin_load_regexes when the private file is absent."""
        monkeypatch.setenv("system", "mips")
        reloaded = _reload_maps_with_blocked(
            "britecore_libraries.maps.britecore_policy_name_map"
        )
        # load_regexes must still be callable and return valid data
        assert callable(reloaded.load_regexes)
        regexes, groups = reloaded.load_regexes()
        assert isinstance(regexes, dict)
        assert "reg_name" in regexes
        assert "multi" in groups

