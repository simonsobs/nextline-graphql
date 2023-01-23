'''Test the configuration for alembic.

Assert `nextlinegraphql/db/migration.toml` is read when the cwd is `nextlinegraphql/db`.
'''

from nextlinegraphql.config import load_settings


def test_db_url(in_alembic_dir):
    del in_alembic_dir
    settings = load_settings()
    assert settings.DB.URL == 'sqlite:///migration.sqlite3'
