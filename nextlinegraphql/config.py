"""Configuration by Dynaconf

Example: https://github.com/rochacbruno/learndynaconf/blob/main/config.py
"""

from pathlib import Path
from typing import Optional, Sequence

from dynaconf import Dynaconf, Validator

HERE = Path(__file__).resolve().parent

MINIMAL_PRELOAD = (str(HERE / 'config' / 'default.toml'),)
MINIMAL_VALIDATORS = (Validator("DB.URL", must_exist=True, is_type_of=str),)


def create_settings(
    preload: Optional[Sequence[str]] = None,
    settings_files: Optional[Sequence[str]] = None,
    validators: Optional[Sequence[Validator]] = None,
) -> Dynaconf:
    '''Return a Dynaconf settings after validation'''
    cwd = Path.cwd()

    minimal_settings_files = (str(cwd / 'nextline-graphql.toml'),)

    preload = MINIMAL_PRELOAD + tuple(preload or ())
    settings_files = minimal_settings_files + tuple(settings_files or ())
    validators = MINIMAL_VALIDATORS + tuple(validators or ())

    if cwd == HERE / 'plugins' / 'db':
        # for alembic
        settings_files = settings_files + (str(cwd / 'migration.toml'),)

    settings = Dynaconf(
        envvar_prefix="NEXTLINE",
        preload=preload,
        settings_files=settings_files,
        validators=validators,
    )

    return settings
