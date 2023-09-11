"""Settings config"""
import os

from dynaconf import Dynaconf, Validator

curr_dir = os.path.dirname(__file__)
setting_files = ["settings.toml", ".secrets.toml"]

setting_files_full = []
for each_file in setting_files:
    setting_files_full.append(os.path.join(curr_dir, each_file))

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=setting_files_full,
)

settings.validators.register(
    Validator(
        "base_url",
        "client_id",
        "client_secret",
        "db_conn_string",
        must_exist=True,
        is_type_of=str,
    ),
    Validator(
        "logging_auto_create_dir",
        "logging_log_to_file",
        "color",
        is_type_of=bool,
    ),
    Validator(
        "logging_path",
        "logging_ext",
        "web_user",
        "web_pass",
        "web_admin_user",
        "web_admin_pass",
        "agent_user",
        "agent_pass",
        "web_browser",
        is_type_of=str,
    ),
    Validator("web_retry", "web_timeout", "web_timeout_long", is_type_of=int),
    Validator("db_conn_options", is_type_of=dict),
)
settings.validators.validate()
