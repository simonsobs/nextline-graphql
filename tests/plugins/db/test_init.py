import logging
from typing import cast

from alembic.migration import MigrationContext
from sqlalchemy.engine.base import Connection

from nextlinegraphql.plugins.db import DB


def test_one(caplog):

    url = 'sqlite:///:memory:?check_same_thread=false'

    with caplog.at_level(logging.DEBUG):
        db = DB(url=url)
        engine = db.engine

    print_logrecords(caplog.records)

    with db.session() as session:
        with session.begin():
            assert session
            # print(session)

    with engine.connect() as connection:
        connection = cast(Connection, connection)
        assert connection
        # print(connection)


def print_logrecords(records):

    format = "{levelname:8s} [{name}] {message}"
    formatter = logging.Formatter(format, style="{")

    for record in records:
        message = formatter.format(record)
        # print(message)
        del message


def test_alembic():

    url = 'sqlite:///:memory:?check_same_thread=false'
    db = DB(url=url)

    with db.engine.connect() as connection:
        context = MigrationContext.configure(connection)
        rev = context.get_current_revision()
        assert rev
