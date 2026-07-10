"""Guardrail tests for API path alignment with the canonical current API spec."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
API_CALLS_ROOT = REPO_ROOT / "src" / "britecore_sdk" / "api" / "api_calls"
SPEC_PATH = REPO_ROOT / "api_specs" / "current" / "britecore.json"

# Baseline known contract drift between wrappers and api_specs/current/britecore.json.
# Keep this list minimal and remove entries when spec/wrapper paths converge.
KNOWN_SPEC_GAPS: set[str] = {
    "/api/v2/lines/list_policy_types",
    "/api/v2/policies/new_mortgagee",
    "/api/v2/policies/new_revision_contact",
    "/api/v2/policies/retrieve_policy_snapshot",
    "/api/v2/policies/store_mortgagee",
    "/api/v2/policies/update_revision_contact",
    "/api/v2/quotes/create_full_quote",
    "/api/v2/quotes/get_quote",
    "/api/v2/reports/retrieve_report",
    "/api/v2/utils/get_available_function_names",
}


def _extract_path_literals(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    paths: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # Positional string literals, e.g. _post("/api/v2/...", ...)
        for arg in node.args:
            if (
                isinstance(arg, ast.Constant)
                and isinstance(arg.value, str)
                and arg.value.startswith("/api/")
            ):
                paths.add(arg.value)

        # Keyword literal for path=..., e.g. do_request(path="/api/v2/...", ...)
        for kw in node.keywords:
            if kw.arg != "path":
                continue
            if (
                isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
                and kw.value.value.startswith("/api/")
            ):
                paths.add(kw.value.value)

    return paths


def _wrapper_files() -> list[Path]:
    return sorted(
        file_path
        for file_path in API_CALLS_ROOT.rglob("*.py")
        if file_path.name != "__init__.py"
    )


def _all_wrapper_paths() -> set[str]:
    paths: set[str] = set()
    for file_path in _wrapper_files():
        paths.update(_extract_path_literals(file_path))
    return paths


def _spec_paths() -> set[str]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    return set(payload.get("paths", {}).keys())


def _format_path_list(paths: list[str]) -> str:
    return "\n".join(f"- {path}" for path in paths)


def _filter_paths_for_scope(paths: set[str], scope: str) -> list[str] | None:
    normalized = scope.strip().lower()
    if normalized in {"1", "all"}:
        return sorted(paths)

    if ":" in normalized:
        version, domain = normalized.split(":", 1)
        if version in {"v1", "v2"} and domain:
            prefix = f"/api/{version}/{domain}/"
            return sorted(path for path in paths if path.startswith(prefix))
        return None

    if normalized in {"v1", "v2"}:
        prefix = f"/api/{normalized}/"
        return sorted(path for path in paths if path.startswith(prefix))

    return None


@pytest.mark.unit
def test_wrapper_paths_exist_in_api_spec() -> None:
    """Ensure wrapper endpoint paths are present in the checked-in API specification."""
    wrapper_paths = _all_wrapper_paths()
    spec_paths = _spec_paths()

    missing = sorted(wrapper_paths - spec_paths - KNOWN_SPEC_GAPS)

    assert not missing, (
        "Wrapper endpoints not found in api_specs/current/britecore.json:\n"
        + _format_path_list(missing)
        + "\n\nIf intentional, add path(s) to KNOWN_SPEC_GAPS in tests/unit/test_api_spec_alignment.py."
    )


@pytest.mark.unit
def test_spec_paths_have_wrappers_report_only() -> None:
    """Report spec endpoints that do not yet have wrappers.

    By default this test is non-blocking and always passes. Set
    BRITECORE_STRICT_SPEC_COVERAGE=1 to enforce wrapper coverage.
    """
    wrapper_paths = _all_wrapper_paths()
    spec_paths = _spec_paths()
    uncovered = sorted(spec_paths - wrapper_paths)

    strict_raw = os.getenv("BRITECORE_STRICT_SPEC_COVERAGE", "").strip()
    scopes = [scope.strip() for scope in strict_raw.split(",") if scope.strip()]
    if not scopes:
        assert True
        return

    for scope in scopes:
        scoped_uncovered = _filter_paths_for_scope(set(uncovered), scope)
        assert scoped_uncovered is not None, (
            "Invalid BRITECORE_STRICT_SPEC_COVERAGE scope: "
            f"'{scope}'. Use one of: 1, all, v1, v2, v1:<domain>, v2:<domain>."
        )
        if scope in {"1", "all"}:
            coverage_message = (
                "Spec endpoints without wrapper implementations:\n"
                + _format_path_list(scoped_uncovered)
            )
            assert not scoped_uncovered, coverage_message
            continue

        coverage_message = (
            f"Spec endpoints without wrapper implementations for scope '{scope}':\n"
            + _format_path_list(scoped_uncovered)
        )
        assert not scoped_uncovered, coverage_message

    assert True
