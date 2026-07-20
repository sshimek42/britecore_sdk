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

html_theme = "alabaster"
html_theme_options = {
    "page_width": "100%",
    "sidebar_width": "320px",
    "sidebar_collapse": False,
    "globaltoc_maxdepth": 3,
}
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
    ]
}
