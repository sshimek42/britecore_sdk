"""Unit tests for async staged workflow helper."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest


def _make_jobs(n=3, include_contact=True, include_quote=False, include_risk=True):
    """Build a list of sample StagedWorkflowJob dicts."""
    jobs = []
    for i in range(n):
        job = {
            "policy_payload": {
                "policy_number": f"POL-{i:03d}",
                "policy_type_id": "pt-uuid",
            },
        }
        if include_contact:
            job["contact_payload"] = {
                "name": f"Person {i}",
                "address": [{"address1": f"{i} Main St"}],
            }
        if include_quote:
            job["quote_payload"] = {"policy_type_id": "pt-uuid", "number": f"Q-{i}"}
        if include_risk:
            job["risk_payloads"] = [{"property_group_number": 1}]
        jobs.append(job)
    return jobs


class TestAsyncStagedWorkflow:
    """Tests for acreate_entities_staged_batch (async)."""

    @pytest.mark.unit
    def test_async_staged_batch_all_stages_success(self):
        """Async workflow completes successfully for all jobs and stages."""
        from britecore_sdk.api.workflows.async_staged_creation import (
            acreate_entities_staged_batch,
        )

        jobs = _make_jobs(3)

        async def _mock_contact(name, address, **kwargs):
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        async def _mock_policy(**kwargs):
            pn = kwargs.get("policy_number", "P")
            return {"revision_id": f"REV-{pn}"}, f"REV-{pn}"

        async def _mock_risk(**kwargs):
            return {"risk_id": "RK-001"}

        async def _run():
            with (
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.anew_contact",
                    new_callable=AsyncMock,
                    side_effect=_mock_contact,
                ),
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.acreate_policy",
                    new_callable=AsyncMock,
                    side_effect=_mock_policy,
                ),
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.acreate_risk",
                    new_callable=AsyncMock,
                    side_effect=_mock_risk,
                ),
            ):
                result = await acreate_entities_staged_batch(
                    jobs,
                    contact_max_concurrent=3,
                    policy_max_concurrent=3,
                    risk_max_concurrent=3,
                )

            assert result["total"] == 3
            assert result["succeeded"] == 3
            assert result["failed"] == 0
            assert result["stage_totals"]["contacts"]["succeeded"] == 3
            assert result["stage_totals"]["policies"]["succeeded"] == 3
            assert result["stage_totals"]["risks"]["succeeded"] == 3

        asyncio.run(_run())

    @pytest.mark.unit
    def test_async_staged_batch_partial_failure(self):
        """Jobs that fail a stage are excluded from subsequent stages."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.async_staged_creation import (
            acreate_entities_staged_batch,
        )

        jobs = _make_jobs(3, include_risk=False)
        call_count = {"n": 0}

        async def _mock_contact(name, address, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise BritecoreError.MissingParameter("contact fail")
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        async def _mock_policy(**kwargs):
            pn = kwargs.get("policy_number", "P")
            return {"revision_id": f"REV-{pn}"}, f"REV-{pn}"

        async def _run():
            with (
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.anew_contact",
                    new_callable=AsyncMock,
                    side_effect=_mock_contact,
                ),
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.acreate_policy",
                    new_callable=AsyncMock,
                    side_effect=_mock_policy,
                ),
            ):
                result = await acreate_entities_staged_batch(jobs, fail_fast=False)

            assert result["total"] == 3
            assert result["failed"] == 1
            assert result["succeeded"] == 2
            assert result["stage_totals"]["contacts"]["failed"] == 1
            # Failed contact job excluded from policies stage
            assert result["stage_totals"]["policies"]["total"] == 2

        asyncio.run(_run())

    @pytest.mark.unit
    def test_async_staged_batch_fail_fast(self):
        """fail_fast=True raises on first error."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.async_staged_creation import (
            acreate_entities_staged_batch,
        )

        jobs = _make_jobs(2, include_risk=False)

        async def _mock_contact(name, address, **kwargs):
            raise BritecoreError.MissingParameter("boom")

        async def _run():
            with patch(
                "britecore_sdk.api.workflows.async_staged_creation.anew_contact",
                new_callable=AsyncMock,
                side_effect=_mock_contact,
            ):
                with pytest.raises(BritecoreError.MissingParameter):
                    await acreate_entities_staged_batch(jobs, fail_fast=True)

        asyncio.run(_run())

    @pytest.mark.unit
    def test_async_staged_batch_skips_missing_stages(self):
        """Jobs without contact_payload skip the contacts stage."""
        from britecore_sdk.api.workflows.async_staged_creation import (
            acreate_entities_staged_batch,
        )

        jobs = _make_jobs(2, include_contact=False, include_risk=False)

        async def _mock_policy(**kwargs):
            pn = kwargs.get("policy_number", "P")
            return {"revision_id": f"REV-{pn}"}, f"REV-{pn}"

        async def _run():
            with patch(
                "britecore_sdk.api.workflows.async_staged_creation.acreate_policy",
                new_callable=AsyncMock,
                side_effect=_mock_policy,
            ):
                result = await acreate_entities_staged_batch(jobs)

            assert result["stage_totals"]["contacts"]["total"] == 0
            assert result["stage_totals"]["policies"]["total"] == 2
            assert result["succeeded"] == 2

        asyncio.run(_run())

    @pytest.mark.unit
    def test_async_staged_batch_invalid_inputs(self):
        """Raises MissingParameter for empty jobs list."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.async_staged_creation import (
            acreate_entities_staged_batch,
        )

        async def _run():
            with pytest.raises(BritecoreError.MissingParameter):
                await acreate_entities_staged_batch([])

        asyncio.run(_run())

    @pytest.mark.unit
    def test_async_staged_batch_passes_explicit_client(self):
        """All async staged API calls should receive the explicit client override."""
        from britecore_sdk.api.workflows.async_staged_creation import (
            acreate_entities_staged_batch,
        )

        fake_client = object()
        jobs = _make_jobs(
            1, include_contact=True, include_quote=True, include_risk=True
        )

        async def _mock_contact(name, address, **kwargs):
            assert kwargs["client"] is fake_client
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        async def _mock_quote(payload, **kwargs):
            assert kwargs["client"] is fake_client
            return {"id": payload["number"]}, payload["number"]

        async def _mock_policy(**kwargs):
            assert kwargs["client"] is fake_client
            return {"revision_id": "REV-1"}, "REV-1"

        async def _mock_risk(**kwargs):
            assert kwargs["client"] is fake_client
            return {"risk_id": "RK-1"}

        async def _run():
            with (
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.anew_contact",
                    new_callable=AsyncMock,
                    side_effect=_mock_contact,
                ),
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.acreate_full_quote",
                    new_callable=AsyncMock,
                    side_effect=_mock_quote,
                ),
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.acreate_policy",
                    new_callable=AsyncMock,
                    side_effect=_mock_policy,
                ),
                patch(
                    "britecore_sdk.api.workflows.async_staged_creation.acreate_risk",
                    new_callable=AsyncMock,
                    side_effect=_mock_risk,
                ),
            ):
                result = await acreate_entities_staged_batch(jobs, client=fake_client)

            assert result["succeeded"] == 1

        asyncio.run(_run())
