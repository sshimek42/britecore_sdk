"""BriteCore v2 Attachments API endpoint wrappers.

This module provides wrappers for attachment folder management, file metadata,
listing, uploads, moves, renames, and removals in the BriteCore v2
attachments API.
"""

from __future__ import annotations

from typing import Any, Unpack

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import build_payload, post

API_CLIENT: BritecoreAPIClient = api_client


def _coerce_attachment_payload(attachment: Any | None) -> Any | None:
    """Accept model instances and convert them to request-safe dict payloads."""
    if attachment is None:
        return None
    if hasattr(attachment, "to_dict") and callable(attachment.to_dict):
        return attachment.to_dict()
    return attachment


def create_folder_in_user_folder(
    folder_name: str | None = None,
    parent_folder_id: str | None = None,
    reference_id: str | None = None,
    reference_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a folder inside a user folder.

    POST /api/v2/attachments/create_folder_in_user_folder
    """
    return post(
        "/api/v2/attachments/create_folder_in_user_folder",
        build_payload(
            folder_name=folder_name,
            parent_folder_id=parent_folder_id,
            reference_id=reference_id,
            reference_type=reference_type,
        ),
        **kwargs,
    )


def delete_photo(
    file_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete an attachment photo by file identifier.

    POST /api/v2/attachments/delete_photo
    """
    return post(
        "/api/v2/attachments/delete_photo",
        build_payload(file_id=file_id),
        **kwargs,
    )


def get_attachments_file_list(
    ascending: bool | None = None,
    folder_id: str | None = None,
    include_forms: bool | None = None,
    order_by: str | None = None,
    page: int | None = None,
    reference_id: str | None = None,
    reference_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a paginated attachment file list for a reference.

    POST /api/v2/attachments/get_attachments_file_list
    """
    return post(
        "/api/v2/attachments/get_attachments_file_list",
        build_payload(
            ascending=ascending,
            folder_id=folder_id,
            include_forms=include_forms,
            order_by=order_by,
            page=page,
            reference_id=reference_id,
            reference_type=reference_type,
        ),
        **kwargs,
    )


def get_file_metadata(
    file_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve metadata for a specific file.

    POST /api/v2/attachments/get_file_metadata
    """
    return post(
        "/api/v2/attachments/get_file_metadata",
        build_payload(file_id=file_id),
        **kwargs,
    )


def get_resource_photos(
    reference_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve photos associated with a resource.

    POST /api/v2/attachments/get_resource_photos
    """
    return post(
        "/api/v2/attachments/get_resource_photos",
        build_payload(reference_id=reference_id),
        **kwargs,
    )


def move_user_file(
    file_id: str | None = None,
    to_folder_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Move a file to a different folder.

    POST /api/v2/attachments/move_user_file
    """
    return post(
        "/api/v2/attachments/move_user_file",
        build_payload(file_id=file_id, to_folder_id=to_folder_id),
        **kwargs,
    )


def remove_attachments(
    attachment_ids: list | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove attachments by identifier list.

    POST /api/v2/attachments/remove_attachments
    """
    return post(
        "/api/v2/attachments/remove_attachments",
        build_payload(attachment_ids=attachment_ids),
        **kwargs,
    )


def rename_user_file(
    file_id: str | None = None,
    file_name: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Rename an existing user file.

    POST /api/v2/attachments/rename_user_file
    """
    return post(
        "/api/v2/attachments/rename_user_file",
        build_payload(file_id=file_id, file_name=file_name),
        **kwargs,
    )


def retrieve_attachments(
    ascending: bool | None = None,
    folder_id: str | None = None,
    list_view: bool | None = None,
    order_by: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    reference_id: str | None = None,
    reference_type: str | None = None,
    search_string: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve attachments for a reference with filtering and pagination.

    POST /api/v2/attachments/retrieve_attachments
    """
    return post(
        "/api/v2/attachments/retrieve_attachments",
        build_payload(
            ascending=ascending,
            folder_id=folder_id,
            list_view=list_view,
            order_by=order_by,
            page=page,
            page_size=page_size,
            reference_id=reference_id,
            reference_type=reference_type,
            search_string=search_string,
        ),
        **kwargs,
    )


def upload_attachment_to_user_folder(
    file_data_base64: str | None = None,
    file_name: str | None = None,
    file_type: str | None = None,
    folder_id: str | None = None,
    reference_id: str | None = None,
    reference_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a file to a user folder.

    POST /api/v2/attachments/upload_attachment_to_user_folder
    """
    return post(
        "/api/v2/attachments/upload_attachment_to_user_folder",
        build_payload(
            file_data_base64=file_data_base64,
            file_name=file_name,
            file_type=file_type,
            folder_id=folder_id,
            reference_id=reference_id,
            reference_type=reference_type,
        ),
        **kwargs,
    )


def upload_attachment_unified(
    file_data_base64: str | None = None,
    file_name: str | None = None,
    file_type: str | None = None,
    folder_id: str | None = None,
    reference_id: str | None = None,
    reference_type: str | None = None,
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a file with the unified attachment endpoint.

    POST /api/v2/attachments/upload_attachment_unified
    """
    return post(
        "/api/v2/attachments/upload_attachment_unified",
        build_payload(
            file_data_base64=file_data_base64,
            file_name=file_name,
            file_type=file_type,
            folder_id=folder_id,
            reference_id=reference_id,
            reference_type=reference_type,
            revisionId=revision_id,
        ),
        **kwargs,
    )


__all__ = [
    "create_folder_in_user_folder",
    "delete_photo",
    "get_attachments_file_list",
    "get_file_metadata",
    "get_resource_photos",
    "move_user_file",
    "remove_attachments",
    "rename_user_file",
    "retrieve_attachments",
    "upload_attachment_to_user_folder",
    "upload_attachment_unified",
]

# --- Autogenerated spec wrappers ---


def edit_attachment(
    attachment: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Edit Attachment.

    POST /api/v2/attachments/edit_attachment
    """
    return post(
        "/api/v2/attachments/edit_attachment",
        build_payload(attachment=_coerce_attachment_payload(attachment)),
        **kwargs,
    )


__all__.extend(
    [
        "edit_attachment",
    ]
)
