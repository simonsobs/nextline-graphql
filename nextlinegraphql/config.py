"""Configuration by Dynaconf

Example: https://github.com/rochacbruno/learndynaconf/blob/main/config.py
"""

from dynaconf import Dynaconf, Validator
from pathlib import Path

here = Path(__file__).resolve().parent

settings = Dynaconf(
    envvar_prefix="NEXTLINE",
    settings_files=[
        str(here.joinpath("config", "default.toml")),
        "nextline-graphql.toml"
    ],
)

settings.validators.register(
    Validator("DB.URL", must_exist=True, is_type_of=str),
)

settings.validators.validate()
