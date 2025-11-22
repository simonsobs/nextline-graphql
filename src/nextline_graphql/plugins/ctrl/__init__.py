__all__ = ['Plugin']

from collections.abc import AsyncIterator, MutableMapping
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dynaconf import Dynaconf, Validator

from nextline import Nextline
from nextline_graphql.hook import spec

from .cache import CacheStdout
from .example_script import statement
from .schema import Mutation, Query, Subscription

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (
    Validator('CTRL.TRACE_MODULES', must_exist=True, is_type_of=bool),
    Validator('CTRL.TRACE_THREADS', must_exist=True, is_type_of=bool),
)


class Plugin:
    @spec.hookimpl
    def dynaconf_preload(self) -> Optional[tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[tuple[str, ...]]:
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf) -> None:
        self._trace_modules = settings.ctrl.trace_modules
        self._trace_threads = settings.ctrl.trace_threads

    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    async def update_lifespan_context(self, context: MutableMapping) -> None:
        self._nextline = Nextline(
            statement,
            trace_modules=self._trace_modules,
            trace_threads=self._trace_threads,
        )
        context['nextline'] = self._nextline

    @spec.hookimpl(trylast=True)  # trylast so to be the innermost context
    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        '''Yield within the nextline context.'''
        self._cache_stdout = CacheStdout()
        self._nextline.register(self._cache_stdout)
        async with self._cache_stdout, self._nextline:
            yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['nextline'] = self._nextline
        ctrl = {'cache_stdout': self._cache_stdout}
        context['ctrl'] = ctrl
