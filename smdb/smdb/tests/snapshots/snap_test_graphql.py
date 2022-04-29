# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_all_citations 1'] = {
    'data': {
        'all_citations': [
            {
                'doi': 'doi://123456/hello',
                'full_reference': 'Initial Reference',
                'missions': [
                    {
                        'expedition': {
                            'name': 'EN1'
                        },
                        'name': 'M1'
                    },
                    {
                        'expedition': {
                            'name': 'EN2'
                        },
                        'name': 'M2'
                    }
                ]
            }
        ]
    }
}

snapshots['test_all_citations_empty 1'] = {
    'data': {
        'all_citations': [
        ]
    }
}

snapshots['test_all_compilations 1'] = {
    'data': {
        'all_compilations': [
            {
                'comment': 'Initial comment.',
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
                'name': '/a/dir/name',
                'navadjust_dir_path': '/nav/adjust/path/',
                'path_name': '/a/path/name',
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

snapshots['test_all_dataarchivals 1'] = {
    'data': {
        'all_dataarchivals': [
            {
                'archival_db_name': 'Initial Archival',
                'doi': 'doi://123456/hello',
                'missions': [
                    {
                        'expedition': {
                            'name': 'EN1'
                        },
                        'name': 'M1'
                    },
                    {
                        'expedition': {
                            'name': 'EN2'
                        },
                        'name': 'M2'
                    }
                ]
            }
        ]
    }
}

snapshots['test_all_dataarchivals_empty 1'] = {
    'data': {
        'all_dataarchivals': [
        ]
    }
}

snapshots['test_all_expeditions 1'] = {
    'data': {
        'all_expeditions': [
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Testing Terrain Relative Navigation for the Axial Geodesy project and Precisions Controls Project',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Testing Mapping AUV 1',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Mapping AUV Testing in upper Monterey Canyon - 6563',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Morro Bay Expedition - 6570',
                'start_date': None
            },
            {
                'end_date': '1998-07-20T00:00:00',
                'name': 'Initial',
                'start_date': '1998-07-01T00:00:00'
            }
        ]
    }
}

snapshots['test_all_expeditions_empty 1'] = {
    'data': {
        'all_expeditions': [
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Testing Terrain Relative Navigation for the Axial Geodesy project and Precisions Controls Project',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Testing Mapping AUV 1',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Mapping AUV Testing in upper Monterey Canyon - 6563',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Morro Bay Expedition - 6570',
                'start_date': None
            }
        ]
    }
}

snapshots['test_all_missions 1'] = {
    'data': {
        'all_missions': [
            {
                'comment': '''MBARI Mapping AUV Operations
24 January 2019
R/V Rachel Carson
Testing Terrain Relative Navigation for the Axial Geodesy project and Precisions Controls Project''',
                'directory': '/mbari/SeafloorMapping/2019/20190124m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190124m1/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
25 January 2019
R/V Rachel Carson
Testing Mapping AUV 1''',
                'directory': '/mbari/SeafloorMapping/2019/20190125m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190125m1/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
8 March 2019
R/V Rachel Carson
Mapping AUV Testing in upper Monterey Canyon''',
                'directory': '/mbari/SeafloorMapping/2019/20190308m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190308m1/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
8 March 2019
R/V Rachel Carson
Mapping AUV Testing in upper Monterey Canyon''',
                'directory': '/mbari/SeafloorMapping/2019/20190308m2',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190308m2/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
14 March 2019
R/V Rachel Carson
Morro Bay Expedition''',
                'directory': '/mbari/SeafloorMapping/2019/20190314m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190314m1/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': 'Initial comment.',
                'directory': '/mbari/SeafloorMapping/2019/20190308m1',
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
                'kml_filename': 'kml_file.kml',
                'thumbnail_filename': 'thumbnail.png',
                'update_status': 5
            }
        ]
    }
}

snapshots['test_all_missions_empty 1'] = {
    'data': {
        'all_missions': [
            {
                'comment': '''MBARI Mapping AUV Operations
24 January 2019
R/V Rachel Carson
Testing Terrain Relative Navigation for the Axial Geodesy project and Precisions Controls Project''',
                'directory': '/mbari/SeafloorMapping/2019/20190124m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190124m1/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
25 January 2019
R/V Rachel Carson
Testing Mapping AUV 1''',
                'directory': '/mbari/SeafloorMapping/2019/20190125m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190125m1/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
8 March 2019
R/V Rachel Carson
Mapping AUV Testing in upper Monterey Canyon''',
                'directory': '/mbari/SeafloorMapping/2019/20190308m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190308m1/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
8 March 2019
R/V Rachel Carson
Mapping AUV Testing in upper Monterey Canyon''',
                'directory': '/mbari/SeafloorMapping/2019/20190308m2',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190308m2/ZTopoSlopeNav.jpg',
                'update_status': None
            },
            {
                'comment': '''MBARI Mapping AUV Operations
14 March 2019
R/V Rachel Carson
Morro Bay Expedition''',
                'directory': '/mbari/SeafloorMapping/2019/20190314m1',
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
                'kml_filename': None,
                'thumbnail_filename': '/mbari/SeafloorMapping/2019/20190314m1/ZTopoSlopeNav.jpg',
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

snapshots['test_all_platforms 1'] = {
    'data': {
        'all_platforms': [
            {
                'name': 'R/V Rachel Carson'
            },
            {
                'name': 'Dorado'
            }
        ]
    }
}

snapshots['test_all_platforms 2'] = {
    'data': {
        'all_platforms': [
            {
                'name': 'R/V Rachel Carson'
            },
            {
                'name': 'Dorado'
            }
        ]
    }
}

snapshots['test_all_platforms_empty 1'] = {
    'data': {
        'all_platforms': [
            {
                'name': 'R/V Rachel Carson',
                'uuid': '502b9e1c-5650-474e-87f8-1b2c3532b32f'
            }
        ]
    }
}

snapshots['test_all_platformtypes 1'] = {
    'data': {
        'all_platformtypes': [
            {
                'name': 'ship'
            },
            {
                'name': 'Initial'
            }
        ]
    }
}

snapshots['test_all_platformtypes_empty 1'] = {
    'data': {
        'all_platformtypes': [
            {
                'name': 'ship',
                'uuid': '5de40722-589e-4cb8-a9b1-e52b1cb8399b'
            }
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
                'name': 'Initial'
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

snapshots['test_create_citation 1'] = {
    'data': {
        'create_citation': {
            'citation': {
                'doi': 'doi://123456/hello',
                'full_reference': 'Initial Reference',
                'missions': [
                    {
                        'expedition': {
                            'name': 'EN1'
                        },
                        'name': 'M1'
                    },
                    {
                        'expedition': {
                            'name': 'EN2'
                        },
                        'name': 'M2'
                    }
                ]
            }
        }
    }
}

snapshots['test_create_compilation 1'] = {
    'data': {
        'create_compilation': {
            'compilation': {
                'comment': 'Initial comment.',
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
                'name': '/a/dir/name',
                'navadjust_dir_path': '/nav/adjust/path/',
                'path_name': '/a/path/name',
                'proc_datalist_filename': 'proc.datalist-1',
                'thumbnail_filename': 'thumbnail.png',
                'update_status': 10
            }
        }
    }
}

snapshots['test_create_dataarchival 1'] = {
    'data': {
        'create_dataarchival': {
            'dataarchival': {
                'archival_db_name': 'Initial Archival',
                'doi': 'doi://123456/hello',
                'missions': [
                    {
                        'expedition': {
                            'name': 'EN1'
                        },
                        'name': 'M1'
                    },
                    {
                        'expedition': {
                            'name': 'EN2'
                        },
                        'name': 'M2'
                    }
                ]
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
                'investigator': {
                    'first_name': 'Henry',
                    'last_name': 'Stommel'
                },
                'name': 'Initial',
                'start_date': '1998-07-01T00:00:00'
            }
        }
    }
}

snapshots['test_create_mission 1'] = {
    'data': {
        'create_mission': {
            'mission': {
                'citations': [
                    {
                        'doi': 'doi://c_initial/1',
                        'full_reference': 'C Initial 1'
                    },
                    {
                        'doi': 'doi://c_initial/2',
                        'full_reference': 'C Initial 2'
                    }
                ],
                'comment': 'Initial comment.',
                'data_archivals': [
                    {
                        'archival_db_name': 'DA Initial 1',
                        'doi': 'doi://da_initial/1'
                    },
                    {
                        'archival_db_name': 'DA Initial 2',
                        'doi': 'doi://da_initial/2'
                    }
                ],
                'directory': '/mbari/SeafloorMapping/2019/20190308m1',
                'end_date': '2021-04-04T00:00:00',
                'expedition': {
                    'name': 'Initial expedition name'
                },
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
                'kml_filename': 'kml_file.kml',
                'missiontype': {
                    'name': 'Initial missiontype'
                },
                'name': 'Initial',
                'notes_filename': 'file.notes',
                'platform': {
                    'name': 'Initial platform'
                },
                'quality_comment': 'Q',
                'region_name': 'region1',
                'repeat_survey': False,
                'sensors': [
                    {
                        'model_name': 'M',
                        'sensortype': {
                            'name': 'ST1'
                        }
                    }
                ],
                'site_detail': 'site detail',
                'start_date': '2021-03-03T00:00:00',
                'start_depth': 1500.0,
                'start_point': {
                    'coordinates': [
                        -121.893,
                        36.775
                    ],
                    'type': 'Point'
                },
                'thumbnail_filename': 'thumbnail.png',
                'track_length': 24.1,
                'update_status': 5
            }
        }
    }
}

snapshots['test_create_missiontype 1'] = {
    'data': {
        'create_missiontype': {
            'missiontype': {
                'name': 'Initial'
            }
        }
    }
}

snapshots['test_create_missiontype_not_authenticated 1'] = {
    'data': {
        'create_missiontype': None
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 9,
                    'line': 2
                }
            ],
            'message': 'You must be logged in',
            'path': [
                'create_missiontype'
            ]
        }
    ]
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
                'name': 'Dorado',
                'operator_org_name': 'MBARI',
                'platformtype': {
                    'name': 'AUV'
                }
            }
        }
    }
}

snapshots['test_create_platform 2'] = {
    'data': {
        'all_platforms': [
            {
                'name': 'R/V Rachel Carson'
            },
            {
                'name': 'Dorado'
            }
        ]
    }
}

snapshots['test_create_platformtype 1'] = {
    'data': {
        'create_platformtype': {
            'platformtype': {
                'name': 'Initial'
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
                'sensortype': {
                    'name': 'Sonar'
                }
            }
        }
    }
}

snapshots['test_create_sensortype 1'] = {
    'data': {
        'create_sensortype': {
            'sensortype': {
                'name': 'Initial'
            }
        }
    }
}

snapshots['test_delete_citation 1'] = {
    'data': {
        'delete_citation': {
            'citation': None
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 6
                }
            ],
            'message': '"<Citation: doi://123456/hello>" needs to have a value for field "id" before this many-to-many relationship can be used.',
            'path': [
                'delete_citation',
                'citation',
                'missions'
            ]
        }
    ]
}

snapshots['test_delete_compilation 1'] = {
    'data': {
        'delete_compilation': {
            'compilation': {
                'comment': 'Initial comment.',
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
                'name': '/a/dir/name',
                'navadjust_dir_path': '/nav/adjust/path/',
                'path_name': '/a/path/name',
                'proc_datalist_filename': 'proc.datalist-1',
                'thumbnail_filename': 'thumbnail.png',
                'update_status': 10
            }
        }
    }
}

snapshots['test_delete_dataarchival 1'] = {
    'data': {
        'delete_dataarchival': {
            'dataarchival': None
        }
    },
    'errors': [
        {
            'locations': [
                {
                    'column': 25,
                    'line': 6
                }
            ],
            'message': '"<DataArchival: doi://123456/hello>" needs to have a value for field "id" before this many-to-many relationship can be used.',
            'path': [
                'delete_dataarchival',
                'dataarchival',
                'missions'
            ]
        }
    ]
}

snapshots['test_delete_expedition 1'] = {
    'data': {
        'delete_expedition': {
            'expedition': {
                'chiefscientist': {
                    'first_name': 'Walter',
                    'last_name': 'Munk'
                },
                'end_date': '1998-07-20T00:00:00',
                'investigator': {
                    'first_name': 'Henry',
                    'last_name': 'Stommel'
                },
                'name': 'Initial',
                'start_date': '1998-07-01T00:00:00'
            }
        }
    }
}

snapshots['test_delete_mission 1'] = {
    'data': {
        'delete_mission': {
            'mission': {
                'comment': 'Initial comment.',
                'directory': '/mbari/SeafloorMapping/2019/20190308m1',
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
                'kml_filename': 'kml_file.kml',
                'thumbnail_filename': 'thumbnail.png',
                'update_status': 5
            }
        }
    }
}

snapshots['test_delete_missiontype 1'] = {
    'data': {
        'delete_missiontype': {
            'missiontype': {
                'name': 'Initial'
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
                'name': 'Dorado'
            }
        }
    }
}

snapshots['test_delete_platformtype 1'] = {
    'data': {
        'delete_platformtype': {
            'platformtype': {
                'name': 'Initial'
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
                'name': 'Initial'
            }
        }
    }
}

snapshots['test_expedition_by_name 1'] = {
    'data': {
        'expedition_by_name': {
            'name': 'Initial'
        }
    }
}

snapshots['test_expedition_by_name 2'] = {
    'data': {
        'all_expeditions': [
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Testing Terrain Relative Navigation for the Axial Geodesy project and Precisions Controls Project',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Testing Mapping AUV 1',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Mapping AUV Testing in upper Monterey Canyon - 6563',
                'start_date': None
            },
            {
                'end_date': None,
                'name': 'R/V Rachel Carson Morro Bay Expedition - 6570',
                'start_date': None
            },
            {
                'end_date': '1998-07-20T00:00:00',
                'name': 'Initial',
                'start_date': '1998-07-01T00:00:00'
            }
        ]
    }
}

snapshots['test_expedition_by_name_does_not_exist 1'] = {
    'data': {
        'expedition_by_name': None
    }
}

snapshots['test_missiontype_by_name 1'] = {
    'data': {
        'missiontype_by_name': {
            'name': 'Initial'
        }
    }
}

snapshots['test_missiontype_by_name_does_not_exist 1'] = {
    'data': {
        'missiontype_by_name': None
    }
}

snapshots['test_update_citation 1'] = {
    'data': {
        'update_citation': {
            'citation': {
                'doi': 'doi://7890/hello',
                'full_reference': 'Updated Reference',
                'missions': [
                    {
                        'expedition': {
                            'name': 'EN3'
                        },
                        'name': 'M3'
                    },
                    {
                        'expedition': {
                            'name': 'EN4'
                        },
                        'name': 'M4'
                    }
                ]
            }
        }
    }
}

snapshots['test_update_compilation 1'] = {
    'data': {
        'update_compilation': {
            'compilation': {
                'comment': 'Updated comment.',
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
                'name': '/b/dir/name',
                'navadjust_dir_path': '/new/adjust/path/',
                'path_name': '/b/path/name',
                'proc_datalist_filename': 'proc.datalist-2',
                'thumbnail_filename': 'thumbnail2.png',
                'update_status': 10
            }
        }
    }
}

snapshots['test_update_dataarchival 1'] = {
    'data': {
        'update_dataarchival': {
            'dataarchival': {
                'archival_db_name': 'Updated Archival',
                'doi': 'doi://7890/hello',
                'missions': [
                    {
                        'expedition': {
                            'name': 'EN3'
                        },
                        'name': 'M3'
                    },
                    {
                        'expedition': {
                            'name': 'EN4'
                        },
                        'name': 'M4'
                    }
                ]
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
                'investigator': {
                    'first_name': 'John',
                    'last_name': 'Doe'
                },
                'name': 'Updated',
                'start_date': '2020-01-01T00:00:00'
            }
        }
    }
}

snapshots['test_update_mission 1'] = {
    'data': {
        'update_mission': {
            'mission': {
                'citations': [
                    {
                        'doi': 'doi://c_updated/1',
                        'full_reference': 'C Updated 1'
                    },
                    {
                        'doi': 'doi://c_updated/2',
                        'full_reference': 'C Updated 2'
                    }
                ],
                'comment': 'Updates comment.',
                'data_archivals': [
                    {
                        'archival_db_name': 'DA Updated 1',
                        'doi': 'doi://da_updated/1'
                    },
                    {
                        'archival_db_name': 'DA Updated 2',
                        'doi': 'doi://da_updated/2'
                    }
                ],
                'directory': "'/mbari/SeafloorMapping/2019/20190308m2",
                'end_date': '2021-06-06T00:00:00',
                'expedition': {
                    'name': 'Added expedition'
                },
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
                'kml_filename': 'Added kml_file.kml',
                'missiontype': {
                    'name': 'Added missiontype'
                },
                'name': 'Updated',
                'notes_filename': 'file2.notes',
                'platform': {
                    'name': 'Added platform'
                },
                'quality_comment': 'R',
                'region_name': 'region2',
                'repeat_survey': True,
                'sensors': [
                    {
                        'model_name': 'M',
                        'sensortype': {
                            'name': 'T1'
                        }
                    }
                ],
                'site_detail': 'site detail 2',
                'start_date': '2021-05-05T00:00:00',
                'start_depth': 1700.0,
                'start_point': {
                    'coordinates': [
                        -121.993,
                        36.875
                    ],
                    'type': 'Point'
                },
                'thumbnail_filename': 'tumbnail2.png',
                'track_length': 24.2,
                'update_status': 6
            }
        }
    }
}

snapshots['test_update_missiontype 1'] = {
    'data': {
        'update_missiontype': {
            'missiontype': {
                'name': 'Updated'
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
        'all_platforms': [
            {
                'name': 'R/V Rachel Carson'
            },
            {
                'name': 'Dorado'
            }
        ]
    }
}

snapshots['test_update_platform 2'] = {
    'data': {
        'update_platform': {
            'platform': {
                'name': 'Updated',
                'operator_org_name': 'SIO',
                'platformtype': {
                    'name': 'LRAUV'
                }
            }
        }
    }
}

snapshots['test_update_platform 3'] = {
    'data': {
        'all_platforms': [
            {
                'name': 'R/V Rachel Carson'
            },
            {
                'name': 'Updated'
            }
        ]
    }
}

snapshots['test_update_platformtype 1'] = {
    'data': {
        'create_platformtype': {
            'platformtype': {
                'name': 'Initial'
            }
        }
    }
}

snapshots['test_update_platformtype 2'] = {
    'data': {
        'update_platformtype': {
            'platformtype': {
                'name': 'Updated'
            }
        }
    }
}

snapshots['test_update_platformtype 3'] = {
    'data': {
        'all_platformtypes': [
            {
                'name': 'ship'
            },
            {
                'name': 'Updated'
            }
        ]
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
                'name': 'Updated'
            }
        }
    }
}
