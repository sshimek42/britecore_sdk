"""Unit tests for batch creation helpers in contacts, policies, and risks workflows."""

from unittest.mock import patch

import pytest


class TestContactsBatchEndpoints:
    """Tests for create_contacts_batch helper."""

    @pytest.mark.unit
    def test_create_contacts_batch_success(self):
        """Batch helper returns ordered successful results for all contact payloads."""
        from britecore_sdk.api.workflows import batch_contacts

        payloads = [
            {"name": "Alice", "address": [{"address1": "1 A St"}]},
            {"name": "Bob", "address": [{"address1": "2 B St"}]},
            {"name": "Carol", "address": [{"address1": "3 C St"}]},
        ]

        def _mock_new_contact(name, address, **kwargs):
            cid = f"CID-{name}"
            return {"contact_id": cid}, cid

        with patch.object(batch_contacts, "new_contact", side_effect=_mock_new_contact):
            result = batch_contacts.create_contacts_batch(payloads, max_workers=3)

        assert result["total"] == 3
        assert result["succeeded"] == 3
        assert result["failed"] == 0
        contact_ids = [item["contact_id"] for item in result["results"]]
        assert sorted(contact_ids) == ["CID-Alice", "CID-Bob", "CID-Carol"]

    @pytest.mark.unit
    def test_create_contacts_batch_partial_failure(self):
        """Batch helper captures per-item errors when fail_fast is disabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import batch_contacts

        payloads = [
            {"name": "Alice", "address": [{"address1": "1 A St"}]},
            {"name": "", "address": [{"address1": "2 B St"}]},
            {"name": "Carol", "address": [{"address1": "3 C St"}]},
        ]

        def _mock_new_contact(name, address, **kwargs):
            if not name:
                raise BritecoreError.MissingParameter("name is required")
            return {"contact_id": f"CID-{name}"}, f"CID-{name}"

        with patch.object(batch_contacts, "new_contact", side_effect=_mock_new_contact):
            result = batch_contacts.create_contacts_batch(payloads, max_workers=2)

        assert result["total"] == 3
        assert result["succeeded"] == 2
        assert result["failed"] == 1
        failed_item = next(i for i in result["results"] if not i["success"])
        assert "name is required" in failed_item["error"]

    @pytest.mark.unit
    def test_create_contacts_batch_fail_fast(self):
        """Batch helper re-raises immediately when fail_fast is enabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import batch_contacts

        payloads = [
            {"name": "", "address": []},
            {"name": "Bob", "address": [{"address1": "2 B St"}]},
        ]

        def _mock_new_contact(name, address, **kwargs):
            if not name:
                raise BritecoreError.MissingParameter("name is required")
            return {"contact_id": "CID-Bob"}, "CID-Bob"

        with patch.object(batch_contacts, "new_contact", side_effect=_mock_new_contact):
            with pytest.raises(BritecoreError.MissingParameter):
                batch_contacts.create_contacts_batch(payloads, max_workers=1, fail_fast=True)

    @pytest.mark.unit
    def test_create_contacts_batch_invalid_inputs(self):
        """Batch helper validates required payload list and worker count."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.batch_contacts import create_contacts_batch

        with pytest.raises(BritecoreError.MissingParameter):
            create_contacts_batch([])

        with pytest.raises(ValueError):
            create_contacts_batch(
                [{"name": "A", "address": []}], max_workers=0
            )


class TestPoliciesBatchEndpoints:
    """Tests for create_policies_batch helper."""

    @pytest.mark.unit
    def test_create_policies_batch_success(self):
        """Batch helper returns ordered successful results for all policy payloads."""
        from britecore_sdk.api.workflows import batch_policies

        payloads = [
            {"policy_number": "POL-001", "policy_type_id": "pt"},
            {"policy_number": "POL-002", "policy_type_id": "pt"},
        ]

        def _mock_create_policy(**kwargs):
            rn = kwargs.get("policy_number", "unknown")
            return {"policy_number": rn, "revision_id": f"REV-{rn}"}, f"REV-{rn}"

        with patch.object(batch_policies, "create_policy", side_effect=_mock_create_policy):
            result = batch_policies.create_policies_batch(payloads, max_workers=2)

        assert result["total"] == 2
        assert result["succeeded"] == 2
        assert result["failed"] == 0
        revision_ids = [item["revision_id"] for item in result["results"]]
        assert sorted(revision_ids) == ["REV-POL-001", "REV-POL-002"]

    @pytest.mark.unit
    def test_create_policies_batch_partial_failure(self):
        """Batch helper captures per-item errors when fail_fast is disabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import batch_policies

        payloads = [
            {"policy_number": "POL-OK", "policy_type_id": "pt"},
            {"policy_number": "", "policy_type_id": "pt"},
        ]

        def _mock_create_policy(**kwargs):
            pn = kwargs.get("policy_number", "")
            if not pn:
                raise BritecoreError.MissingParameter("policy_number required")
            return {"policy_number": pn, "revision_id": f"REV-{pn}"}, f"REV-{pn}"

        with patch.object(batch_policies, "create_policy", side_effect=_mock_create_policy):
            result = batch_policies.create_policies_batch(payloads, max_workers=2)

        assert result["total"] == 2
        assert result["succeeded"] == 1
        assert result["failed"] == 1

    @pytest.mark.unit
    def test_create_policies_batch_invalid_inputs(self):
        """Batch helper validates required list and worker count."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.batch_policies import create_policies_batch

        with pytest.raises(BritecoreError.MissingParameter):
            create_policies_batch([])

        with pytest.raises(ValueError):
            create_policies_batch(
                [{"policy_number": "P"}], max_workers=0
            )


class TestRisksBatchEndpoints:
    """Tests for create_risks_batch helper."""

    @pytest.mark.unit
    def test_create_risks_batch_success(self):
        """Batch helper returns ordered successful results for all risk payloads."""
        from britecore_sdk.api.workflows import batch_policies

        payloads = [
            {"revision_id": "REV-001"},
            {"revision_id": "REV-002"},
        ]

        def _mock_create_risk(**kwargs):
            rid = kwargs.get("revision_id", "unknown")
            return {"risk_id": f"RISK-{rid}"}

        with patch.object(batch_policies, "create_risk", side_effect=_mock_create_risk):
            result = batch_policies.create_risks_batch(payloads, max_workers=2)

        assert result["total"] == 2
        assert result["succeeded"] == 2
        assert result["failed"] == 0

    @pytest.mark.unit
    def test_create_risks_batch_partial_failure(self):
        """Batch helper captures per-item errors when fail_fast is disabled."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows import batch_policies

        payloads = [
            {"revision_id": "REV-OK"},
            {"revision_id": ""},
        ]

        def _mock_create_risk(**kwargs):
            rid = kwargs.get("revision_id", "")
            if not rid:
                raise BritecoreError.MissingParameter("revision_id required")
            return {"risk_id": f"RISK-{rid}"}

        with patch.object(batch_policies, "create_risk", side_effect=_mock_create_risk):
            result = batch_policies.create_risks_batch(payloads, max_workers=2)

        assert result["total"] == 2
        assert result["succeeded"] == 1
        assert result["failed"] == 1

    @pytest.mark.unit
    def test_create_risks_batch_invalid_inputs(self):
        """Batch helper validates required list and worker count."""
        from britecore_sdk import BritecoreError
        from britecore_sdk.api.workflows.batch_policies import create_risks_batch

        with pytest.raises(BritecoreError.MissingParameter):
            create_risks_batch([])

        with pytest.raises(ValueError):
            create_risks_batch([{"revision_id": "R"}], max_workers=0)
