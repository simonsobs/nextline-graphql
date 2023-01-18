'''A wrapper around pluggy to make it work with async functions.

>>> from nextlinegraphql import apluggy

>>> hookspec = apluggy.HookspecMarker("myproject")
>>> hookimpl = apluggy.HookimplMarker("myproject")

>>> class MySpec:
...     """A hook specification namespace."""
...
...     @hookspec
...     async def myhook(self, arg1, arg2):
...         """My special little hook that you can customize."""

>>> class Plugin_1:
...     """A hook implementation namespace."""
...
...     @hookimpl
...     async def myhook(self, arg1, arg2):
...         print("inside Plugin_1.myhook()")
...         return arg1 + arg2

>>> class Plugin_2:
...     """A 2nd hook implementation namespace."""
...
...     @hookimpl
...     async def myhook(self, arg1, arg2):
...         print("inside Plugin_2.myhook()")
...         return arg1 - arg2


>>> async def main():
...     pm = apluggy.APluginManager("myproject")
...     pm.add_hookspecs(MySpec)
...     r = pm.register(Plugin_1())
...     r = pm.register(Plugin_2())
...     results = await pm.ahook.myhook(arg1=1, arg2=2)  # ahook instead of hook
...     print(results)

>>> asyncio.run(main())
inside Plugin_2.myhook()
inside Plugin_1.myhook()
[-1, 3]

'''

__all__ = [
    'PluginManager',
    'PluginValidationError',
    'HookCallError',
    'HookspecMarker',
    'HookimplMarker',
    'AsyncPluginManager',
]

import asyncio

from pluggy import (
    HookCallError,
    HookimplMarker,
    HookspecMarker,
    PluginManager,
    PluginValidationError,
)


class _AHook:
    def __init__(self, pm: PluginManager):
        self.pm = pm

    def __getattr__(self, name):
        async def call(*args, **kwargs):
            hook = getattr(self.pm.hook, name)
            coros = hook(*args, **kwargs)
            return await asyncio.gather(*coros)

        return call


class APluginManager(PluginManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ahook = _AHook(self)
