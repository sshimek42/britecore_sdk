"""Regression tests verifying SDK endpoint wrappers route to the correct API paths.

**This file is auto-generated.** Do not edit manually.
Re-generate with::

    python generate_probe_regression_tests.py

Source: post_probe_report.json (generated 2026-07-17T20:21:30.387404+00:00)
Endpoints covered: 0 (0 genuine_success, 0 informative_error)
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

_ENDPOINTS: list[tuple[str, str, str, str, str]] = []

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
    # positional param so that "not empty" guards in wrappers don't short-circuit
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
        # Patch the module-level name so the wrapper's call is intercepted.
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
        actual_path: str | None = (
            call_args.args[0] if call_args.args else call_args.kwargs.get("path")
        )
    else:
        # Wrapper calls API_CLIENT.do_request directly.
        mock_client = Mock()
        mock_client.do_request.return_value = Mock(
            status=200,
            headers={},
            data=b'{"success": true, "data": {}}',
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
