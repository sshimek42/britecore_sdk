"""Sphinx configuration for britecore_sdk."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

project = "britecore_sdk"
copyright = "2026, britecore_sdk contributors"
author = "britecore_sdk contributors"

# Read package version from pyproject.toml without importing runtime modules.
try:
    import tomllib

    pyproject_data = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    release = pyproject_data["project"]["version"]
except Exception:
    release = "0.0.0"

# Use the same value for short and full version display in docs UI.
version = release
html_title = f"{project} {release} documentation"
html_short_title = f"{project} {release}"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

myst_enable_extensions = [
    "substitution",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


def _git_show(fmt: str, ref: str = "HEAD") -> str:
    """Return formatted git metadata or empty string when unavailable."""
    try:
        return subprocess.check_output(
            ["git", "show", "-s", f"--format={fmt}", ref],
            cwd=ROOT,
            text=True,
        ).strip()
    except Exception:
        return ""


docs_commit_hash = os.environ.get(
    "READTHEDOCS_GIT_COMMIT_HASH", ""
).strip() or _git_show("%H")
docs_commit_short = docs_commit_hash[:8] if docs_commit_hash else "unknown"
docs_commit_date_iso = _git_show("%cI", docs_commit_hash or "HEAD")
docs_commit_date = (
    docs_commit_date_iso.split("T")[0] if docs_commit_date_iso else "unknown"
)
docs_build_date = datetime.now(UTC).strftime("%Y-%m-%d")

myst_substitutions = {
    "docs_version": release,
    "docs_commit": docs_commit_short,
    "docs_commit_date": docs_commit_date,
    "docs_build_date": docs_build_date,
}

master_doc = "index"

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Napoleon settings for Google-style docstrings used throughout the SDK.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_attr_annotations = True

# Only mock packages that are not installed in the docs build environment.
# urllib3 and dynaconf are runtime dependencies and are available, so they
# must not be mocked — mocking them causes urllib3 types (Timeout, Retry, etc.)
# to render as MagicMock in the generated API docs.
autodoc_mock_imports: list[str] = []

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "migrations/*"]

# Suppress warnings for relative .md links that point to files intentionally
# outside the Sphinx source tree (for example, test-only docs and local notes).
# Primary user guides are included in the docs tree via {include} wrappers.
suppress_warnings = ["myst.xref_missing"]

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
}
html_static_path = ["_static"]
html_css_files = ["custom.css"]
