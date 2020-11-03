# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_counter 1'] = {
    'counter': 1
}

snapshots['test_counter 2'] = {
    'counter': 2
}

snapshots['test_counter 3'] = {
    'counter': 3
}

snapshots['test_counter 4'] = {
    'counter': 4
}

snapshots['test_counter 5'] = {
    'counter': 5
}
