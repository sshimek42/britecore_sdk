"""Unit tests for policy helper utilities."""

import json

import pytest

from britecore_sdk.utils import policy_helpers


class _ResponseWithData:
    def __init__(self, payload: bytes) -> None:
        self.data = payload


class _ClientStub:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def do_request(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


@pytest.mark.unit
def test_get_policies_returns_decoded_payload_and_forwards_kwargs(monkeypatch):
    expected = {"success": True, "data": [{"policy_id": "P-123"}]}
    client = _ClientStub(_ResponseWithData(json.dumps(expected).encode("utf-8")))
    monkeypatch.setattr(policy_helpers, "api_client", client)

    result = policy_helpers.get_policies(timeout=5, headers={"X-Test": "1"})

    assert result == expected
    assert client.calls == [
        {
            "path": "/api/v2/policies/get_policies",
            "timeout": 5,
            "headers": {"X-Test": "1"},
        }
    ]


@pytest.mark.unit
def test_get_policies_raises_runtime_error_when_response_is_none(monkeypatch):
    client = _ClientStub(None)
    monkeypatch.setattr(policy_helpers, "api_client", client)

    with pytest.raises(RuntimeError, match="No response from get_policies API"):
        policy_helpers.get_policies()


@pytest.mark.unit
def test_get_policies_raises_runtime_error_when_response_missing_data(monkeypatch):
    client = _ClientStub(object())
    monkeypatch.setattr(policy_helpers, "api_client", client)

    with pytest.raises(RuntimeError, match="No response from get_policies API"):
        policy_helpers.get_policies()


@pytest.mark.unit
def test_get_policies_raises_json_decode_error_on_invalid_payload(monkeypatch):
    client = _ClientStub(_ResponseWithData(b"{not-json"))
    monkeypatch.setattr(policy_helpers, "api_client", client)

    with pytest.raises(json.JSONDecodeError):
        policy_helpers.get_policies()


@pytest.mark.unit
def test_get_policies_raises_unicode_decode_error_on_non_utf8_payload(monkeypatch):
    client = _ClientStub(_ResponseWithData(b"\xff\xfe\xfa"))
    monkeypatch.setattr(policy_helpers, "api_client", client)

    with pytest.raises(UnicodeDecodeError):
        policy_helpers.get_policies()
