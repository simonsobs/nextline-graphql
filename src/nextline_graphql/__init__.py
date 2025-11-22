"""
uvicorn --factory --reload --reload-dir nextline-graphql --reload-dir nextline nextline_graphql:create_app
use "--lifespan on" to show exception in lifespan
"""

__all__ = ['__version__', 'create_app', 'spec']

import sys  # noqa: E402

from .__about__ import __version__
from .factory import create_app
from .hook import spec

# remove args so that they won't be processed in the executing script
# TODO This should be properly handled and tested
sys.argv[1:] = []
