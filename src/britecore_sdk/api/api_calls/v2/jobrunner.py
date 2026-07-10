"""BriteCore v2 Jobrunner API endpoint wrappers."""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


def list_processes(
    status: str | None = None,
    per_page: int | None = None,
    page: int | None = None,
    job_name: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List jobrunner processes with optional filters and pagination."""
    return post(
        "/api/v2/jobrunner/list_processes",
        build_payload(
            status=status,
            per_page=per_page,
            page=page,
            job_name=job_name,
        ),
        **kwargs,
    )


def relaunch_process(
    job_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Relaunch a jobrunner process by ``job_id``."""
    return post(
        "/api/v2/jobrunner/relaunch_process",
        build_payload(job_id=job_id),
        **kwargs,
    )


__all__ = [
    "list_processes",
    "relaunch_process",
]
