from pathlib import Path

import pytest


@pytest.fixture
def in_alembic_dir(monkeypatch: pytest.MonkeyPatch):
    import nextlinegraphql

    path = Path(nextlinegraphql.__file__).parent / 'db'
    print(path)
    # '/path/to/repo/src/c5backup/alembic'

    monkeypatch.chdir(path)
