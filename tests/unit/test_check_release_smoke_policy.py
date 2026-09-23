from __future__ import annotations

import pytest

from scripts.check_release_smoke_policy import (
    determine_release_type,
    evaluate_release_policy,
    has_break_glass_marker,
)

pytestmark = pytest.mark.unit


def test_determine_release_type_minor_release() -> None:
    release_type, previous_tag = determine_release_type(
        "v2.5.0",
        ["v2.4.8", "v2.5.0"],
    )

    assert release_type == "minor"
    assert previous_tag == "v2.4.8"


def test_determine_release_type_prerelease() -> None:
    release_type, previous_tag = determine_release_type(
        "v2.5.0-rc.1",
        ["v2.4.8", "v2.5.0"],
    )

    assert release_type == "prerelease"
    assert previous_tag == "none"


def test_break_glass_marker_detects_annotation() -> None:
    assert has_break_glass_marker("release: hotfix [break-glass]")
    assert not has_break_glass_marker("release: hotfix")
    assert not has_break_glass_marker("release: [b] note")


def test_evaluate_release_policy_rejects_minor_without_merged_pr() -> None:
    result = evaluate_release_policy(
        "minor",
        [{"number": 248, "merged_at": None}],
        break_glass=False,
    )

    assert result.exit_code == 1
    assert "merged PR" in result.message
    assert "#248" in result.message


def test_evaluate_release_policy_allows_patch_break_glass_without_merged_pr() -> None:
    result = evaluate_release_policy(
        "patch",
        [{"number": 12, "merged_at": None}],
        break_glass=True,
    )

    assert result.exit_code == 0
    assert "break-glass patch tag" in result.message
