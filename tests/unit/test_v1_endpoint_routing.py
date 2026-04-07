"""Unit tests for canonical v1 endpoint module routing."""

from unittest.mock import MagicMock, patch

import pytest
from urllib3 import BaseHTTPResponse


def _make_response(
    payload: bytes = b'{"success": true, "data": {"ok": true}}',
) -> MagicMock:
    response = MagicMock(spec=BaseHTTPResponse)
    response.status = 200
    response.reason = "OK"
    response.data = payload
    return response


def _get_initialized_client(mock_settings):
    import britecore_libraries.api.api_calls as api_calls

    api_calls._api_client = None
    with patch(
        "britecore_libraries.api.britecore_api_client.LoadClientSettings"
    ) as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_config.return_value = mock_settings
        mock_loader.return_value = mock_loader_instance
        return api_calls.get_api_client()


@pytest.mark.unit
def test_v1_custom_ui_endpoint_path(env_api_key, mock_settings):
    from britecore_libraries.api.api_calls.v1 import custom_ui

    client = _get_initialized_client(mock_settings)
    mock_response = _make_response()

    with patch.object(
        client, "do_request", return_value=mock_response
    ) as mock_do_request:
        with patch.object(client, "process_result", return_value={"ok": True}):
            result = custom_ui.createurloverride(json_obj={"url": "/demo"})

    assert result == {"ok": True}
    mock_do_request.assert_called_once_with(
        path="/api/v1/custom_ui/createURLOverride",
        json={"json_obj": {"url": "/demo"}},
    )


@pytest.mark.unit
def test_v1_printing_endpoint_path(env_api_key, mock_settings):
    from britecore_libraries.api.api_calls.v1 import printing

    client = _get_initialized_client(mock_settings)
    mock_response = _make_response()

    with patch.object(
        client, "do_request", return_value=mock_response
    ) as mock_do_request:
        with patch.object(client, "process_result", return_value={"ok": True}):
            result = printing.getattachment(json_dict={"attachment_id": "A-1"})

    assert result == {"ok": True}
    mock_do_request.assert_called_once_with(
        path="/api/v1/printing/getAttachment",
        json={"json_dict": {"attachment_id": "A-1"}},
    )


@pytest.mark.unit
def test_v1_payments_endpoint_path(env_api_key, mock_settings):
    from britecore_libraries.api.api_calls.v1 import payments

    client = _get_initialized_client(mock_settings)
    mock_response = _make_response()

    with patch.object(
        client, "do_request", return_value=mock_response
    ) as mock_do_request:
        with patch.object(client, "process_result", return_value={"ok": True}):
            result = payments.makemanualpolicypayment(
                json_dict={"policy_number": "POL-1", "amount": 10.0}
            )

    assert result == {"ok": True}
    mock_do_request.assert_called_once_with(
        path="/api/v1/payments/makeManualPolicyPayment",
        json={"json_dict": {"policy_number": "POL-1", "amount": 10.0}},
    )
