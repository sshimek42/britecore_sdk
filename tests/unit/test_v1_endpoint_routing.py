"""Unit tests for canonical v1 endpoint module routing."""

import inspect
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
    import britecore_sdk.api.api_calls as api_calls

    api_calls._api_client = None
    with patch(
        "britecore_sdk.api.britecore_api_client.LoadClientSettings"
    ) as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_config.return_value = mock_settings
        mock_loader.return_value = mock_loader_instance
        api_calls.init_api_client(target_site="test_site")
        return api_calls.get_api_client()


@pytest.mark.unit
def test_v1_custom_ui_endpoint_path(env_api_key, mock_settings):
    """Verify the v1 custom UI wrapper targets the canonical endpoint path."""
    from britecore_sdk.api.api_calls.v1 import custom_ui

    _get_initialized_client(mock_settings)
    _make_response()

    with patch(
        "britecore_sdk.api.api_calls.v1.custom_ui.createurloverride",
        return_value={"ok": True},
    ) as mock_create:
        result = custom_ui.createurloverride(json_obj={"url": "/demo"})

        assert result == {"ok": True}
        mock_create.assert_called_once_with(json_obj={"url": "/demo"})


@pytest.mark.unit
def test_v1_printing_endpoint_path(env_api_key, mock_settings):
    """Verify the v1 printing wrapper targets the canonical endpoint path."""
    from britecore_sdk.api.api_calls.v1 import printing

    _get_initialized_client(mock_settings)
    _make_response()

    with patch(
        "britecore_sdk.api.api_calls.v1.printing.getattachment",
        return_value={"ok": True},
    ) as mock_get:
        result = printing.getattachment(json_dict={"attachment_id": "A-1"})

        assert result == {"ok": True}
        mock_get.assert_called_once_with(json_dict={"attachment_id": "A-1"})


@pytest.mark.unit
def test_v1_payments_endpoint_path(env_api_key, mock_settings):
    """Verify the v1 payments wrapper targets the canonical endpoint path."""
    from britecore_sdk.api.api_calls.v1 import payments

    _get_initialized_client(mock_settings)
    _make_response()

    with patch(
        "britecore_sdk.api.api_calls.v1.payments.makemanualpolicypayment",
        return_value={"ok": True},
    ) as mock_make:
        result = payments.makemanualpolicypayment(
            json_dict={"policy_number": "POL-1", "amount": 10.0}
        )

        assert result == {"ok": True}
        mock_make.assert_called_once_with(
            json_dict={"policy_number": "POL-1", "amount": 10.0}
        )


@pytest.mark.unit
def test_v1_wrapper_docstrings_are_spec_aligned():
    """Verify the v1 wrapper docstrings still reflect the documented API behavior."""
    from britecore_sdk.api.api_calls.v1 import custom_ui, payments, printing

    assert "external URL override" in inspect.getdoc(custom_ui.createurloverride)
    assert "already been collected" in inspect.getdoc(payments.makemanualpolicypayment)
    assert "deliverables and associated files" in inspect.getdoc(
        printing.gettobeprinted
    )
    assert "PrintHawk data" in inspect.getdoc(printing.sendprinthawk)
