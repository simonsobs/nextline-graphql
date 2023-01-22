"""Configuration by Dynaconf

Example: https://github.com/rochacbruno/learndynaconf/blob/main/config.py
"""

from pathlib import Path
from typing import Optional, Sequence

from dynaconf import Dynaconf, Validator

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

MINIMAL_PRELOAD = (str(DEFAULT_CONFIG_PATH),)
MINIMAL_VALIDATORS = ()


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

    settings = Dynaconf(
        envvar_prefix="NEXTLINE",
        preload=preload,
        settings_files=settings_files,
        validators=validators,
    )

    return settings
