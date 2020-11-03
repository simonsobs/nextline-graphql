from pathlib import Path

from ariadne import load_schema_from_path

##__________________________________________________________________||
_THISDIR = Path(__file__).resolve().parent
type_defs = load_schema_from_path(_THISDIR)

del _THISDIR
##__________________________________________________________________||
