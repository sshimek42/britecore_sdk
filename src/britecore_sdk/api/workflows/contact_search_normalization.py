"""Helpers for normalizing contact-search response envelopes."""

from typing import Any


def normalize_contact_search_results(payload: Any) -> list[dict[str, Any]]:
    """Normalize common contact-search response shapes to ``list[dict]``.

    Supported shapes include:
    - raw list payloads
    - ``{"data": [...]}``
    - ``{"data": {"results": [...]}}``
    - ``{"results": [...]}``
    - ``{"contacts": [...]}``
    """
    if payload is None:
        return []

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    direct_candidates = (
        payload.get("data"),
        payload.get("results"),
        payload.get("contacts"),
    )
    for candidate in direct_candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]

    data = payload.get("data")
    if isinstance(data, dict):
        nested_candidates = (
            data.get("results"),
            data.get("contacts"),
            data.get("items"),
        )
        for candidate in nested_candidates:
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]

    return []


__all__ = ["normalize_contact_search_results"]
