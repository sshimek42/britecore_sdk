"""Settings config"""
import os

from dynaconf import Dynaconf, Validator

curr_dir = os.path.dirname(__file__)
setting_files = [".secrets.toml", "settings.toml"]

setting_files_full = []
for each_file in setting_files:
    setting_files_full.append(os.path.join(curr_dir, each_file))

settings = Dynaconf(
    settings_files=setting_files_full,
    enviroments=True)

settings.validators.register(
    Validator(
        "base_url",
        "client_id",
        "client_secret",
        env=["homestead", "wausau"],
        must_exist=True,
        is_type_of=str,
    ),
    Validator("web_retry", "web_timeout", "web_timeout_long", is_type_of=int),
)
settings.validators.validate()
