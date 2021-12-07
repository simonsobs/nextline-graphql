from pathlib import Path

from ariadne import load_schema_from_path, make_executable_schema

##__________________________________________________________________||
_THISDIR = Path(__file__).resolve().parent
type_defs = load_schema_from_path(_THISDIR)

del _THISDIR

##__________________________________________________________________||
from .bindables import bindables  # noqa: E402

##__________________________________________________________________||
schema = make_executable_schema(type_defs, *bindables)

##__________________________________________________________________||
