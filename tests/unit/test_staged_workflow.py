"""Unit tests for sync staged workflow helper."""

from unittest.mock import patch

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


class TestStagedWorkflowSync:
    """Tests for create_entities_staged_batch (sync)."""

    @pytest.mark.unit
    def test_staged_batch_all_stages_success(self):
        """All stages complete successfully for all jobs."""
        from britecore_sdk.api.workflows.staged_creation import (
            create_entities_staged_batch,
        )

        jobs = _make_jobs(3)

        def _mock_contact(name, address, **kwargs):
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        def _mock_policy(**kwargs):
            pn = kwargs.get("policy_number", "P")
            return {"revision_id": f"REV-{pn}"}, f"REV-{pn}"

        def _mock_risk(**kwargs):
            return {"risk_id": "RK-001"}

        with (
            patch(
                "britecore_sdk.api.workflows.staged_creation.new_contact",
                side_effect=_mock_contact,
            ),
            patch(
                "britecore_sdk.api.workflows.staged_creation.create_policy",
                side_effect=_mock_policy,
            ),
            patch(
                "britecore_sdk.api.workflows.staged_creation.create_risk",
                side_effect=_mock_risk,
            ),
        ):
            result = create_entities_staged_batch(
                jobs,
                contact_max_workers=3,
                policy_max_workers=3,
                risk_max_workers=3,
            )

        assert result["total"] == 3
        assert result["succeeded"] == 3
        assert result["failed"] == 0
        assert result["stage_totals"]["contacts"]["succeeded"] == 3
        assert result["stage_totals"]["policies"]["succeeded"] == 3
        assert result["stage_totals"]["risks"]["succeeded"] == 3

        for item in result["results"]:
            assert item["success"] is True
            assert item["contact_id"] is not None
            assert item["revision_id"] is not None
            assert item["risk_ids"] == ["RK-001"]  # risk_id extracted from mock

    @pytest.mark.unit
    def test_staged_batch_partial_contact_failure(self):
        """Jobs whose contacts fail are excluded from subsequent stages."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.staged_creation import (
            create_entities_staged_batch,
        )

        jobs = _make_jobs(3, include_risk=False)

        call_count = {"n": 0}

        def _mock_contact(name, address, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise BritecoreError.MissingParameter("contact fail")
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        def _mock_policy(**kwargs):
            pn = kwargs.get("policy_number", "P")
            return {"revision_id": f"REV-{pn}"}, f"REV-{pn}"

        with (
            patch(
                "britecore_sdk.api.workflows.staged_creation.new_contact",
                side_effect=_mock_contact,
            ),
            patch(
                "britecore_sdk.api.workflows.staged_creation.create_policy",
                side_effect=_mock_policy,
            ),
        ):
            result = create_entities_staged_batch(jobs, fail_fast=False)

        assert result["total"] == 3
        assert result["failed"] == 1
        assert result["succeeded"] == 2
        assert result["stage_totals"]["contacts"]["failed"] == 1
        # Failed contact job should be excluded from policy stage
        assert result["stage_totals"]["policies"]["total"] == 2

        failed_items = [item for item in result["results"] if not item["success"]]
        assert len(failed_items) == 1
        assert failed_items[0]["failed_stage"] == "contacts"

    @pytest.mark.unit
    def test_staged_batch_fail_fast_raises(self):
        """fail_fast=True stops processing on the first error."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.staged_creation import (
            create_entities_staged_batch,
        )

        jobs = _make_jobs(2, include_risk=False)

        def _mock_contact(name, address, **kwargs):
            raise BritecoreError.MissingParameter("boom")

        with patch(
            "britecore_sdk.api.workflows.staged_creation.new_contact",
            side_effect=_mock_contact,
        ):
            with pytest.raises(BritecoreError.MissingParameter):
                create_entities_staged_batch(jobs, fail_fast=True)

    @pytest.mark.unit
    def test_staged_batch_skips_missing_stages(self):
        """Jobs without a contact_payload skip the contacts stage."""
        from britecore_sdk.api.workflows.staged_creation import (
            create_entities_staged_batch,
        )

        # No contact payloads
        jobs = _make_jobs(2, include_contact=False, include_risk=False)

        def _mock_policy(**kwargs):
            pn = kwargs.get("policy_number", "P")
            return {"revision_id": f"REV-{pn}"}, f"REV-{pn}"

        with patch(
            "britecore_sdk.api.workflows.staged_creation.create_policy",
            side_effect=_mock_policy,
        ):
            result = create_entities_staged_batch(jobs)

        assert result["stage_totals"]["contacts"]["total"] == 0
        assert result["stage_totals"]["policies"]["total"] == 2
        assert result["succeeded"] == 2

    @pytest.mark.unit
    def test_staged_batch_invalid_inputs(self):
        """Batch helper raises on missing or empty jobs list."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.staged_creation import (
            create_entities_staged_batch,
        )

        with pytest.raises(BritecoreError.MissingParameter):
            create_entities_staged_batch([])

        with pytest.raises(BritecoreError.MissingParameter):
            create_entities_staged_batch(None)  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_staged_batch_risks_injected_revision_id(self):
        """revision_id from policy stage is injected into risk payloads."""
        from britecore_sdk.api.workflows.staged_creation import (
            create_entities_staged_batch,
        )

        jobs = [
            {
                "policy_payload": {"policy_number": "POL-X", "policy_type_id": "pt"},
                "risk_payloads": [{"property_group_number": 1}],
            }
        ]

        captured_risk_kwargs: list[dict] = []

        def _mock_policy(**kwargs):
            return {"revision_id": "REV-AUTO"}, "REV-AUTO"

        def _mock_risk(**kwargs):
            captured_risk_kwargs.append(dict(kwargs))
            return {"risk_id": "RK-AUTO"}

        with (
            patch(
                "britecore_sdk.api.workflows.staged_creation.create_policy",
                side_effect=_mock_policy,
            ),
            patch(
                "britecore_sdk.api.workflows.staged_creation.create_risk",
                side_effect=_mock_risk,
            ),
        ):
            result = create_entities_staged_batch(jobs)

        assert result["succeeded"] == 1
        assert captured_risk_kwargs[0]["revision_id"] == "REV-AUTO"
