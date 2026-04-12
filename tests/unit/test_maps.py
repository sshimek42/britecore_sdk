"""Unit tests for maps module."""

import re

import pytest


class TestGetCommonRegexes:
    """Tests for the carrier-agnostic get_common_regexes() function."""

    @pytest.mark.unit
    def test_returns_dict_of_patterns(self):
        from britecore_sdk.maps import get_common_regexes

        result = get_common_regexes()
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_contains_expected_keys(self):
        from britecore_sdk.maps import get_common_regexes

        result = get_common_regexes()
        for key in (
            "reg_name",
            "reg_address",
            "reg_phone",
            "reg_email",
            "reg_business_name",
            "search_email",
            "search_name_single",
            "search_name_mult",
            "street_name_replacement",
        ):
            assert key in result, f"Missing key: {key}"

    @pytest.mark.unit
    def test_does_not_require_system_env(self, monkeypatch):
        """get_common_regexes must work without any system env var."""
        monkeypatch.delenv("system", raising=False)
        from britecore_sdk.maps import get_common_regexes

        result = get_common_regexes()
        assert "reg_name" in result

    @pytest.mark.unit
    def test_patterns_are_compiled(self):
        from britecore_sdk.maps import get_common_regexes

        result = get_common_regexes()
        for key, val in result.items():
            if key != "street_name_replacement":
                assert isinstance(
                    val, re.Pattern
                ), f"Expected compiled Pattern for key {key!r}, got {type(val)}"


class TestLoadRegexes:
    """Tests for load_regexes function."""

    @pytest.mark.unit
    def test_load_regexes_with_system_env(self, monkeypatch):
        """load_regexes reads system from env var when no arg supplied."""
        monkeypatch.setenv("system", "mips")
        from britecore_sdk.maps import load_regexes

        compiled_regexes, naming_groups = load_regexes()
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)
        assert "reg_name" in compiled_regexes
        # naming_groups is empty — carrier data is injected by the caller
        assert naming_groups == {}

    @pytest.mark.unit
    def test_load_regexes_with_system_arg(self):
        """load_regexes accepts system= kwarg without env var."""
        from britecore_sdk.maps import load_regexes

        compiled_regexes, naming_groups = load_regexes(system="spectrum_v1")
        assert isinstance(compiled_regexes, dict)
        assert isinstance(naming_groups, dict)
        assert "search_name_single" in compiled_regexes

    @pytest.mark.unit
    def test_load_regexes_accepts_overrides(self):
        """Injected overrides replace the corresponding common key."""
        import re as _re

        from britecore_sdk.maps import load_regexes

        custom = {"search_name_single": _re.compile(r"custom_pattern")}
        compiled, _ = load_regexes(
            system="spectrum_v2",
            overrides=custom,
            naming_groups={"multi": {"last_name_1": 5}},
        )
        assert compiled["search_name_single"].pattern == "custom_pattern"

    @pytest.mark.unit
    def test_load_regexes_accepts_naming_groups(self):
        """Injected naming_groups are returned as-is."""
        from britecore_sdk.maps import load_regexes

        groups = {"multi": {"last_name_1": 1, "first_name_1": 2}}
        _, returned_groups = load_regexes(system="mips", naming_groups=groups)
        assert returned_groups == groups

    @pytest.mark.unit
    def test_load_regexes_unknown_system_returns_common(self, monkeypatch):
        """Unknown system returns common regexes; KeyError is raised by
        the caller (RegexMappings), not by load_regexes itself."""
        from britecore_sdk.maps import load_regexes

        compiled, groups = load_regexes(
            system="unknown_system",
            overrides={},
            naming_groups={},
        )
        assert "reg_name" in compiled
        assert groups == {}

    @pytest.mark.unit
    def test_load_regexes_raises_when_system_not_set(self, monkeypatch):
        """load_regexes raises ValueError when no system is provided at all."""
        monkeypatch.delenv("system", raising=False)
        from britecore_sdk.maps import load_regexes

        with pytest.raises(ValueError, match="system"):
            load_regexes()


class TestMapsPublicExports:
    """Smoke tests for exported map symbols."""

    @pytest.mark.unit
    def test_load_regexes_exported(self):
        from britecore_sdk.maps import load_regexes

        assert callable(load_regexes)

    @pytest.mark.unit
    def test_get_common_regexes_exported(self):
        from britecore_sdk.maps import get_common_regexes

        assert callable(get_common_regexes)

    @pytest.mark.unit
    def test_all_exports_present(self):
        import britecore_sdk.maps as maps_mod

        for name in maps_mod.__all__:
            assert hasattr(maps_mod, name), f"__all__ entry missing from module: {name}"
