"""Unit tests for the deprecated policy_helpers shim."""

import warnings
from unittest.mock import patch

import pytest

from britecore_sdk.utils import policy_helpers


@pytest.mark.unit
def test_get_policies_emits_deprecation_warning():
    """Calling policy_helpers.get_policies() always emits DeprecationWarning."""
    fake_result = {"policies": [], "total_pages": 0}
    with patch(
        "britecore_sdk.api.api_calls.v2.policies.get_policies",
        return_value=fake_result,
    ):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = policy_helpers.get_policies()

    assert any(
        issubclass(w.category, DeprecationWarning) for w in caught
    ), "Expected DeprecationWarning but none was raised"
    assert result == fake_result


@pytest.mark.unit
def test_get_policies_delegates_to_v2_policies():
    """Deprecated shim forwards all kwargs to v2/policies.get_policies."""
    fake_result = {"policies": [{"policyNumber": "POL-1"}], "total_pages": 1}
    with patch(
        "britecore_sdk.api.api_calls.v2.policies.get_policies",
        return_value=fake_result,
    ) as mock_v2:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = policy_helpers.get_policies(page_number=1, page_size=10)

    mock_v2.assert_called_once_with(page_number=1, page_size=10)
    assert result == fake_result


@pytest.mark.unit
def test_get_policies_warning_message_mentions_v2_path():
    """DeprecationWarning message points callers to the v2/policies module."""
    with patch(
        "britecore_sdk.api.api_calls.v2.policies.get_policies",
        return_value={},
    ):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            policy_helpers.get_policies()

    dep_warnings = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert dep_warnings, "No DeprecationWarning emitted"
    assert "v2.policies" in str(dep_warnings[0].message).lower() or (
        "api_calls" in str(dep_warnings[0].message)
    )
