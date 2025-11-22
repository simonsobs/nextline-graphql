import sys
import warnings
from importlib import import_module
from pathlib import Path
from types import ModuleType

import pytest

import nextline_graphql

with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    import nextlinegraphql


def _find_all_submodule_names(module: ModuleType) -> tuple[str, ...]:
    '''Names of all submodules under the given module.'''

    assert module.__file__ is not None
    package_path = Path(module.__file__).parent
    abs_init_paths = package_path.rglob('__init__.py')
    rel_init_paths = (p.parent.relative_to(package_path) for p in abs_init_paths)
    rel_init_paths = (p for p in rel_init_paths if str(p) != '.')  # exclude root
    submodule_names = tuple(str(p).replace('/', '.') for p in rel_init_paths)
    return submodule_names


# 'nextline_graphql'
NEW_NAME = nextline_graphql.__name__

# 'nextlinegraphql'
OLD_NAME = nextlinegraphql.__name__

# ('config', 'plugins', 'plugins.ctrl', ...)
ALL_SUBMODULE_NAMES = _find_all_submodule_names(nextline_graphql)

# ('nextline_graphql', 'nextline_graphql.config', 'nextline_graphql.plugins', ...)
ALL_NEW_NAMES = tuple(
    [NEW_NAME, *['.'.join((NEW_NAME, n)) for n in ALL_SUBMODULE_NAMES]]
)

# ('nextlinegraphql', 'nextlinegraphql.config', 'nextlinegraphql.plugins', ...)
ALL_OLD_NAMES = tuple(
    [OLD_NAME, *['.'.join((OLD_NAME, n)) for n in ALL_SUBMODULE_NAMES]]
)


@pytest.fixture(autouse=True)
def clear_module_cache() -> None:
    '''Reset sys.modules to raise warnings afresh for each test.'''
    for key in list(sys.modules):
        if key.split('.')[0] in (OLD_NAME, NEW_NAME):
            del sys.modules[key]


# @pytest.mark.skip
@pytest.mark.parametrize('old_name, new_name', zip(ALL_OLD_NAMES, ALL_NEW_NAMES))
def test_import(old_name: str, new_name: str) -> None:
    '''Confirm the modules are imported correctly with deprecation warnings.'''

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')

        by_old_name = import_module(old_name)

    # Assert deprecation warning was raised
    messages = [m for m in w if issubclass(m.category, DeprecationWarning)]
    assert len(messages) >= 1
    assert NEW_NAME in str(messages[0].message)

    # Assert the same module by both names
    by_new_name = import_module(new_name)
    assert by_old_name is by_new_name
