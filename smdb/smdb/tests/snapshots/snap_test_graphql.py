# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_all_expeditions 1'] = {
    'data': {
        'all_expeditions': [
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190124m1',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190125m1',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190308m1',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190308m2',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190314m1',
                'start_date': None
            },
            {
                'end_date': '1998-07-20T00:00:00+00:00',
                'expd_name': 'Initial',
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190308m1',
                'start_date': '1998-07-01T00:00:00+00:00'
            }
        ]
    }
}

snapshots['test_all_expeditions_empty 1'] = {
    'data': {
        'all_expeditions': [
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190124m1',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190125m1',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190308m1',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190308m2',
                'start_date': None
            },
            {
                'end_date': None,
                'expd_name': None,
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190314m1',
                'start_date': None
            }
        ]
    }
}

snapshots['test_all_missiontypes_empty 1'] = {
    'data': {
        'all_missiontypes': [
        ]
    }
}

snapshots['test_all_persons 1'] = {
    'data': {
        'all_persons': [
            {
                'first_name': 'Jane',
                'institution_name': 'MBARI',
                'last_name': 'Doe'
            }
        ]
    }
}

snapshots['test_all_persons_empty 1'] = {
    'data': {
        'all_persons': [
        ]
    }
}

snapshots['test_all_platforms_empty 1'] = {
    'data': {
        'all_platforms': [
        ]
    }
}

snapshots['test_all_platformtypes 1'] = {
    'data': {
        'all_platformtypes': [
            {
                'platformtype_name': 'Initial'
            }
        ]
    }
}

snapshots['test_all_platformtypes_empty 1'] = {
    'data': {
        'all_platformtypes': [
        ]
    }
}

snapshots['test_all_sensors 1'] = {
    'data': {
        'all_sensors': [
            {
                'comment': 'Initial comment',
                'model_name': 'Initial'
            }
        ]
    }
}

snapshots['test_all_sensors_empty 1'] = {
    'data': {
        'all_sensors': [
        ]
    }
}

snapshots['test_all_sensortypes 1'] = {
    'data': {
        'all_sensortypes': [
            {
                'sensortype_name': 'Initial'
            }
        ]
    }
}

snapshots['test_all_sensortypes_empty 1'] = {
    'data': {
        'all_sensortypes': [
        ]
    }
}

snapshots['test_create_expedition 1'] = {
    'data': {
        'create_expedition': {
            'expedition': {
                'chiefscientist': {
                    'first_name': 'Walter',
                    'last_name': 'Munk'
                },
                'end_date': '1998-07-20T00:00:00',
                'expd_name': 'Initial',
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190308m1',
                'investigator': {
                    'first_name': 'Henry',
                    'last_name': 'Stommel'
                },
                'start_date': '1998-07-01T00:00:00'
            }
        }
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

snapshots['test_create_person 1'] = {
    'data': {
        'create_person': {
            'person': {
                'first_name': 'Jane',
                'institution_name': 'MBARI',
                'last_name': 'Doe'
            }
        }
    }
}

snapshots['test_create_platform 1'] = {
    'data': {
        'create_platform': {
            'platform': {
                'operator_org_name': 'MBARI',
                'platform_name': 'Dorado',
                'platform_type': {
                    'platformtype_name': 'AUV'
                }
            }
        }
    }
}

snapshots['test_create_platformtype 1'] = {
    'data': {
        'create_platformtype': {
            'platformtype': {
                'platformtype_name': 'Initial'
            }
        }
    }
}

snapshots['test_create_sensor 1'] = {
    'data': {
        'create_sensor': {
            'sensor': {
                'comment': 'Initial comment',
                'model_name': 'Initial',
                'sensor_type': {
                    'sensortype_name': 'Sonar'
                }
            }
        }
    }
}

snapshots['test_create_sensortype 1'] = {
    'data': {
        'create_sensortype': {
            'sensortype': {
                'sensortype_name': 'Initial'
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

snapshots['test_delete_person 1'] = {
    'data': {
        'delete_person': {
            'person': {
                'first_name': 'Jane',
                'institution_name': 'MBARI',
                'last_name': 'Doe'
            }
        }
    }
}

snapshots['test_delete_platform 1'] = {
    'data': {
        'delete_platform': {
            'platform': {
                'platform_name': 'Dorado'
            }
        }
    }
}

snapshots['test_delete_platformtype 1'] = {
    'data': {
        'delete_platformtype': {
            'platformtype': {
                'platformtype_name': 'Initial'
            }
        }
    }
}

snapshots['test_delete_sensor 1'] = {
    'data': {
        'delete_sensor': {
            'sensor': {
                'comment': 'Initial comment',
                'model_name': 'Initial'
            }
        }
    }
}

snapshots['test_delete_sensortype 1'] = {
    'data': {
        'delete_sensortype': {
            'sensortype': {
                'sensortype_name': 'Initial'
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

snapshots['test_update_person 1'] = {
    'data': {
        'update_person': {
            'person': {
                'first_name': 'Jim',
                'institution_name': 'SIO',
                'last_name': 'Roe'
            }
        }
    }
}

snapshots['test_update_platform 1'] = {
    'data': {
        'update_platform': {
            'platform': {
                'operator_org_name': 'SIO',
                'platform_name': 'Updated',
                'platform_type': {
                    'platformtype_name': 'LRAUV'
                }
            }
        }
    }
}

snapshots['test_update_platformtype 1'] = {
    'data': {
        'update_platformtype': {
            'platformtype': {
                'platformtype_name': 'Updated'
            }
        }
    }
}

snapshots['test_update_sensor 1'] = {
    'data': {
        'update_sensor': {
            'sensor': {
                'comment': 'New comment',
                'model_name': 'Updated'
            }
        }
    }
}

snapshots['test_update_sensortype 1'] = {
    'data': {
        'update_sensortype': {
            'sensortype': {
                'sensortype_name': 'Updated'
            }
        }
    }
}
