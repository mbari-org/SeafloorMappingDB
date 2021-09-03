# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_all_compilations 1'] = {
    'data': {
        'all_compilations': [
            {
                'comment': 'Initial comment.',
                'compilation_dir_name': '/a/dir/name',
                'compilation_path_name': '/a/path/name',
                'figures_dir_path': '/figures/path',
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.94,
                                36.69
                            ],
                            [
                                -121.94,
                                36.69
                            ],
                            [
                                -121.93,
                                36.69
                            ],
                            [
                                -121.93,
                                36.69
                            ],
                            [
                                -121.94,
                                36.69
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': 'file.kml',
                'navadjust_dir_path': '/nav/adjust/path/',
                'proc_datalist_filename': 'proc.datalist-1',
                'thumbnail_filename': 'thumbnail.png',
                'update_status': 10
            }
        ]
    }
}

snapshots['test_all_compilations_empty 1'] = {
    'data': {
        'all_compilations': [
        ]
    }
}

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

snapshots['test_all_missions 1'] = {
    'data': {
        'all_missions': [
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.945672127,
                                36.692478839
                            ],
                            [
                                -121.945672127,
                                36.69939862
                            ],
                            [
                                -121.936047424,
                                36.69939862
                            ],
                            [
                                -121.936047424,
                                36.692478839
                            ],
                            [
                                -121.945672127,
                                36.692478839
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.893889754,
                                36.775318037
                            ],
                            [
                                -121.893889754,
                                36.794786063
                            ],
                            [
                                -121.869546184,
                                36.794786063
                            ],
                            [
                                -121.869546184,
                                36.775318037
                            ],
                            [
                                -121.893889754,
                                36.775318037
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.893000566,
                                36.778004247
                            ],
                            [
                                -121.893000566,
                                36.795133122
                            ],
                            [
                                -121.870634333,
                                36.795133122
                            ],
                            [
                                -121.870634333,
                                36.778004247
                            ],
                            [
                                -121.893000566,
                                36.778004247
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.87456349,
                                36.776214476
                            ],
                            [
                                -121.87456349,
                                36.781282764
                            ],
                            [
                                -121.866131021,
                                36.781282764
                            ],
                            [
                                -121.866131021,
                                36.776214476
                            ],
                            [
                                -121.87456349,
                                36.776214476
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.892778682,
                                36.777594169
                            ],
                            [
                                -121.892778682,
                                36.795013157
                            ],
                            [
                                -121.870777136,
                                36.795013157
                            ],
                            [
                                -121.870777136,
                                36.777594169
                            ],
                            [
                                -121.892778682,
                                36.777594169
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': 'Initial comment.',
                'grid_bounds': None,
                'kml_filename': None,
                'thumbnail_filename': 'tumbnail.png',
                'update_status': 5
            }
        ]
    }
}

