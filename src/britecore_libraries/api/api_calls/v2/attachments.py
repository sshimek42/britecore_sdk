"""BriteCore v2 Attachments API endpoint wrappers.

Provides:
    create_folder_in_user_folder        -- Create a folder inside a user folder.
    delete_photo                        -- Delete an attachment photo by file ID.
    get_attachments_file_list           -- Retrieve a paginated file list for a reference.
    get_file_metadata                   -- Retrieve metadata for a specific file.
    get_resource_photos                 -- Retrieve photos for a specific resource.
    move_user_file                      -- Move a file to a different folder.
    remove_attachments                  -- Remove multiple attachments by ID.
    rename_user_file                    -- Rename an existing user file.
    retrieve_attachments                -- Retrieve attachments for a reference, paginated.
    upload_attachment_to_user_folder    -- Upload a file to a specific user folder.
    upload_attachment_unified           -- Upload a file using the unified upload endpoint.
"""
from logging import Logger
from typing import Any, Optional, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: Optional[dict[str, Any]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send an attachments request and normalize the response."""
    LOGGER.debug("Calling attachments endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def create_folder_in_user_folder(
    folder_name: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    reference_id: Optional[str] = None,
    reference_type: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a new folder inside a user folder.

    Parameters
    ----------
    folder_name : str, optional
        Name of the new folder.
    parent_folder_id : str, optional
        ID of the parent folder.
    reference_id : str, optional
        ID of the associated resource (e.g. policy ID).
    reference_type : str, optional
        Type of the associated resource (e.g. ``"policy"``).
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/attachments/create_folder_in_user_folder",
        _build_payload(
            folder_name=folder_name,
            parent_folder_id=parent_folder_id,
            reference_id=reference_id,
            reference_type=reference_type,
        ),
        **kwargs,
    )


def delete_photo(
    file_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete an attachment photo by file ID.

    Parameters
    ----------
    file_id : str, optional
        UUID of the file to delete.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/attachments/delete_photo",
        _build_payload(file_id=file_id),
        **kwargs,
    )


def get_attachments_file_list(
    ascending: Optional[bool] = None,
    folder_id: Optional[str] = None,
    include_forms: Optional[bool] = None,
    order_by: Optional[str] = None,
    page: Optional[int] = None,
    reference_id: Optional[str] = None,
    reference_type: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a paginated list of attachment files for a reference.

    Parameters
    ----------
    ascending : bool, optional
        Sort direction; ``True`` for ascending.
    folder_id : str, optional
        Filter by folder UUID.
    include_forms : bool, optional
        Whether to include form files in results.
    order_by : str, optional
        Field name to sort by.
    page : int, optional
        Page number (1-based).
    reference_id : str, optional
        ID of the associated resource.
    reference_type : str, optional
        Type of the associated resource.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the file list.
    """
    return _post(
        "/api/v2/attachments/get_attachments_file_list",
        _build_payload(
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
    file_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve metadata for a specific file.

    Parameters
    ----------
    file_id : str, optional
        UUID of the file whose metadata to retrieve.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing file metadata.
    """
    return _post(
        "/api/v2/attachments/get_file_metadata",
        _build_payload(file_id=file_id),
        **kwargs,
    )


def get_resource_photos(
    reference_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve photos associated with a specific resource.

    Parameters
    ----------
    reference_id : str, optional
        ID of the resource whose photos to retrieve.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the resource photos.
    """
    return _post(
        "/api/v2/attachments/get_resource_photos",
        _build_payload(reference_id=reference_id),
        **kwargs,
    )


def move_user_file(
    file_id: Optional[str] = None,
    to_folder_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Move a file to a different folder.

    Parameters
    ----------
    file_id : str, optional
        UUID of the file to move.
    to_folder_id : str, optional
        UUID of the destination folder.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/attachments/move_user_file",
        _build_payload(file_id=file_id, to_folder_id=to_folder_id),
        **kwargs,
    )


def remove_attachments(
    attachment_ids: Optional[list] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove multiple attachments by their IDs.

    Parameters
    ----------
    attachment_ids : list, optional
        List of attachment UUIDs to remove.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/attachments/remove_attachments",
        _build_payload(attachment_ids=attachment_ids),
        **kwargs,
    )


def rename_user_file(
    file_id: Optional[str] = None,
    file_name: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Rename an existing user file.

    Parameters
    ----------
    file_id : str, optional
        UUID of the file to rename.
    file_name : str, optional
        New name for the file.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response.
    """
    return _post(
        "/api/v2/attachments/rename_user_file",
        _build_payload(file_id=file_id, file_name=file_name),
        **kwargs,
    )


def retrieve_attachments(
    ascending: Optional[bool] = None,
    folder_id: Optional[str] = None,
    list_view: Optional[bool] = None,
    order_by: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    reference_id: Optional[str] = None,
    reference_type: Optional[str] = None,
    search_string: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve attachments for a reference, with pagination and filtering.

    Parameters
    ----------
    ascending : bool, optional
        Sort direction; ``True`` for ascending.
    folder_id : str, optional
        Filter by folder UUID.
    list_view : bool, optional
        Return results in list-view format.
    order_by : str, optional
        Field name to sort by.
    page : int, optional
        Page number (1-based).
    page_size : int, optional
        Number of results per page.
    reference_id : str, optional
        ID of the associated resource.
    reference_type : str, optional
        Type of the associated resource.
    search_string : str, optional
        Text to search within file names or metadata.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the attachment list.
    """
    return _post(
        "/api/v2/attachments/retrieve_attachments",
        _build_payload(
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
    file_data_base64: Optional[str] = None,
    file_name: Optional[str] = None,
    file_type: Optional[str] = None,
    folder_id: Optional[str] = None,
    reference_id: Optional[str] = None,
    reference_type: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a Base64-encoded file to a specific user folder.

    Parameters
    ----------
    file_data_base64 : str, optional
        Base64-encoded file contents.
    file_name : str, optional
        Name to give the uploaded file.
    file_type : str, optional
        MIME type or file type identifier.
    folder_id : str, optional
        Target folder UUID.
    reference_id : str, optional
        ID of the associated resource.
    reference_type : str, optional
        Type of the associated resource.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the new file details.
    """
    return _post(
        "/api/v2/attachments/upload_attachment_to_user_folder",
        _build_payload(
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
    file_data_base64: Optional[str] = None,
    file_name: Optional[str] = None,
    file_type: Optional[str] = None,
    folder_id: Optional[str] = None,
    reference_id: Optional[str] = None,
    reference_type: Optional[str] = None,
    revision_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a file using the unified attachment upload endpoint.

    Parameters
    ----------
    file_data_base64 : str, optional
        Base64-encoded file contents.
    file_name : str, optional
        Name to give the uploaded file.
    file_type : str, optional
        MIME type or file type identifier.
    folder_id : str, optional
        Target folder UUID.
    reference_id : str, optional
        ID of the associated resource.
    reference_type : str, optional
        Type of the associated resource.
    revision_id : str, optional
        Policy revision UUID to associate with the upload.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the new file details.
    """
    return _post(
        "/api/v2/attachments/upload_attachment_unified",
        _build_payload(
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
