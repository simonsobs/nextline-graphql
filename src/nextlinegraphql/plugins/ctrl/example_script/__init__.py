import sys
from pathlib import Path

__all__ = ["statement"]

THIS_DIR = Path(__file__).resolve().parent
SCRIPT_PATH = THIS_DIR / 'script.py'

sys.path.insert(0, str(THIS_DIR))

with open(SCRIPT_PATH) as f:
    statement = f.read()
