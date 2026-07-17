"""
Generate pytest regression tests from post_probe_report.json.

Each probe-confirmed endpoint (genuine_success or informative_error) becomes a
parametrized routing test that verifies the SDK wrapper calls do_request with the
correct API path.  Re-run this script after a new probe run to refresh the suite.

Usage::

    python generate_probe_regression_tests.py              # default paths
    python generate_probe_regression_tests.py \\
        --report post_probe_report.json \\
        --output tests/unit/test_probe_endpoint_regression.py

The generated file is committed to source control and run as part of the normal
unit-test suite (no live API required).
"""

from __future__ import annotations

import argparse
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT = REPO_ROOT / "post_probe_report.json"
DEFAULT_OUTPUT = REPO_ROOT / "tests" / "unit" / "test_probe_endpoint_regression.py"

# Outcomes that confirm an endpoint is real and reachable
_VALID_OUTCOMES = {"genuine_success", "informative_error"}

# Map API version prefix -> Python package path segment
_VERSION_MAP = {
    "v1": "britecore_sdk.api.api_calls.v1",
    "v2": "britecore_sdk.api.api_calls.v2",
}

# Source root for inspecting module files
_SRC_ROOT = REPO_ROOT / "src"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _path_to_module_and_func(api_path: str) -> tuple[str, str] | None:
    """Derive (module_dotpath, func_name) from an API path like /api/v2/foo/bar_baz.

    Returns None if the path cannot be mapped to a known package.
    """
    parts = api_path.strip("/").split("/")
    # Expected: api / <version> / <module_segment> / <func_name>
    if len(parts) < 4:
        return None
    version = parts[1]  # "v1" or "v2"
    module_segment = parts[2]  # e.g. "accounting"
    func_name = parts[3]  # e.g. "set_return_premium_to_export"

    pkg = _VERSION_MAP.get(version)
    if pkg is None:
        return None

    # v1 API paths may use camelCase (e.g. sendPrintHawkEmail) while the Python
    # wrapper uses all-lowercase (e.g. sendprinthawkemail).  Normalise here so
    # the generated test can locate the function via getattr().
    if version == "v1":
        func_name = func_name.lower()

    return f"{pkg}.{module_segment}", func_name


def _detect_mock_strategy(module_dotpath: str, func_name: str) -> str:
    """Return ``"post_helper"`` if the wrapper uses the ``post()`` helper from
    ``_common``, otherwise ``"api_client"``.

    Inspects the source file to determine which patching strategy the generated
    test should use.
    """
    # Convert dotpath to filesystem path
    rel_parts = module_dotpath.replace("britecore_sdk.", "").split(".")
    # britecore_sdk.api.api_calls.v2.accounting -> src/britecore_sdk/api/api_calls/v2/accounting.py
    src_path = _SRC_ROOT / "britecore_sdk" / Path(*rel_parts).with_suffix(".py")
    if not src_path.exists():
        return "api_client"  # default

    content = src_path.read_text(encoding="utf-8")
    idx = content.find(f"def {func_name}(")
    if idx == -1:
        return "api_client"

    # Look at 400 chars of the function body for a bare post( call
    snippet = content[idx : idx + 400]
    # A bare `post(` call (not `API_CLIENT.post` or `_build_payload`) means
    # the function delegates to the _common.post() helper.
    import re
    if re.search(r"\bpost\(", snippet):
        return "post_helper"
    return "api_client"


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

_FILE_HEADER = '''\
"""Regression tests verifying SDK endpoint wrappers route to the correct API paths.

**This file is auto-generated.** Do not edit manually.
Re-generate with::

    python generate_probe_regression_tests.py

Source: post_probe_report.json (generated {generated_at})
Endpoints covered: {total} ({genuine_success} genuine_success, {informative_error} informative_error)
"""

from __future__ import annotations

import importlib
import inspect
from unittest.mock import Mock, patch

import pytest


# ---------------------------------------------------------------------------
# Parametrize data
# (api_path, module_dotpath, func_name, expected_outcome, mock_strategy)
#
# mock_strategy values:
#   "api_client"   - wrapper calls API_CLIENT.do_request directly
#   "post_helper"  - wrapper delegates to the post() helper from _common
# ---------------------------------------------------------------------------

_ENDPOINTS: list[tuple[str, str, str, str, str]] = [
'''

_ENDPOINT_ENTRY = "    ({path!r}, {module!r}, {func!r}, {outcome!r}, {strategy!r}),\n"

