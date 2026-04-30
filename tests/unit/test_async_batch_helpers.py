"""Unit tests for async batch creation helpers (contacts, policies, risks)."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest


class TestAsyncContactsBatchEndpoints:
    """Tests for acreate_contacts_batch helper."""

    @pytest.mark.unit
    def test_acreate_contacts_batch_success(self):
        """Async batch helper returns ordered results for all contact payloads."""
        from britecore_sdk.api.workflows import async_batch_contacts

        payloads = [
            {"name": "Alice", "address": [{"address1": "1 A St"}]},
            {"name": "Bob", "address": [{"address1": "2 B St"}]},
        ]

        async def _mock_new_contact(name, address, **kwargs):
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        async def _run():
            with patch.object(
                async_batch_contacts,
                "anew_contact",
                new_callable=AsyncMock,
                side_effect=_mock_new_contact,
            ):
                result = await async_batch_contacts.acreate_contacts_batch(
                    payloads, max_concurrent=2
                )
            assert result["total"] == 2
            assert result["succeeded"] == 2
            assert result["failed"] == 0
            cids = sorted([item["contact_id"] for item in result["results"]])
            assert cids == ["CID-Alice", "CID-Bob"]

        asyncio.run(_run())

    @pytest.mark.unit
    def test_acreate_contacts_batch_partial_failure(self):
        """Async batch helper captures per-item errors when fail_fast disabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import async_batch_contacts

        payloads = [
            {"name": "Alice", "address": [{"address1": "1 A St"}]},
            {"name": "", "address": []},
        ]

        async def _mock_new_contact(name, address, **kwargs):
            if not name:
                raise BritecoreError.MissingParameter("name required")
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        async def _run():
            with patch.object(
                async_batch_contacts,
                "anew_contact",
                new_callable=AsyncMock,
                side_effect=_mock_new_contact,
            ):
                result = await async_batch_contacts.acreate_contacts_batch(
                    payloads, max_concurrent=2
                )
            assert result["total"] == 2
            assert result["succeeded"] == 1
            assert result["failed"] == 1

        asyncio.run(_run())

    @pytest.mark.unit
    def test_acreate_contacts_batch_fail_fast(self):
        """Async batch helper re-raises immediately when fail_fast enabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import async_batch_contacts

        payloads = [{"name": "", "address": []}, {"name": "Bob", "address": []}]

        async def _mock_new_contact(name, address, **kwargs):
            if not name:
                raise BritecoreError.MissingParameter("name required")
            return {"contact_id": "CID-Bob"}, "CID-Bob"

        async def _run():
            with patch.object(
                async_batch_contacts,
                "anew_contact",
                new_callable=AsyncMock,
                side_effect=_mock_new_contact,
            ):
                with pytest.raises(BritecoreError.MissingParameter):
                    await async_batch_contacts.acreate_contacts_batch(
                        payloads, max_concurrent=1, fail_fast=True
                    )

        asyncio.run(_run())

    @pytest.mark.unit
    def test_acreate_contacts_batch_invalid_inputs(self):
        """Async batch helper validates required list and concurrent count."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.async_batch_contacts import (
            acreate_contacts_batch,
        )

        async def _run():
            with pytest.raises(BritecoreError.MissingParameter):
                await acreate_contacts_batch([])
            with pytest.raises(ValueError):
                await acreate_contacts_batch(
                    [{"name": "A", "address": []}], max_concurrent=0
                )

        asyncio.run(_run())


class TestAsyncPoliciesBatchEndpoints:
    """Tests for acreate_policies_batch helper."""

    @pytest.mark.unit
    def test_acreate_policies_batch_success(self):
        """Async batch helper returns ordered results for all policy payloads."""
        from britecore_sdk.api.workflows import async_batch_policies

        payloads = [
            {"policy_number": "POL-001", "policy_type_id": "pt"},
            {"policy_number": "POL-002", "policy_type_id": "pt"},
        ]

        async def _mock_create_policy(**kwargs):
            pn = kwargs.get("policy_number", "unknown")
            return {"policy_number": pn, "revision_id": f"REV-{pn}"}, f"REV-{pn}"

        async def _run():
            with patch.object(
                async_batch_policies,
                "acreate_policy",
                new_callable=AsyncMock,
                side_effect=_mock_create_policy,
            ):
                result = await async_batch_policies.acreate_policies_batch(
                    payloads, max_concurrent=2
                )
            assert result["total"] == 2
            assert result["succeeded"] == 2
            assert result["failed"] == 0

        asyncio.run(_run())

    @pytest.mark.unit
    def test_acreate_risks_batch_success(self):
        """Async batch helper returns ordered results for all risk payloads."""
        from britecore_sdk.api.workflows import async_batch_policies

        payloads = [
            {"revision_id": "REV-001"},
            {"revision_id": "REV-002"},
        ]

        async def _mock_create_risk(**kwargs):
            rid = kwargs.get("revision_id")
            return {"risk_id": f"RISK-{rid}"}

        async def _run():
            with patch.object(
                async_batch_policies,
                "acreate_risk",
                new_callable=AsyncMock,
                side_effect=_mock_create_risk,
            ):
                result = await async_batch_policies.acreate_risks_batch(
                    payloads, max_concurrent=2
                )
            assert result["total"] == 2
            assert result["succeeded"] == 2
            assert result["failed"] == 0

        asyncio.run(_run())
