# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_all_missiontypes_empty 1'] = {
    'data': {
        'all_missiontypes': [
        ]
    }
}

snapshots['test_create_missiontype 1'] = {
    'data': {
        'create_missiontype': {
            'missiontype': {
                'missiontype_name': 'Initial'
            }
        }
    }
}

snapshots['test_delete_missiontype 1'] = {
    'data': {
        'delete_missiontype': {
            'missiontype': {
                'missiontype_name': 'Initial'
            }
        }
    }
}

snapshots['test_update_missiontype 1'] = {
    'data': {
        'update_missiontype': {
            'missiontype': {
                'missiontype_name': 'Updated'
            }
        }
    }
}
