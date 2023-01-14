"""Configuration by Dynaconf

Example: https://github.com/rochacbruno/learndynaconf/blob/main/config.py
"""

from pathlib import Path

from dynaconf import Dynaconf, Validator

HERE = Path(__file__).resolve().parent


def create_settings() -> Dynaconf:
    '''Return a Dynaconf settings after validation'''
    cwd = Path.cwd()

    settings = Dynaconf(
        envvar_prefix="NEXTLINE",
        settings_files=[
            str(HERE.joinpath("config", "default.toml")),
            str(cwd.joinpath("nextline-graphql.toml")),
            str(cwd.joinpath("migration.toml")),  # for alembic to run in ./db/
        ],
        environments=True,
    )

    settings.validators.register(
        Validator("DB.URL", must_exist=True, is_type_of=str),
    )

    settings.validators.validate()

    return settings


settings = create_settings()
