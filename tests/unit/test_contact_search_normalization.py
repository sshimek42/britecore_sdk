"""Unit tests for contact search response normalization helper."""

import pytest

from britecore_sdk.api.workflows.contact_search_normalization import (
    normalize_contact_search_results,
)


@pytest.mark.unit
def test_normalize_contact_search_results_raw_list():
    payload = [{"id": "c1"}, {"id": "c2"}]
    assert normalize_contact_search_results(payload) == payload


@pytest.mark.unit
def test_normalize_contact_search_results_data_list():
    payload = {"data": [{"id": "c1"}]}
    assert normalize_contact_search_results(payload) == [{"id": "c1"}]


@pytest.mark.unit
def test_normalize_contact_search_results_nested_results_list():
    payload = {"data": {"results": [{"id": "c1"}]}}
    assert normalize_contact_search_results(payload) == [{"id": "c1"}]


@pytest.mark.unit
def test_normalize_contact_search_results_non_dict_items_filtered():
    payload = {"results": [{"id": "c1"}, "bad", 123]}
    assert normalize_contact_search_results(payload) == [{"id": "c1"}]


@pytest.mark.unit
def test_normalize_contact_search_results_unknown_shape_returns_empty_list():
    assert normalize_contact_search_results({"success": True}) == []
    assert normalize_contact_search_results(None) == []
