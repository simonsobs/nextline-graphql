import janus

import pytest

from nextlinegraphql.schema.bindables import QueueDist


##__________________________________________________________________||
@pytest.mark.asyncio
async def test_one():
    queue = janus.Queue()
    qd = QueueDist(queue)
    q1 = qd.subscribe()
    q2 = qd.subscribe()

    queue.sync_q.put("abc")
    assert "abc" == await q1.async_q.get()
    assert "abc" == await q2.async_q.get()

    queue.sync_q.put("def")
    assert "def" == q1.sync_q.get()
    assert "def" == q2.sync_q.get()

    await qd.unsubscribe(q1)
    await qd.unsubscribe(q2)

    assert not qd.subscribers


##__________________________________________________________________||
