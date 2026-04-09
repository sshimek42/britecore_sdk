import importlib.util
import os

# Path to the utility
UTIL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "src",
    "britecore_libraries",
    "utils",
    "check_site_configs.py",
)

spec = importlib.util.spec_from_file_location("check_site_configs", UTIL_PATH)
check_site_configs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_site_configs)


def test_no_secrets_in_settings():
    """Fail if forbidden keys are found in settings.toml."""
    # This will print a warning if forbidden keys are found
    # We want to fail the test if any are found
    found = []

    def fake_print(*args, **kwargs):
        msg = " ".join(str(a) for a in args)
        if "Sensitive keys found in settings.toml" in msg:
            found.append(msg)

    orig_print = __builtins__["print"]
    __builtins__["print"] = fake_print
    try:
        check_site_configs.warn_if_secrets_in_settings(check_site_configs.SETTINGS_PATH)
    finally:
        __builtins__["print"] = orig_print
    assert (
        not found
    ), "Sensitive keys found in settings.toml! Move them to .secrets.toml."
