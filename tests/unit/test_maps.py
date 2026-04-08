"""Unit tests for maps module."""

import importlib
import sys

import pytest


class TestLoadRegexes:
    """Tests for load_regexes function."""

    @pytest.mark.unit
    def test_load_regexes_with_mips_system(self, monkeypatch):
        monkeypatch.setenv("system", "mips")
        from britecore_libraries.maps import load_regexes

        compiled_regexes, naming_groups = load_regexes()
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)
        assert "reg_name" in compiled_regexes
        assert "multi" in naming_groups

    @pytest.mark.unit
    def test_load_regexes_with_spectrum_v1_system(self, monkeypatch):
        monkeypatch.setenv("system", "spectrum_v1")
        from britecore_libraries.maps import load_regexes

        compiled_regexes, naming_groups = load_regexes()
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)
        assert "search_name_single" in compiled_regexes

    @pytest.mark.unit
    def test_load_regexes_with_spectrum_v2_system(self, monkeypatch):
        monkeypatch.setenv("system", "spectrum_v2")
        from britecore_libraries.maps import load_regexes

        compiled_regexes, naming_groups = load_regexes()
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)

    @pytest.mark.unit
    def test_load_regexes_raises_for_unknown_system(self, monkeypatch):
        monkeypatch.setenv("system", "invalid_system")
        from britecore_libraries.maps import load_regexes

        with pytest.raises(KeyError):
            load_regexes()


class TestMapsPublicExports:
    """Smoke tests for exported map symbols."""

    @pytest.mark.unit
    def test_load_regexes_exported(self):
        from britecore_libraries.maps import load_regexes

        assert callable(load_regexes)

    @pytest.mark.unit
    def test_all_exports_present(self):
        import britecore_libraries.maps as maps_mod

        for name in maps_mod.__all__:
            assert hasattr(maps_mod, name), f"__all__ entry missing from module: {name}"


class TestMapsStrictImports:
    """Maps package gracefully falls back when optional map modules are missing."""

    @pytest.mark.unit
    def test_maps_import_fails_when_required_module_missing(self):
        maps_key = "britecore_libraries.maps"
        blocked = "britecore_libraries.maps.britecore_agency_map"
        saved_maps = sys.modules.get(maps_key)
        saved_blocked = sys.modules.get(blocked, ...)

        try:
            sys.modules[blocked] = None  # type: ignore[assignment]
            sys.modules.pop(maps_key, None)
            maps_mod = importlib.import_module(maps_key)
            assert hasattr(maps_mod, "agency")
            assert maps_mod.agency == {}
        finally:
            if saved_maps is not None:
                sys.modules[maps_key] = saved_maps
            else:
                sys.modules.pop(maps_key, None)

            if saved_blocked is ...:
                sys.modules.pop(blocked, None)
            else:
                sys.modules[blocked] = saved_blocked  # type: ignore[assignment]
