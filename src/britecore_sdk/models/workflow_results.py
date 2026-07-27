"""Typed workflow result models for batch operations."""

from typing import Any, TypedDict


class BatchItemResult(TypedDict):
    """Strict per-item result contract for batch workflow helpers."""

    index: int
    success: bool
    id: str | None
    data: dict[str, Any] | None
    error: str | None
    error_type: str | None


def to_legacy_quote_result(item: BatchItemResult) -> dict[str, Any]:
    """Convert strict batch item result to legacy quote key names."""
    return {
        "index": item["index"],
        "success": item["success"],
        "quote_id": item["id"],
        "quote_data": item["data"],
        "error": item["error"],
    }


def to_legacy_contact_result(item: BatchItemResult) -> dict[str, Any]:
    """Convert strict batch item result to legacy contact key names."""
    return {
        "index": item["index"],
        "success": item["success"],
        "contact_id": item["id"],
        "contact_data": item["data"],
        "error": item["error"],
    }


__all__ = [
    "BatchItemResult",
    "to_legacy_quote_result",
    "to_legacy_contact_result",
]
