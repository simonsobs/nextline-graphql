'''implement asynccontextmanager in the same way as decorator.contextmanager'''

__all__ = ['asynccontextmanager']

import contextlib

from decorator import decorate, decorator


class AsyncContextManager(contextlib._AsyncGeneratorContextManager):
    def __init__(self, g, *a, **k):
        super().__init__(g, a, k)

    def __call__(self, func):
        async def caller(f, *a, **k):
            async with self.__class__(self.func, *self.args, **self.kwds):
                return f(*a, **k)

        return decorate(func, caller)


_asynccontextmanager = decorator(AsyncContextManager)


def asynccontextmanager(func):
    return _asynccontextmanager(func)
