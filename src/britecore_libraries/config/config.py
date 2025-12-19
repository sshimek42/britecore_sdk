"""Settings config"""

from pathlib import Path

from dynaconf import Dynaconf, Validator

curr_dir = Path(__file__).parent
setting_files: list[str] = [".secrets.toml", "settings.toml"]

setting_files_full: list[Path] = []
for each_file in setting_files:
    setting_files_full.append(curr_dir / each_file)

settings = Dynaconf(settings_files=setting_files_full, enviroments=True)

settings.validators.register(
    Validator(
        "base_url",
        "client_id",
        "client_secret",
        "api_key",
        env=["wausau", "wausau_test"],
        must_exist=True,
        is_type_of=str,
    ),
    Validator("web_retry", "web_timeout", "web_timeout_long", is_type_of=int),
)
settings.validators.validate()
