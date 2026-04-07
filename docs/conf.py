"""Sphinx configuration for britecore_libraries."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

project = "britecore_libraries"
copyright = "2026, britecore_libraries contributors"
author = "britecore_libraries contributors"

# Read package version from pyproject.toml without importing runtime modules.
try:
    import tomllib

    pyproject_data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
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
    "pyinputplus",
    "pyodbc",
    "sclogging",
    "selenium",
    "urllib3",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = []

