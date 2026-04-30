"""Unit tests for batched quote creation helper in the workflows layer."""

from unittest.mock import patch

import pytest


class TestQuotesBatchEndpoints:
    """Tests for batched quote creation helper."""

    @pytest.mark.unit
    def test_create_full_quotes_batch_success(self):
        """Batch helper returns ordered successful results for all payloads."""
        from britecore_sdk.api.workflows import batch_quotes

        payloads = [
            {"number": "Q-001", "policy_type_id": "pt"},
            {"number": "Q-002", "policy_type_id": "pt"},
            {"number": "Q-003", "policy_type_id": "pt"},
        ]

        def _mock_create(payload, **kwargs):
            quote_id = payload["number"]
            return {"id": quote_id}, quote_id

        with patch.object(batch_quotes, "create_full_quote", side_effect=_mock_create):
            batch_result = batch_quotes.create_full_quotes_batch(payloads, max_workers=3)

        assert batch_result["total"] == 3
        assert batch_result["succeeded"] == 3
        assert batch_result["failed"] == 0
        assert [item["quote_id"] for item in batch_result["results"]] == [
            "Q-001",
            "Q-002",
            "Q-003",
        ]

    @pytest.mark.unit
    def test_create_full_quotes_batch_partial_failure(self):
        """Batch helper captures per-item errors when fail_fast is disabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import batch_quotes

        payloads = [
            {"number": "Q-OK-1", "policy_type_id": "pt"},
            {"number": "", "policy_type_id": "pt"},
            {"number": "Q-OK-2", "policy_type_id": "pt"},
        ]

        def _mock_create(payload, **kwargs):
            if not payload.get("number"):
                raise BritecoreError.MissingParameter("number is required")
            quote_id = payload["number"]
            return {"id": quote_id}, quote_id

        with patch.object(batch_quotes, "create_full_quote", side_effect=_mock_create):
            batch_result = batch_quotes.create_full_quotes_batch(payloads, max_workers=2)

        assert batch_result["total"] == 3
        assert batch_result["succeeded"] == 2
        assert batch_result["failed"] == 1
        assert batch_result["results"][1]["success"] is False
        assert "number is required" in str(batch_result["results"][1]["error"])

    @pytest.mark.unit
    def test_create_full_quotes_batch_fail_fast(self):
        """Batch helper re-raises immediately when fail_fast is enabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import batch_quotes

        payloads = [
            {"number": "", "policy_type_id": "pt"},
            {"number": "Q-OK", "policy_type_id": "pt"},
        ]

        def _mock_create(payload, **kwargs):
            if not payload.get("number"):
                raise BritecoreError.MissingParameter("number is required")
            quote_id = payload["number"]
            return {"id": quote_id}, quote_id

        with patch.object(batch_quotes, "create_full_quote", side_effect=_mock_create):
            with pytest.raises(BritecoreError.MissingParameter):
                batch_quotes.create_full_quotes_batch(
                    payloads,
                    max_workers=1,
                    fail_fast=True,
                )

    @pytest.mark.unit
    def test_create_full_quotes_batch_invalid_inputs(self):
        """Batch helper validates required payload list and worker count."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import batch_quotes

        with pytest.raises(BritecoreError.MissingParameter):
            batch_quotes.create_full_quotes_batch([])

        with pytest.raises(ValueError):
            batch_quotes.create_full_quotes_batch([{"number": "Q-001"}], max_workers=0)


class TestBritecoreAPIClientBatchMethod:
    """Tests that BritecoreAPIClient exposes create_full_quotes_batch as a method."""

    @pytest.mark.unit
    def test_client_method_delegates_to_workflow(self):
        """Client method delegates to the workflow batch function."""
        from unittest.mock import MagicMock, patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        client = BritecoreAPIClient.__new__(BritecoreAPIClient)
        expected = {"total": 1, "succeeded": 1, "failed": 0, "results": []}

        with patch(
            "britecore_sdk.api.workflows.batch_quotes.create_full_quotes_batch",
            return_value=expected,
        ) as mock_fn:
            result = client.create_full_quotes_batch(
                [{"number": "Q-001"}], max_workers=2
            )

        mock_fn.assert_called_once_with(
            [{"number": "Q-001"}], max_workers=2, fail_fast=False
        )
        assert result == expected
