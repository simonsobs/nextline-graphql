"""Configuration by Dynaconf

Example: https://github.com/rochacbruno/learndynaconf/blob/main/config.py
"""

from dynaconf import Dynaconf, Validator
from pathlib import Path

here = Path(__file__).resolve().parent
cwd = Path.cwd()

settings = Dynaconf(
    envvar_prefix="NEXTLINE",
    settings_files=[
        str(here.joinpath("config", "default.toml")),
        str(cwd.joinpath("nextline-graphql.toml")),
        str(cwd.joinpath("migration.toml")),  # for alembic to run in ./db/
    ],
    environments=True,
)

settings.validators.register(
    Validator("DB.URL", must_exist=True, is_type_of=str),
)

settings.validators.validate()
