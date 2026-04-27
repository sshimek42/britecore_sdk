"""Regression tests for lazy package-root exports."""

import importlib
import logging
import sys
from types import ModuleType

import pytest

_DEFERRABLE_SUBMODULES = [
    "britecore_sdk",
    "britecore_sdk.api.api_calls",
    "britecore_sdk.models",
    "britecore_sdk.models.contact",
    "britecore_sdk.validators",
    "britecore_sdk.validators.address_validator",
]


def _import_fresh_package(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Import the package root after clearing selected cached modules.

    When ``britecore_sdk.api.api_calls`` is evicted from *sys.modules*
    and then reimported, Python's import machinery also sets the
    ``api_calls`` *attribute* on the parent package object
    (``britecore_sdk.api``).  ``monkeypatch.delitem`` only restores the
    ``sys.modules`` dict entry on teardown; it does **not** touch parent-package
    attributes.  This leaves ``britecore_sdk.api.api_calls`` (accessed via
    the attribute chain by ``import ... as`` statements) pointing at the
    freshly-created module even after the monkeypatch is undone.

    We therefore use ``monkeypatch.setattr`` to snapshot the current value of
    that attribute so it is also properly restored after each test.
    """
    # Preserve parent-package attribute for britecore_sdk.api.api_calls
    # so that attribute-chain imports (``import britecore_sdk.api.api_calls
    # as X``) resolve to the original module after sys.modules is restored.
    _api_pkg = sys.modules.get("britecore_sdk.api")
    if _api_pkg is not None and hasattr(_api_pkg, "api_calls"):
        monkeypatch.setattr(_api_pkg, "api_calls", _api_pkg.api_calls)

    for module_name in _DEFERRABLE_SUBMODULES:
        monkeypatch.delitem(sys.modules, module_name, raising=False)
    return importlib.import_module("britecore_sdk")


class TestPackageRootExports:
    """Verify root exports remain available without eager submodule imports."""

    @pytest.mark.unit
    def test_root_import_is_lazy_for_convenience_exports(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Importing the root package should not eagerly import heavy submodules."""
        package = _import_fresh_package(monkeypatch)

        assert package.logger.name == "britecore_sdk"
        assert isinstance(package.logger, logging.Logger)
        assert any(
            isinstance(handler, logging.NullHandler)
            for handler in package.logger.handlers
        )
        assert callable(package.configure_logging)
        assert "britecore_sdk.api.api_calls" not in sys.modules
        assert "britecore_sdk.models" not in sys.modules
        assert "britecore_sdk.validators" not in sys.modules

    @pytest.mark.unit
    def test_root_exports_resolve_on_first_access(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Lazy exports should import and cache their backing modules on demand."""
        package = _import_fresh_package(monkeypatch)

        assert package.PhoneValidator.__name__ == "PhoneValidator"
        assert "britecore_sdk.validators" in sys.modules

        assert package.BritecoreContact.__name__ == "BritecoreContact"
        assert "britecore_sdk.models" in sys.modules

        assert callable(package.get_api_client)
        assert "britecore_sdk.api.api_calls" in sys.modules

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
            "configure_logging",
            "__version__",
        }

        assert expected_exports.issubset(set(package.__all__))
        assert expected_exports.issubset(set(dir(package)))
