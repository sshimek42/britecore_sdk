"""CLI tools for BriteCore SDK."""

from britecore_sdk.cli.config_wizard import main as config_wizard_main
from britecore_sdk.cli.quick_check import main as quick_check_main

__all__ = ["quick_check_main", "config_wizard_main"]

