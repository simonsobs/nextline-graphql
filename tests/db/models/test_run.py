import datetime
from sqlalchemy.orm import Session
from sqlalchemy.future import select

import pytest

from typing import cast

from nextlinegraphql.db import init_db
from nextlinegraphql.db.models import Run


def test_one(db):
    run_no = 1
    with db() as session:
        session = cast(Session, session)
        model = Run(
            run_no=run_no,
            state="running",
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now(),
            script="pass",
        )
        session.add(model)
        session.commit()
        assert model.id

    with db() as session:
        stmt = select(Run).filter_by(run_no=run_no)
        model = session.execute(stmt).scalar_one()


@pytest.fixture
def db():
    config = {
        "url": "sqlite:///:memory:",
        "connect_args": {"check_same_thread": False},
    }
    return init_db(config)
