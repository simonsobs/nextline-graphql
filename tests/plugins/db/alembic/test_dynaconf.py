'''Test the configuration for alembic.

Assert `nextlinegraphql/db/migration.toml` is read when the cwd is `nextlinegraphql/db`.
'''

from nextlinegraphql.config import load_settings
from nextlinegraphql.hook import load_plugins


def test_db_url(in_alembic_dir):
    del in_alembic_dir
    hook = load_plugins()
    settings = load_settings(hook=hook)
    assert settings.DB.URL == 'sqlite:///migration.sqlite3'
