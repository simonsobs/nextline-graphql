import datetime
from typing import cast

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from nextlinegraphql.db import DB
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
    url = 'sqlite:///:memory:?check_same_thread=false'
    db = DB(url=url)
    return sessionmaker(autocommit=False, autoflush=False, bind=db.engine)
