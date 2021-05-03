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
