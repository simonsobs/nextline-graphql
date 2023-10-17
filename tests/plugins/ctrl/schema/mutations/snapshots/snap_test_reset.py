# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['test_reset[no-statement] 1'] = {
    'data': {
        'source': [
            'import time',
            '',
            'time.sleep(0.3)',
            '',
            'def f():',
            '    for _ in range(10):',
            '        pass',
            '    return',
            '',
            'f()',
            'f()',
            '',
            "print('here!')",
            '',
            'import script_threading',
            '',
            'script_threading.run()',
            '',
            '',
            'import script_asyncio',
            '',
            'script_asyncio.run()',
            '',
        ]
    }
}

snapshots['test_reset[statement] 1'] = {
    'data': {'source': ['import time', 'time.sleep(0.1)']}
}
