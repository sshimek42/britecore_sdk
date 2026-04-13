"""Unit tests for v2/policies.get_policies endpoint wrapper."""

from unittest.mock import MagicMock

import pytest

from britecore_sdk.api.api_calls.v2 import policies as policies_module


def _make_client(process_result_value):
    """Return a stub API client whose process_result returns the given value."""
    client = MagicMock()
    client.do_request.return_value = MagicMock()
    client.json_dict_builder.side_effect = lambda d: {
        k: v for k, v in d.items() if v is not None and k != "kwargs"
    }
    client.process_result.return_value = process_result_value
    return client


@pytest.mark.unit
def test_get_policies_calls_correct_path(monkeypatch):
    """get_policies sends a POST to /api/v2/policies/get_policies."""
    fake_client = _make_client({"policies": [], "total_pages": 0})
    monkeypatch.setattr(policies_module, "API_CLIENT", fake_client)

    policies_module.get_policies()

    fake_client.do_request.assert_called_once()
    call_kwargs = fake_client.do_request.call_args.kwargs
    assert call_kwargs["path"] == "/api/v2/policies/get_policies"


@pytest.mark.unit
def test_get_policies_returns_process_result(monkeypatch):
    """get_policies returns whatever process_result() returns."""
    expected = {"policies": [{"policyNumber": "POL-1"}], "total_pages": 1}
    fake_client = _make_client(expected)
    monkeypatch.setattr(policies_module, "API_CLIENT", fake_client)

    result = policies_module.get_policies()

    assert result == expected


@pytest.mark.unit
def test_get_policies_passes_json_body_from_kwargs(monkeypatch):
    """get_policies includes non-None filter params in the request body."""
    fake_client = _make_client({})
    monkeypatch.setattr(policies_module, "API_CLIENT", fake_client)

    policies_module.get_policies(page_number=2, page_size=25)

    call_kwargs = fake_client.do_request.call_args.kwargs
    sent_json = call_kwargs.get("json", {})
    assert sent_json.get("page_number") == 2
    assert sent_json.get("page_size") == 25


@pytest.mark.unit
def test_get_policies_omits_none_params(monkeypatch):
    """get_policies does not include None-valued optional params in the body."""
    fake_client = _make_client({})
    monkeypatch.setattr(policies_module, "API_CLIENT", fake_client)

    policies_module.get_policies(contact_id=None, page_number=1)

    call_kwargs = fake_client.do_request.call_args.kwargs
    sent_json = call_kwargs.get("json", {})
    assert "contact_id" not in sent_json
    assert sent_json.get("page_number") == 1


@pytest.mark.unit
def test_get_policies_forwards_request_parameters(monkeypatch):
    """Extra RequestParameters kwargs (e.g. timeout) are forwarded to do_request."""
    from urllib3 import Timeout

    fake_client = _make_client({})
    monkeypatch.setattr(policies_module, "API_CLIENT", fake_client)

    t = Timeout(connect=5, read=30)
    policies_module.get_policies(request_timeout=t)

    call_kwargs = fake_client.do_request.call_args.kwargs
    assert call_kwargs.get("request_timeout") == t
