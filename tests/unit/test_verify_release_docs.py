from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "verify_release_docs.py"


def _write_release_docs(root: Path, *, version: str = "2.5.0") -> None:
    (root / "README.md").write_text(
        f"**Status:** Stable (v{version}+) | **License:** Apache-2.0 | **Python:** 3.11+\n",
        encoding="utf-8",
    )
    (root / "IMPROVEMENT_ROADMAP.md").write_text(
        f"*Status: Active roadmap aligned to `v{version}` and `v3.0.0` deprecation planning*\n",
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        f"## [{version}] - 2026-09-23\n",
        encoding="utf-8",
    )


def _run_script(repo_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo_root), *extra_args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_verify_release_docs_passes_for_expected_version(tmp_path: Path) -> None:
    _write_release_docs(tmp_path)

    result = _run_script(tmp_path, "--version", "2.5.0")

    assert result.returncode == 0, result.stderr
    assert "release-facing docs match v2.5.0" in result.stdout


def test_verify_release_docs_reports_missing_banner(tmp_path: Path) -> None:
    _write_release_docs(tmp_path)
    (tmp_path / "README.md").write_text(
        "**Status:** Stable (v2.4.8+) | **License:** Apache-2.0 | **Python:** 3.11+\n",
        encoding="utf-8",
    )

    result = _run_script(tmp_path, "--version", "2.5.0")

    assert result.returncode == 1
    assert "README.md: expected release/status banner for v2.5.0" in result.stderr
