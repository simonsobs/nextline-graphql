'''Configuration by Dynaconf.

Dynaconf: https://www.dynaconf.com/
'''

__all__ = ['load_settings']
from collections.abc import Sequence
from itertools import chain
from pathlib import Path
from typing import Optional

from apluggy import PluginManager
from dynaconf import Dynaconf, Validator

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

MINIMAL_PRELOAD = (str(DEFAULT_CONFIG_PATH),)
MINIMAL_VALIDATORS = (
    # NOTE: Provide default values `['*']` here so that these values will be overridden
    # by the settings file. If the default values were provided in `default.toml`, the
    # lists would be merged instead of overridden.
    Validator('CORS.ALLOW_ORIGINS', is_type_of=list, default=['*']),
    Validator('CORS.ALLOW_HEADERS', is_type_of=list, default=['*']),
    Validator('CORS.ALLOW_CREDENTIALS', is_type_of=bool),
)


def load_settings(hook: PluginManager) -> Dynaconf:
    '''Return a Dynaconf settings after validation'''

    settings = _load_settings(
        preload=tuple(chain(*hook.hook.dynaconf_preload())),
        settings_files=tuple(chain(*hook.hook.dynaconf_settings_files())),
        validators=tuple(chain(*hook.hook.dynaconf_validators())),
    )

    return settings


def _load_settings(
    preload: Optional[Sequence[str]] = None,
    settings_files: Optional[Sequence[str]] = None,
    validators: Optional[Sequence[Validator]] = None,
) -> Dynaconf:
    cwd = Path.cwd()
    minimal_settings_files = (str(cwd / 'nextline-graphql.toml'),)

    preload = MINIMAL_PRELOAD + tuple(preload or ())
    settings_files = minimal_settings_files + tuple(settings_files or ())
    validators = MINIMAL_VALIDATORS + tuple(validators or ())

    # Dynaconf object:
    # Dynaconf Doc: https://www.dynaconf.com/configuration/
    # Example: https://github.com/rochacbruno/learndynaconf/blob/main/config.py
    settings = Dynaconf(
        envvar_prefix="NEXTLINE",
        preload=preload,
        settings_files=settings_files,
        validators=validators,
        merge_enabled=True,
    )

    return settings
