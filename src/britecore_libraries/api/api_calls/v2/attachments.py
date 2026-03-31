"""BriteCore attachments API stubs (generated from britecore_api.json).
This module intentionally contains placeholders for API calls that are not yet
implemented in the SDK. Use these stubs for discovery and planning; concrete
request wrappers will be added in a future implementation phase.
"""
from typing import Any, Final
# NOTE: Keys are planned wrapper function names; values are API endpoint paths.
UNIMPLEMENTED_CALLS: Final[dict[str, str]] = {
    "create_folder_in_user_folder": "/api/v2/attachments/create_folder_in_user_folder",
    "delete_photo": "/api/v2/attachments/delete_photo",
    "get_attachments_file_list": "/api/v2/attachments/get_attachments_file_list",
    "get_file_metadata": "/api/v2/attachments/get_file_metadata",
    "get_resource_photos": "/api/v2/attachments/get_resource_photos",
    "move_user_file": "/api/v2/attachments/move_user_file",
    "remove_attachments": "/api/v2/attachments/remove_attachments",
    "rename_user_file": "/api/v2/attachments/rename_user_file",
    "retrieve_attachments": "/api/v2/attachments/retrieve_attachments",
    "upload_attachment_to_user_folder": "/api/v2/attachments/upload_attachment_to_user_folder",
    "upload_attachment_unified": "/api/v2/attachments/upload_attachment_unified",
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
