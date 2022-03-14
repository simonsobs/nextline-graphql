"""Configuration by Dynaconf

Example: https://github.com/rochacbruno/learndynaconf/blob/main/config.py
"""

from dynaconf import Dynaconf, Validator
from pathlib import Path

cwd = Path(__file__).resolve().parent
default_settings_file = cwd.joinpath("config", "default.toml")

settings = Dynaconf(
    envvar_prefix="NEXTLINE",
    settings_files=[str(default_settings_file)],
)

settings.validators.register(
    Validator("DB.URL", must_exist=True, is_type_of=str),
)

settings.validators.validate()
