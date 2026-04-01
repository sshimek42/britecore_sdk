"""Legacy setup.py shim — all package metadata and configuration lives in
``pyproject.toml``.  This file exists only for compatibility with tools that
require a ``setup.py`` entry point (e.g. ``pip install -e .`` on older pip
versions, some IDE integrations).  Do not add metadata here; edit
``pyproject.toml`` instead.
"""
from setuptools import setup

setup()