_FILE_FOOTER = '''\
]

_TEST_IDS = [f"{mod.rsplit('.', 1)[-1]}.{fn}" for _, mod, fn, _, _ in _ENDPOINTS]


@pytest.mark.unit
@pytest.mark.parametrize(
    "api_path,module_path,func_name,expected_outcome,mock_strategy",
    _ENDPOINTS,
    ids=_TEST_IDS,
)
def test_probe_endpoint_routes_to_correct_path(
    api_path: str,
    module_path: str,
    func_name: str,
    expected_outcome: str,
    mock_strategy: str,
) -> None:
    """Wrapper for *api_path* must exist and call the transport layer with the correct path.

    This test:

    * Imports the wrapper module dynamically.
    * Verifies the expected function is present.
    * Mocks the transport layer (``API_CLIENT`` or the ``post()`` helper) so no
      network call is made.
    * Passes ``None`` placeholders for any required positional parameters.
    * Asserts that the transport was invoked with ``path=api_path``.

    Failures indicate that the wrapper was deleted, renamed, or rewired to the
    wrong API path — all of which would be silent regressions without this check.
    The ``expected_outcome`` field documents whether the real endpoint succeeds
    with an empty payload (``genuine_success``) or requires arguments
    (``informative_error``); it is not asserted here but preserved for reference.
    """
    module = importlib.import_module(module_path)
    func = getattr(module, func_name, None)
    assert func is not None, (
        f"{module_path} has no attribute {func_name!r} — "
        "was the wrapper renamed or removed?"
    )

    # Build minimal call kwargs: pass a non-empty sentinel for every required
    # positional param so that "not empty" guards in wrappers don\'t short-circuit
    # before reaching the transport call.
    sig = inspect.signature(func)
    call_kwargs: dict[str, object] = {}
    for name, param in sig.parameters.items():
        if param.kind in (
            inspect.Parameter.VAR_KEYWORD,
            inspect.Parameter.VAR_POSITIONAL,
        ):
            continue
        if param.default is inspect.Parameter.empty:
            call_kwargs[name] = "__probe__"

    if mock_strategy == "post_helper":
        # Wrapper delegates to the post() helper imported from _common.
        # Patch the module-level name so the wrapper\'s call is intercepted.
        mock_post = Mock(return_value={"success": True, "data": {}})
        with patch(f"{module_path}.post", mock_post):
            try:
                func(**call_kwargs)
            except Exception:
                pass

        assert mock_post.called, (
            f"{module_path}.{func_name} did not call post() — "
            "the wrapper may be broken or the mock_strategy is wrong."
        )
        call_args = mock_post.call_args
        actual_path: str | None = call_args.args[0] if call_args.args else call_args.kwargs.get("path")
    else:
        # Wrapper calls API_CLIENT.do_request directly.
        mock_client = Mock()
        mock_client.do_request.return_value = Mock(
            status=200,
            headers={},
            data=b\'{"success": true, "data": {}}\',
        )
        mock_client.process_result.return_value = {"success": True, "data": {}}

        with patch(f"{module_path}.API_CLIENT", mock_client):
            try:
                func(**call_kwargs)
            except Exception:
                pass

        assert mock_client.do_request.called, (
            f"{module_path}.{func_name} did not call API_CLIENT.do_request — "
            "the wrapper may be broken or not using API_CLIENT."
        )
        call_args = mock_client.do_request.call_args
        actual_path = call_args.kwargs.get("path")
        if actual_path is None and call_args.args:
            actual_path = call_args.args[0]

    assert actual_path == api_path, (
        f"{module_path}.{func_name} called transport with path={actual_path!r}, "
        f"expected {api_path!r}"
    )
'''


def _generate(report_path: Path, output_path: Path) -> None:
    with report_path.open(encoding="utf-8") as fh:
        report = json.load(fh)

    results = report.get("results", [])
    generated_at = report.get("generated_at_utc", datetime.now(tz=timezone.utc).isoformat())

    entries: list[tuple[str, str, str, str, str]] = []
    skipped: list[str] = []

    for result in results:
        outcome = result.get("outcome", "")
        if outcome not in _VALID_OUTCOMES:
            continue
        api_path: str = result["path"]
        mapping = _path_to_module_and_func(api_path)
        if mapping is None:
            skipped.append(api_path)
            continue
        module_dotpath, func_name = mapping
        strategy = _detect_mock_strategy(module_dotpath, func_name)
        entries.append((api_path, module_dotpath, func_name, outcome, strategy))

    genuine_count = sum(1 for e in entries if e[3] == "genuine_success")
    informative_count = sum(1 for e in entries if e[3] == "informative_error")

    lines: list[str] = []
    lines.append(
        _FILE_HEADER.format(
            generated_at=generated_at,
            total=len(entries),
            genuine_success=genuine_count,
            informative_error=informative_count,
        )
    )

    for api_path, module_dotpath, func_name, outcome, strategy in sorted(entries):
        lines.append(
            _ENDPOINT_ENTRY.format(
                path=api_path,
                module=module_dotpath,
                func=func_name,
                outcome=outcome,
                strategy=strategy,
            )
        )

    lines.append(_FILE_FOOTER)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(lines), encoding="utf-8")

    print(f"Generated {len(entries)} test cases → {output_path}")
    if skipped:
        print(f"Skipped {len(skipped)} paths (could not map to a module):")
        for p in skipped:
            print(f"  {p}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate pytest regression tests from post_probe_report.json."
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        metavar="PATH",
        help="Path to the probe report JSON (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="PATH",
        help="Output test file path (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if not args.report.exists():
        print(f"ERROR: Report file not found: {args.report}")
        return 1

    _generate(args.report, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

