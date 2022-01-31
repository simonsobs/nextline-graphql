import sys
import threading
import pytest


##__________________________________________________________________||
@pytest.fixture(autouse=True)
def recover_trace():
    """Set the original trace funciton back after each test"""
    trace_org = sys.gettrace()
    yield
    sys.settrace(trace_org)
    threading.settrace(trace_org)


##__________________________________________________________________||
@pytest.fixture(autouse=True)
async def close_nextline():
    """Close nextline after each test"""
    yield
    from nextlinegraphql.nl import close_nextline as close

    await close()


##__________________________________________________________________||
