# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['test_source[default] 1'] = {
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

snapshots['test_source[path] 1'] = {
    'source': [
        'from threading import Thread',
        '',
        '',
        'def run():',
        '    t1 = Thread(target=f1)',
        '    t1.start()',
        '    t2 = Thread(target=f2)',
        '    t2.start()',
        '    t2.join()',
        '    t1.join()',
        '    return',
        '',
        'def f1():',
        '    for _ in range(5):',
        '        pass',
        '    return',
        '',
        'def f2():',
        '    for _ in range(5):',
        '        pass',
        '    return',
        '',
    ]
}

snapshots['test_source[string] 1'] = {
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
