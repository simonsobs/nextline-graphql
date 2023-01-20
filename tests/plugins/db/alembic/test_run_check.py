'''Run alembic check

- https://github.com/sqlalchemy/alembic/releases/tag/rel_1_9_0
- https://github.com/sqlalchemy/alembic/issues/724
- https://github.com/sqlalchemy/alembic/pull/1101
'''
from pathlib import Path

from alembic import command
from alembic.config import Config


def test_run(in_alembic_dir):
    del in_alembic_dir
    config = Config(Path.cwd() / 'alembic.ini')
    command.upgrade(config, "head")
    command.check(config)
