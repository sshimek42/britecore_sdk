"""Unit tests for response helper utility normalization helpers."""

import pytest

from britecore_sdk.api.response_helpers import (
    extract_items,
    normalize_batch_results,
    normalize_pagination_envelope,
)


@pytest.mark.unit
def test_extract_items_from_standard_envelope():
    """extract_items returns list payload from canonical data envelope."""
    response = {"success": True, "data": [{"id": "1"}, {"id": "2"}]}

    assert extract_items(response) == [{"id": "1"}, {"id": "2"}]


@pytest.mark.unit
def test_extract_items_from_nested_items_key():
    """extract_items handles nested list containers under data.items."""
    response = {
        "success": True,
        "data": {
            "items": [{"id": "A"}],
            "totalCount": 1,
        },
    }

    assert extract_items(response) == [{"id": "A"}]


@pytest.mark.unit
def test_extract_items_returns_empty_on_missing_data():
    """extract_items returns empty list instead of raising for missing data payloads."""
    response = {"success": True, "message": "no data"}

    assert extract_items(response) == []


@pytest.mark.unit
def test_normalize_pagination_envelope_with_metadata():
    """Pagination helper normalizes camelCase metadata and computes next page."""
    response = {
        "success": True,
        "data": {
            "items": [{"id": "Q1"}, {"id": "Q2"}],
            "totalCount": 10,
            "page": 2,
            "pageSize": 2,
            "isLastPage": False,
        },
    }

    normalized = normalize_pagination_envelope(response)

    assert normalized["items"] == [{"id": "Q1"}, {"id": "Q2"}]
    assert normalized["total_count"] == 10
    assert normalized["page"] == 2
    assert normalized["page_size"] == 2
    assert normalized["is_last_page"] is False
    assert normalized["next_page"] == 3


@pytest.mark.unit
def test_normalize_pagination_envelope_infers_last_page_when_metadata_missing():
    """Pagination helper infers final page when returned items are fewer than page size."""
    response = {
        "data": [{"id": "Q1"}],
        "page": 4,
        "page_size": 50,
    }

    normalized = normalize_pagination_envelope(response)

    assert normalized["is_last_page"] is True
    assert normalized["next_page"] is None


@pytest.mark.unit
def test_normalize_batch_results_maps_legacy_alias_keys():
    """Batch helper maps legacy quote/contact alias keys into canonical id/data fields."""
    response = {
        "results": [
            {
                "index": 0,
                "success": True,
                "quote_id": "Q-1",
                "quote_data": {"id": "Q-1"},
                "error": None,
            },
            {
                "index": 1,
                "success": False,
                "contact_id": None,
                "contact_data": None,
                "error": "bad payload",
                "errorType": "ValidationError",
            },
        ]
    }

    normalized = normalize_batch_results(response)

    assert normalized["total"] == 2
    assert normalized["succeeded"] == 1
    assert normalized["failed"] == 1
    assert normalized["results"][0]["id"] == "Q-1"
    assert normalized["results"][0]["data"] == {"id": "Q-1"}
    assert normalized["results"][1]["error_type"] == "ValidationError"


@pytest.mark.unit
def test_normalize_batch_results_handles_non_dict_items():
    """Batch helper marks unexpected result item shapes as failed entries."""
    response = {"results": ["not-a-dict"]}

    normalized = normalize_batch_results(response)

    assert normalized["total"] == 1
    assert normalized["failed"] == 1
    assert normalized["results"][0]["success"] is False
    assert "Unexpected non-dict batch item" in normalized["results"][0]["error"]


@pytest.mark.unit
def test_api_package_exports_response_helpers():
    """api package exposes response helper utilities for direct imports."""
    import britecore_sdk.api as api

    assert hasattr(api, "extract_data")
    assert hasattr(api, "extract_items")
    assert hasattr(api, "normalize_pagination_envelope")
    assert hasattr(api, "normalize_batch_results")