snapshots['test_all_missions_empty 1'] = {
    'data': {
        'all_missions': [
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.945672127,
                                36.692478839
                            ],
                            [
                                -121.945672127,
                                36.69939862
                            ],
                            [
                                -121.936047424,
                                36.69939862
                            ],
                            [
                                -121.936047424,
                                36.692478839
                            ],
                            [
                                -121.945672127,
                                36.692478839
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.893889754,
                                36.775318037
                            ],
                            [
                                -121.893889754,
                                36.794786063
                            ],
                            [
                                -121.869546184,
                                36.794786063
                            ],
                            [
                                -121.869546184,
                                36.775318037
                            ],
                            [
                                -121.893889754,
                                36.775318037
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.893000566,
                                36.778004247
                            ],
                            [
                                -121.893000566,
                                36.795133122
                            ],
                            [
                                -121.870634333,
                                36.795133122
                            ],
                            [
                                -121.870634333,
                                36.778004247
                            ],
                            [
                                -121.893000566,
                                36.778004247
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.87456349,
                                36.776214476
                            ],
                            [
                                -121.87456349,
                                36.781282764
                            ],
                            [
                                -121.866131021,
                                36.781282764
                            ],
                            [
                                -121.866131021,
                                36.776214476
                            ],
                            [
                                -121.87456349,
                                36.776214476
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
            },
            {
                'comment': None,
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.892778682,
                                36.777594169
                            ],
                            [
                                -121.892778682,
                                36.795013157
                            ],
                            [
                                -121.870777136,
                                36.795013157
                            ],
                            [
                                -121.870777136,
                                36.777594169
                            ],
                            [
                                -121.892778682,
                                36.777594169
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': '',
                'thumbnail_filename': '',
                'update_status': None
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

snapshots['test_create_compilation 1'] = {
    'data': {
        'create_compilation': {
            'compilation': {
                'comment': 'Initial comment.',
                'compilation_dir_name': '/a/dir/name',
                'compilation_path_name': '/a/path/name',
                'figures_dir_path': '/figures/path',
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.94,
                                36.69
                            ],
                            [
                                -121.94,
                                36.69
                            ],
                            [
                                -121.93,
                                36.69
                            ],
                            [
                                -121.93,
                                36.69
                            ],
                            [
                                -121.94,
                                36.69
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': 'file.kml',
                'navadjust_dir_path': '/nav/adjust/path/',
                'proc_datalist_filename': 'proc.datalist-1',
                'thumbnail_filename': 'thumbnail.png',
                'update_status': 10
            }
        }
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

snapshots['test_create_mission 1'] = {
    'data': {
        'create_mission': {
            'mission': {
                'comment': 'Initial comment.',
                'grid_bounds': None,
                'kml_filename': None,
                'thumbnail_filename': 'tumbnail.png',
                'update_status': 5
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

snapshots['test_delete_compilation 1'] = {
    'data': {
        'delete_compilation': {
            'compilation': {
                'comment': 'Initial comment.',
                'compilation_dir_name': '/a/dir/name',
                'compilation_path_name': '/a/path/name',
                'figures_dir_path': '/figures/path',
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.94,
                                36.69
                            ],
                            [
                                -121.94,
                                36.69
                            ],
                            [
                                -121.93,
                                36.69
                            ],
                            [
                                -121.93,
                                36.69
                            ],
                            [
                                -121.94,
                                36.69
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': 'file.kml',
                'navadjust_dir_path': '/nav/adjust/path/',
                'proc_datalist_filename': 'proc.datalist-1',
                'thumbnail_filename': 'thumbnail.png',
                'update_status': 10
            }
        }
    }
}

snapshots['test_delete_expedition 1'] = {
    'data': {
        'delete_expedition': {
            'expedition': {
                'chiefscientist': {
                    'first_name': 'Walter',
                    'last_name': 'Munk'
                },
                'end_date': '1998-07-20T00:00:00+00:00',
                'expd_name': 'Initial',
                'expd_path_name': '/mbari/SeafloorMapping/2019/20190308m1',
                'investigator': {
                    'first_name': 'Henry',
                    'last_name': 'Stommel'
                },
                'start_date': '1998-07-01T00:00:00+00:00'
            }
        }
    }
}

snapshots['test_delete_mission 1'] = {
    'data': {
        'delete_mission': {
            'mission': {
                'comment': 'Initial comment.',
                'grid_bounds': None,
                'kml_filename': None,
                'thumbnail_filename': 'tumbnail.png',
                'update_status': 5
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

snapshots['test_update_compilation 1'] = {
    'data': {
        'update_compilation': {
            'compilation': {
                'comment': 'Updated comment.',
                'compilation_dir_name': '/b/dir/name',
                'compilation_path_name': '/b/path/name',
                'figures_dir_path': '/figures/path2',
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.893,
                                36.775
                            ],
                            [
                                -121.893,
                                36.794
                            ],
                            [
                                -121.869,
                                36.794
                            ],
                            [
                                -121.869,
                                36.775
                            ],
                            [
                                -121.893,
                                36.775
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': 'file2.kml',
                'navadjust_dir_path': '/new/adjust/path/',
                'proc_datalist_filename': 'proc.datalist-2',
                'thumbnail_filename': 'thumbnail2.png',
                'update_status': 10
            }
        }
    }
}

snapshots['test_update_expedition 1'] = {
    'data': {
        'update_expedition': {
            'expedition': {
                'chiefscientist': {
                    'first_name': 'Jane',
                    'last_name': 'Roe'
                },
                'end_date': '2021-02-02T00:00:00',
                'expd_name': 'Updated',
                'expd_path_name': '/a/directory/path',
                'investigator': {
                    'first_name': 'John',
                    'last_name': 'Doe'
                },
                'start_date': '2020-01-01T00:00:00'
            }
        }
    }
}

snapshots['test_update_mission 1'] = {
    'data': {
        'create_mission': {
            'mission': {
                'comment': 'Updates comment.',
                'grid_bounds': {
                    'coordinates': [
                        [
                            [
                                -121.893,
                                36.775
                            ],
                            [
                                -121.893,
                                36.794
                            ],
                            [
                                -121.869,
                                36.794
                            ],
                            [
                                -121.869,
                                36.775
                            ],
                            [
                                -121.893,
                                36.775
                            ]
                        ]
                    ],
                    'type': 'Polygon'
                },
                'kml_filename': None,
                'thumbnail_filename': 'tumbnail2.png',
                'update_status': 6
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
