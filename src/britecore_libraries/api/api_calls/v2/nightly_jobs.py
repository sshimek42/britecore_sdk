"""BriteCore nightly_jobs API stubs (generated from britecore_api.json).
This module intentionally contains placeholders for API calls that are not yet
implemented in the SDK. Use these stubs for discovery and planning; concrete
request wrappers will be added in a future implementation phase.
"""
from typing import Any, Final
# NOTE: Keys are planned wrapper function names; values are API endpoint paths.
UNIMPLEMENTED_CALLS: Final[dict[str, str]] = {
    "process_auto_pays": "/api/v2/nightly_jobs/process_auto_pays",
    "process_cancellation_pending_or_non_renewals": "/api/v2/nightly_jobs/process_cancellation_pending_or_non_renewals",
    "process_non_pays_and_cancellations": "/api/v2/nightly_jobs/process_non_pays_and_cancellations",
    "process_renewals": "/api/v2/nightly_jobs/process_renewals",
}
def list_unimplemented_calls() -> dict[str, str]:
    """Return a copy of the unimplemented call map for this API domain."""
    return dict(UNIMPLEMENTED_CALLS)
def not_implemented_call(
    call_name: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    """Placeholder dispatcher for unimplemented calls in this module.
    Parameters:
        call_name: Planned wrapper function name from ``UNIMPLEMENTED_CALLS``.
        payload: Optional future request body payload.
    Raises:
        ValueError: If ``call_name`` is unknown.
        NotImplementedError: Always, for known stub calls.
    """
    if call_name not in UNIMPLEMENTED_CALLS:
        raise ValueError(
            f"Unknown stub call '{call_name}'. "
            f"Valid values: {', '.join(sorted(UNIMPLEMENTED_CALLS))}"
        )
    _ = payload
    raise NotImplementedError(
        f"Call '{call_name}' ({UNIMPLEMENTED_CALLS[call_name]}) is not yet implemented."
    )
__all__ = [
    "UNIMPLEMENTED_CALLS",
    "list_unimplemented_calls",
    "not_implemented_call",
]
