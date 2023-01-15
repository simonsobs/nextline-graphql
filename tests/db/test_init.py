import logging
from typing import cast

from alembic.migration import MigrationContext
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm.session import Session

from nextlinegraphql.db import init_db


def test_one(caplog):

    config = {"url": "sqlite:///:memory:?check_same_thread=false"}

    with caplog.at_level(logging.DEBUG):
        db, engine = init_db(config)

    print_logrecords(caplog.records)

    with db.begin() as session:
        session = cast(Session, db)
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

    config = {"url": "sqlite:///:memory:?check_same_thread=false"}

    db, engine = init_db(config)

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        rev = context.get_current_revision()
        assert rev
