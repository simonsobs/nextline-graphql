"""
uvicorn --factory --reload --reload-dir nextline-graphql --reload-dir nextline nextlinegraphql:create_app
use "--lifespan on" to show exception in lifespan
"""

__all__ = ["create_app", "__version__"]

# remove args so that they won't be processed in the executing script
# TODO This should be properly handled and tested
import sys  # noqa: E402

from .__about__ import __version__
from .factory import create_app

sys.argv[1:] = []
