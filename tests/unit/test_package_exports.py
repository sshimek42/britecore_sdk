"""Regression tests for lazy package-root exports."""

import importlib
import sys
from types import ModuleType

import pytest

_DEFERRABLE_SUBMODULES = [
    "britecore_libraries",
    "britecore_libraries.api.api_calls",
    "britecore_libraries.models",
    "britecore_libraries.models.contact",
    "britecore_libraries.validators",
    "britecore_libraries.validators.address_validator",
]


def _import_fresh_package(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Import the package root after clearing selected cached modules."""
    for module_name in _DEFERRABLE_SUBMODULES:
        monkeypatch.delitem(sys.modules, module_name, raising=False)
    return importlib.import_module("britecore_libraries")


class TestPackageRootExports:
    """Verify root exports remain available without eager submodule imports."""

    @pytest.mark.unit
    def test_root_import_is_lazy_for_convenience_exports(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Importing the root package should not eagerly import heavy submodules."""
        package = _import_fresh_package(monkeypatch)

        assert package.logger.name == "britecore_libraries"
        assert "britecore_libraries.api.api_calls" not in sys.modules
        assert "britecore_libraries.models" not in sys.modules
        assert "britecore_libraries.validators" not in sys.modules

    @pytest.mark.unit
    def test_root_exports_resolve_on_first_access(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Lazy exports should import and cache their backing modules on demand."""
        package = _import_fresh_package(monkeypatch)

        assert package.PhoneValidator.__name__ == "PhoneValidator"
        assert "britecore_libraries.validators" in sys.modules

        assert package.BritecoreContact.__name__ == "BritecoreContact"
        assert "britecore_libraries.models" in sys.modules

        assert callable(package.get_api_client)
        assert "britecore_libraries.api.api_calls" in sys.modules

    @pytest.mark.unit
    def test_root_all_and_dir_include_supported_exports(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The package root should advertise the existing public export surface."""
        package = _import_fresh_package(monkeypatch)

        expected_exports = {
            "BritecoreContact",
            "BritecorePolicy",
            "AddressValidator",
            "EmailValidator",
            "NameValidator",
            "PhoneValidator",
            "BritecoreError",
            "get_api_client",
            "get_async_api_client",
            "logger",
            "__version__",
        }

        assert expected_exports.issubset(set(package.__all__))
        assert expected_exports.issubset(set(dir(package)))
