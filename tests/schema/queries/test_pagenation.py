import datetime
from sqlalchemy.orm import Session


import pytest
from async_asgi_testclient import TestClient

from typing import cast

from nextlinegraphql.db import init_db
from nextlinegraphql.db.models import Run

from ..funcs import gql_request

QUERY = """
{
  history {
    allRuns {
      edges {
        cursor
        node {
          id
          runNo
        }
      }
    }
  }
}
"""


async def test_one(sample, client: TestClient):
    del sample
    data = await gql_request(client, QUERY)
    print(data)


@pytest.fixture
def sample(db):
    with db() as session:
        session = cast(Session, session)
        for run_no in range(0, 100):
            model = Run(
                run_no=run_no,
                state="running",
                started_at=datetime.datetime.now(),
                ended_at=datetime.datetime.now(),
                script="pass",
            )
            session.add(model)
        session.commit()


@pytest.fixture
def db():
    config = {
        "url": "sqlite:///:memory:",
        "connect_args": {"check_same_thread": False},
    }
    return init_db(config)
