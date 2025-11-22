'''
The module 'nextlinegraphql' is moving to 'nextline_graphql'.

This is an alias for backward compatibility and will be removed
in a future version.
'''

__all__ = ['__version__', 'create_app', 'spec']

import sys
import warnings
from collections.abc import Sequence
from importlib import import_module
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib.util import find_spec

import nextline_graphql
from nextline_graphql import __version__, create_app, spec

warnings.warn(
    "The 'nextlinegraphql' module is moving to 'nextline_graphql'. "
    'This is an alias for backward compatibility '
    'and will be removed in a future version.',
    DeprecationWarning,
    stacklevel=2,
)


def __getattr__(name: str) -> object:
    return getattr(nextline_graphql, name)


def __dir__() -> list[str]:
    return dir(nextline_graphql)


# 'nextline_graphql'
NEW_NAME = nextline_graphql.__name__

# 'nextlinegraphql'
OLD_NAME = __name__


class _Redirector(MetaPathFinder):
    '''An import hook to redirect imports from OLD_NAME to NEW_NAME.'''
    def find_spec(
        self, fullname: str, path: Sequence[str] | None, target: object | None = None
    ) -> ModuleSpec | None:
        if fullname.split('.')[0] != OLD_NAME:
            return None

        new_name = fullname.replace(OLD_NAME, NEW_NAME, 1)
        spec = find_spec(new_name)
        if spec is None:
            return None

        warnings.warn(
            f"The '{fullname}' module is moving to '{new_name}'. "
            'This is an alias for backward compatibility '
            'and will be removed in a future version.',
            DeprecationWarning,
            stacklevel=2,
        )

        sys.modules[fullname] = import_module(new_name)
        return spec


# Install the import hook
sys.meta_path.insert(0, _Redirector())
