from __future__ import annotations

from pathlib import Path

import pytest

from scripts.resolve_published_artifact import (
    append_github_output,
    append_job_summary,
    build_metadata_url,
    select_artifact_url,
)

pytestmark = pytest.mark.unit


def test_build_metadata_url_escapes_package_name_and_version() -> None:
    url = build_metadata_url(
        "https://pypi.org/pypi/",
        "britecore sdk",
        "2.5.1+build 7",
    )

    assert url == "https://pypi.org/pypi/britecore%20sdk/2.5.1%2Bbuild%207/json"


def test_select_artifact_url_prefers_wheel() -> None:
    payload = {
        "urls": [
            {
                "packagetype": "sdist",
                "url": "https://files.pythonhosted.org/packages/source/b/britecore_sdk.tar.gz",
            },
            {
                "packagetype": "bdist_wheel",
                "url": "https://files.pythonhosted.org/packages/wheel/britecore_sdk.whl",
            },
        ]
    }

    artifact_url, artifact_type = select_artifact_url(payload)

    assert artifact_type == "bdist_wheel"
    assert artifact_url.endswith("britecore_sdk.whl")


def test_select_artifact_url_falls_back_to_sdist() -> None:
    payload = {
        "urls": [
            {
                "packagetype": "sdist",
                "url": "https://files.pythonhosted.org/packages/source/b/britecore_sdk.tar.gz",
            }
        ]
    }

    artifact_url, artifact_type = select_artifact_url(payload)

    assert artifact_type == "sdist"
    assert artifact_url.endswith("britecore_sdk.tar.gz")


def test_append_github_output_writes_key_value_lines(tmp_path: Path) -> None:
    output_path = tmp_path / "github_output.txt"

    append_github_output(
        str(output_path),
        {
            "artifact_url": "https://example.invalid/file.whl",
            "artifact_type": "bdist_wheel",
        },
    )

    assert output_path.read_text(encoding="utf-8") == (
        "artifact_url=https://example.invalid/file.whl\n" "artifact_type=bdist_wheel\n"
    )


def test_append_job_summary_writes_markdown_lines(tmp_path: Path) -> None:
    summary_path = tmp_path / "summary.md"

    append_job_summary(
        str(summary_path), ["### Published artifact resolved", "- Registry: PyPI"]
    )

    assert summary_path.read_text(encoding="utf-8") == (
        "### Published artifact resolved\n- Registry: PyPI\n"
    )


def test_main_rejects_non_https_metadata_url() -> None:
    from scripts.resolve_published_artifact import main

    with pytest.raises(SystemExit, match="did not become available from PyPI in time"):
        main(
            [
                "--package-name",
                "britecore_sdk",
                "--package-version",
                "2.5.1",
                "--json-base",
                "http://example.com/pypi",
                "--index-label",
                "PyPI",
                "--max-attempts",
                "1",
                "--delay-seconds",
                "0",
            ]
        )
