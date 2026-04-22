"""Sphinx configuration for britecore_sdk."""

from __future__ import annotations

import sys
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

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Keep docs build stable in isolated CI environments.
autodoc_mock_imports = [
    "dynaconf",
    "sclogging",
    "urllib3",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Suppress warnings for relative .md links that point to files intentionally
# outside the Sphinx source tree (e.g. tests/README.md, GETTING_STARTED.md,
# TROUBLESHOOTING.md).  These are valid links for GitHub/local viewing but are
# not part of the built docs.
suppress_warnings = ["myst.xref_missing"]

html_theme = "alabaster"
html_static_path = []
