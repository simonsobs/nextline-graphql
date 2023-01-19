import datetime

from sqlalchemy import select

from nextlinegraphql.db import DB
from nextlinegraphql.db.models import Run


def test_one():
    db = DB()
    run_no = 1
    with db.session() as session:
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

    with db.session() as session:
        stmt = select(Run).filter_by(run_no=run_no)
        model = session.execute(stmt).scalar_one()
