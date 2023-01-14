import pytest
from sqlalchemy import create_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from .models import Base, Entity


@pytest.fixture
def session(db, sample):
    del sample
    with db() as y:
        yield y


def test_sample(db, sample):
    del sample
    Model = Entity
    with db() as session:
        stmt = select(Model)
        models = session.scalars(stmt)
        assert 10 == len(models.all())


@pytest.fixture
def sample(db):
    with db.begin() as session:
        num = [3, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        txt = ["AA", "BB", "AA", "AA", "BB", "AA", "AA", "BB", "AA", "BB"]
        for i in range(10):
            model = Entity(num=num[i], txt=txt[i])
            session.add(model)


@pytest.fixture
def db(engine):
    Base.metadata.create_all(bind=engine)
    y = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return y


@pytest.fixture
def engine():
    url = "sqlite:///:memory:?check_same_thread=false"
    y = create_engine(url)
    return y
