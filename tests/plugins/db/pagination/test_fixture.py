from sqlalchemy import select

from .models import Entity


def test_sample(session):
    Model = Entity
    stmt = select(Model)
    models = session.scalars(stmt)
    assert 10 == len(models.all())
