"""
uvicorn --factory --reload --reload-dir nextline-graphql --reload-dir nextline nextlinegraphql:create_app
use "--lifespan on" to show exception in lifespan
"""

__all__ = ["create_app"]

from .factory import create_app

##__________________________________________________________________||
# remove args so that they won't be processed in the executing script
# TODO This should be properly handled and tested
import sys  # noqa: E402

sys.argv[1:] = []

##__________________________________________________________________||
from ._version import get_versions  # noqa: E402

__version__ = get_versions()["version"]
"""str: version

The version string, e.g., "0.1.2", "0.1.2+83.ga093a20.dirty".
generated from git tags by versioneer.

Versioneer: https://github.com/warner/python-versioneer

"""

del get_versions

##__________________________________________________________________||
