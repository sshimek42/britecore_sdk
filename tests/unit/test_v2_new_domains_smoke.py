"""Smoke tests for newly added v2 domain wrappers."""

from __future__ import annotations

import inspect
from unittest.mock import Mock, patch


def _mock_api_client() -> Mock:
    client = Mock()
    client.do_request.return_value = {"raw": True}
    client.process_result.return_value = {"ok": True}
    return client


def test_jobrunner_list_processes_signature_and_request() -> None:
    from britecore_sdk.api.api_calls.v2 import jobrunner

    signature = inspect.signature(jobrunner.list_processes)
    assert "status" in signature.parameters
    assert "per_page" in signature.parameters
    assert "page" in signature.parameters
    assert "job_name" in signature.parameters

    with patch("britecore_sdk.api.api_calls.v2.jobrunner.post") as mock_post:
        mock_post.return_value = {"ok": True}
        result = jobrunner.list_processes(
            status="running",
            per_page=50,
            page=2,
            job_name="nightly_jobs",
        )

    assert result == {"ok": True}
    mock_post.assert_called_once_with(
        "/api/v2/jobrunner/list_processes",
        {
            "status": "running",
            "per_page": 50,
            "page": 2,
            "job_name": "nightly_jobs",
        },
    )


def test_background_jobs_search_smoke() -> None:
    from britecore_sdk.api.api_calls.v2 import background_jobs

    signature = inspect.signature(background_jobs.search)
    assert "kwargs" in signature.parameters

    mock_client = _mock_api_client()
    with patch(
        "britecore_sdk.api.api_calls.v2.background_jobs.API_CLIENT", mock_client
    ):
        result = background_jobs.search()

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/background_jobs/search",
        json={},
        method="POST",
    )


def test_ingestion_job_wrappers_smoke() -> None:
    from britecore_sdk.api.api_calls.v2 import ingestion_job

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.ingestion_job.API_CLIENT", mock_client):
        result = ingestion_job.list_ingestion_jobs()

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/ingestion_job/list_ingestion_jobs",
        json={},
        method="POST",
    )
