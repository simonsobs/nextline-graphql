import sys
import threading
import pytest

##__________________________________________________________________||
@pytest.fixture(autouse=True)
def recover_trace(monkeypatch):
    trace_org = sys.gettrace()
    yield
    sys.settrace(trace_org)
    threading.settrace(trace_org)

##__________________________________________________________________||
@pytest.fixture(autouse=True)
async def close_nextline():
    yield
    from nextlinegraphql.schema.bindables import close_nextline as close
    await close()

##__________________________________________________________________||
