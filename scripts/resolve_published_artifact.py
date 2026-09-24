#!/usr/bin/env python3
"""Resolve a published PyPI/TestPyPI artifact URL for workflow smoke tests."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

REQUEST_TIMEOUT_SECONDS = 20
DEFAULT_MAX_ATTEMPTS = 12
DEFAULT_DELAY_SECONDS = 20
PREFERRED_PACKAGE_TYPES = ("bdist_wheel", "sdist")


def build_metadata_url(json_base: str, package_name: str, package_version: str) -> str:
    """Return the versioned package metadata URL for the given package index base."""
    base = json_base.rstrip("/")
    return (
        f"{base}/{quote(package_name, safe='')}/{quote(package_version, safe='')}/json"
    )


def fetch_json(
    url: str, *, timeout: int = REQUEST_TIMEOUT_SECONDS
) -> tuple[int, dict[str, Any]]:
    """Fetch a JSON document from an HTTPS URL and return its status code and payload."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Metadata URL must be an HTTPS URL with a host: {url}")

    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    connection = http.client.HTTPSConnection(parsed.netloc, timeout=timeout)
    try:
        connection.request(
            "GET",
            path,
            headers={
                "Accept": "application/json",
                "User-Agent": "britecore-sdk-publish-smoke-test",
            },
        )
        response = connection.getresponse()
        payload_text = response.read().decode("utf-8")
    except OSError as exc:
        raise RuntimeError(f"Request to {url} failed: {exc}") from exc
    finally:
        connection.close()

    if response.status == 404:
        return response.status, {}
    if response.status >= 400:
        raise RuntimeError(
            f"Request to {url} failed with HTTP {response.status}: {response.reason}"
        )

    payload = json.loads(payload_text)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object payload from {url}")
    return response.status, payload


def select_artifact_url(payload: dict[str, Any]) -> tuple[str, str]:
    """Return the preferred published artifact URL and its package type."""
    files = payload.get("urls", [])
    if not isinstance(files, list):
        return "", ""

    for package_type in PREFERRED_PACKAGE_TYPES:
        for item in files:
            if not isinstance(item, dict):
                continue
            url = item.get("url", "")
            if item.get("packagetype") == package_type and isinstance(url, str) and url:
                return url, package_type
    return "", ""


def append_github_output(output_path: str | None, values: dict[str, str]) -> None:
    """Append workflow outputs to the GitHub Actions output file when configured."""
    if not output_path:
        return

    output_file = Path(output_path)
    with output_file.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def append_job_summary(summary_path: str | None, lines: list[str]) -> None:
    """Append status lines to the GitHub Actions job summary when configured."""
    if not summary_path:
        return

    summary_file = Path(summary_path)
    with summary_file.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    """Poll package metadata until a published artifact URL becomes available."""
    parser = argparse.ArgumentParser(
        description="Resolve a published wheel or sdist URL from package index metadata.",
    )
    parser.add_argument("--package-name", required=True)
    parser.add_argument("--package-version", required=True)
    parser.add_argument("--json-base", required=True)
    parser.add_argument("--index-label", required=True)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument("--delay-seconds", type=int, default=DEFAULT_DELAY_SECONDS)
    parser.add_argument(
        "--github-output",
        default=os.environ.get("GITHUB_OUTPUT", ""),
        help="Path to the GitHub Actions output file (defaults to GITHUB_OUTPUT).",
    )
    parser.add_argument(
        "--github-step-summary",
        default=os.environ.get("GITHUB_STEP_SUMMARY", ""),
        help="Path to the GitHub Actions job summary file (defaults to GITHUB_STEP_SUMMARY).",
    )
    args = parser.parse_args(argv)

    if args.max_attempts < 1:
        raise SystemExit("--max-attempts must be at least 1")
    if args.delay_seconds < 0:
        raise SystemExit("--delay-seconds must be 0 or greater")

    metadata_url = build_metadata_url(
        args.json_base,
        args.package_name,
        args.package_version,
    )

    artifact_url = ""
    artifact_type = ""

    for attempt in range(1, args.max_attempts + 1):
        try:
            status, payload = fetch_json(metadata_url)
            if status == 404:
                print(
                    f"{args.index_label} metadata for {args.package_name}=={args.package_version} is not visible yet "
                    f"(attempt {attempt}/{args.max_attempts})."
                )
            else:
                artifact_url, artifact_type = select_artifact_url(payload)
                if artifact_url:
                    descriptor = "wheel" if artifact_type == "bdist_wheel" else "sdist"
                    if artifact_type == "bdist_wheel":
                        print(
                            f"Resolved published {descriptor} artifact from {args.index_label}: {artifact_url}"
                        )
                    else:
                        print(
                            f"Wheel artifact not listed yet; falling back to published {descriptor} artifact from {args.index_label}: {artifact_url}"
                        )
                    append_github_output(
                        args.github_output,
                        {
                            "artifact_url": artifact_url,
                            "artifact_type": artifact_type,
                            "metadata_url": metadata_url,
                        },
                    )
                    append_job_summary(
                        args.github_step_summary,
                        [
                            "### Published artifact resolved",
                            f"- Registry: {args.index_label}",
                            f"- Package: `{args.package_name}=={args.package_version}`",
                            f"- Metadata URL: `{metadata_url}`",
                            f"- Artifact type: `{artifact_type}`",
                            f"- Artifact URL: `{artifact_url}`",
                        ],
                    )
                    return 0
                print(
                    f"{args.index_label} metadata is visible for {args.package_name}=={args.package_version}, "
                    f"but no wheel or sdist URL was listed yet (attempt {attempt}/{args.max_attempts})."
                )
        except Exception as exc:
            print(
                f"Unexpected error while checking {args.index_label} metadata for {args.package_name}=={args.package_version}: "
                f"{exc} (attempt {attempt}/{args.max_attempts})."
            )

        if attempt == args.max_attempts:
            raise SystemExit(
                " ".join(
                    [
                        f"Package {args.package_name}=={args.package_version} did not become available from {args.index_label} in time.",
                        "The publish step may still have succeeded while registry metadata propagation lagged.",
                        "Re-run the smoke-test job or re-run the publish workflow manually from the same tag if this package version later appears in the registry.",
                    ]
                )
            )

        print(
            f"Waiting {args.delay_seconds} seconds for {args.index_label} metadata propagation..."
        )
        time.sleep(args.delay_seconds)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
