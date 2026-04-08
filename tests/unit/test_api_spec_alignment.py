"""Guardrail tests for API path alignment with the canonical current API spec."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
API_CALLS_ROOT = REPO_ROOT / "src" / "britecore_libraries" / "api" / "api_calls"
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

    strict_mode = os.getenv("BRITECORE_STRICT_SPEC_COVERAGE", "").strip() == "1"
    if strict_mode:
        assert (
            not uncovered
        ), "Spec endpoints without wrapper implementations:\n" + _format_path_list(
            uncovered
        )

    assert True
