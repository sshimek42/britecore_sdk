"""Unit tests for async batched quote creation in the workflows layer."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest


class TestAsyncQuotesBatchEndpoints:
    """Tests for async batched quote creation helper."""

    @pytest.mark.unit
    def test_acreate_full_quotes_batch_success(self):
        """Async batch helper returns ordered successful results for all payloads."""
        from britecore_sdk.api.workflows import async_batch_quotes

        payloads = [
            {"number": "Q-001", "policy_type_id": "pt"},
            {"number": "Q-002", "policy_type_id": "pt"},
            {"number": "Q-003", "policy_type_id": "pt"},
        ]

        async def _mock_create(payload, **kwargs):
            quote_id = payload["number"]
            return {"id": quote_id}, quote_id

        async def _run_test():
            with patch.object(
                async_batch_quotes,
                "acreate_full_quote",
                new_callable=AsyncMock,
                side_effect=_mock_create,
            ):
                batch_result = await async_batch_quotes.acreate_full_quotes_batch(
                    payloads, max_concurrent=3
                )

            assert batch_result["total"] == 3
            assert batch_result["succeeded"] == 3
            assert batch_result["failed"] == 0
            assert sorted([item["quote_id"] for item in batch_result["results"]]) == [
                "Q-001",
                "Q-002",
                "Q-003",
            ]

        asyncio.run(_run_test())

    @pytest.mark.unit
    def test_acreate_full_quotes_batch_partial_failure(self):
        """Async batch helper captures per-item errors when fail_fast is disabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import async_batch_quotes

        payloads = [
            {"number": "Q-OK-1", "policy_type_id": "pt"},
            {"number": "", "policy_type_id": "pt"},
            {"number": "Q-OK-2", "policy_type_id": "pt"},
        ]

        async def _mock_create(payload, **kwargs):
            if not payload.get("number"):
                raise BritecoreError.MissingParameter("number is required")
            quote_id = payload["number"]
            return {"id": quote_id}, quote_id

        async def _run_test():
            with patch.object(
                async_batch_quotes,
                "acreate_full_quote",
                new_callable=AsyncMock,
                side_effect=_mock_create,
            ):
                batch_result = await async_batch_quotes.acreate_full_quotes_batch(
                    payloads, max_concurrent=2
                )

            assert batch_result["total"] == 3
            assert batch_result["succeeded"] == 2
            assert batch_result["failed"] == 1
            failed_item = [
                item for item in batch_result["results"] if not item["success"]
            ][0]
            assert "number is required" in failed_item["error"]

        asyncio.run(_run_test())

    @pytest.mark.unit
    def test_acreate_full_quotes_batch_fail_fast(self):
        """Async batch helper re-raises immediately when fail_fast is enabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import async_batch_quotes

        payloads = [
            {"number": "", "policy_type_id": "pt"},
            {"number": "Q-OK", "policy_type_id": "pt"},
        ]

        async def _mock_create(payload, **kwargs):
            if not payload.get("number"):
                raise BritecoreError.MissingParameter("number is required")
            quote_id = payload["number"]
            return {"id": quote_id}, quote_id

        async def _run_test():
            with patch.object(
                async_batch_quotes,
                "acreate_full_quote",
                new_callable=AsyncMock,
                side_effect=_mock_create,
            ):
                with pytest.raises(BritecoreError.MissingParameter):
                    await async_batch_quotes.acreate_full_quotes_batch(
                        payloads,
                        max_concurrent=1,
                        fail_fast=True,
                    )

        asyncio.run(_run_test())

    @pytest.mark.unit
    def test_acreate_full_quotes_batch_invalid_inputs(self):
        """Async batch helper validates required payload list and concurrent count."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import async_batch_quotes

        async def _run_test():
            with pytest.raises(BritecoreError.MissingParameter):
                await async_batch_quotes.acreate_full_quotes_batch([])

            with pytest.raises(ValueError):
                await async_batch_quotes.acreate_full_quotes_batch(
                    [{"number": "Q-001"}], max_concurrent=0
                )

        asyncio.run(_run_test())

    @pytest.mark.unit
    def test_acreate_full_quotes_batch_respects_max_concurrent(self):
        """Async batch helper respects max_concurrent semaphore."""
        from britecore_sdk.api.workflows import async_batch_quotes

        concurrent_count = 0
        max_concurrent_observed = 0

        async def _mock_create_with_tracking(payload, **kwargs):
            nonlocal concurrent_count, max_concurrent_observed
            concurrent_count += 1
            max_concurrent_observed = max(max_concurrent_observed, concurrent_count)
            # Simulate async work
            await asyncio.sleep(0.01)
            concurrent_count -= 1
            return {"id": payload["number"]}, payload["number"]

        async def _run_test():
            payloads = [{"number": f"Q-{i:03d}"} for i in range(10)]

            with patch.object(
                async_batch_quotes,
                "acreate_full_quote",
                new_callable=AsyncMock,
                side_effect=_mock_create_with_tracking,
            ):
                result = await async_batch_quotes.acreate_full_quotes_batch(
                    payloads, max_concurrent=3
                )

            assert result["succeeded"] == 10
            assert max_concurrent_observed <= 3

        asyncio.run(_run_test())


class TestAsyncBritecoreAPIClientBatchMethod:
    """Tests that AsyncBritecoreAPIClient exposes acreate_full_quotes_batch as a method."""

    @pytest.mark.unit
    def test_async_client_method_delegates_to_workflow(self):
        """Async client method delegates to the workflow batch function."""
        from unittest.mock import AsyncMock, patch

        from britecore_sdk.api.britecore_async_api_client import AsyncBritecoreAPIClient

        client = AsyncBritecoreAPIClient.__new__(AsyncBritecoreAPIClient)
        expected = {"total": 1, "succeeded": 1, "failed": 0, "results": []}

        async def _run_test():
            with patch(
                "britecore_sdk.api.workflows.async_batch_quotes.acreate_full_quotes_batch",
                new_callable=AsyncMock,
                return_value=expected,
            ) as mock_fn:
                result = await client.acreate_full_quotes_batch(
                    [{"number": "Q-001"}], max_concurrent=2
                )

            mock_fn.assert_called_once_with(
                [{"number": "Q-001"}], max_concurrent=2, fail_fast=False
            )
            assert result == expected

        asyncio.run(_run_test())
