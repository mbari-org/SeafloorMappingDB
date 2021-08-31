# Snapshot testing referenced here: https://docs.graphene-python.org/en/latest/testing/
# https://github.com/syrusakbary/snapshottest/#reasons-to-use-this-package

import json

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from graphene.test import Client

from smdb.models import MissionType, Person, Platform, PlatformType, Sensor, SensorType
from smdb.schema import schema
from smdb.users.models import User

pytestmark = pytest.mark.django_db


def user_authenticated():
    rf = RequestFactory()
    user, _ = User.objects.get_or_create(username="tester")
    request = rf.post("/graphql/")
    request.user = user

    return request


# ===== MissionType Tests =====
create_missiontype_mutation = """mutation {
        create_missiontype(missiontype_name: "Initial") {
            missiontype {
            missiontype_name
            }
        }
    }"""


def test_all_missiontypes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_missiontypes {
                    missiontype_name
                    uuid
                  }
                }"""
        )
    )


def test_create_missiontype(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_missiontype_mutation, context=user_authenticated())
    )
    assert MissionType.objects.all()[0].missiontype_name == "Initial"


def test_all_sensortypes(snapshot):
    client = Client(schema)
    client.execute(create_sensortype_mutation, context=user_authenticated())
    response = client.execute(
        """{
                all_sensortypes {
                    sensortype_name
                  }
                }"""
    )
    assert response["data"]["all_sensortypes"][0]["sensortype_name"] == "Initial"
    snapshot.assert_match(response)


def test_update_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation, context=user_authenticated())
    assert MissionType.objects.all()[0].missiontype_name == "Initial"

    update_missiontype_mutation = """mutation {
                update_missiontype(missiontype_name: "Initial", new_missiontype_name: "Updated") {
                    missiontype {
                        missiontype_name
                    }
                }
            }"""
    ##breakpoint()
    ##result = client.execute(update_missiontype_mutation, context=user_authenticated())
    ##breakpoint()
    snapshot.assert_match(
        client.execute(
            """mutation {
                update_missiontype(missiontype_name: "Initial", new_missiontype_name: "Updated") {
                    missiontype {
                        missiontype_name
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert MissionType.objects.all()[0].missiontype_name == "Updated"


def test_delete_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation, context=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_missiontype(missiontype_name: "Initial") {
                    missiontype {
                        missiontype_name
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert MissionType.objects.all().count() == 0


# ===== Person Tests =====
create_person_mutation = """mutation {
        create_person(first_name: "Jane", last_name: "Doe", institution_name: "MBARI") {
            person {
                first_name
                last_name
               institution_name
            }
        }
    }"""

create_person_mutation_uuid = """mutation {
        create_person(first_name: "Jane", last_name: "Doe", institution_name: "MBARI") {
            person {
                uuid
            }
        }
    }"""


def test_all_persons_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_persons {
                    uuid
                    first_name
                    last_name
                    institution_name
                  }
                }"""
        )
    )


def test_create_person(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_person_mutation, context=user_authenticated())
    )
    assert Person.objects.all()[0].first_name == "Jane"
    assert Person.objects.all()[0].last_name == "Doe"
    assert Person.objects.all()[0].institution_name == "MBARI"


def test_all_persons(snapshot):
    client = Client(schema)
    client.execute(create_person_mutation, context=user_authenticated())
    response = client.execute(
        """{
                all_persons {
                    first_name
                    last_name
                    institution_name
                  }
                }"""
    )
    assert response["data"]["all_persons"][0]["first_name"] == "Jane"
    assert response["data"]["all_persons"][0]["last_name"] == "Doe"
    assert response["data"]["all_persons"][0]["institution_name"] == "MBARI"
    snapshot.assert_match(response)


# https://medium.com/@jamesvaresamuel/mutation-and-query-in-graphql-using-python-django-part-2-79d9852a1092
def test_update_person(snapshot):
    client = Client(schema)
    response = client.execute(create_person_mutation_uuid, context=user_authenticated())
    uuid = response["data"]["create_person"]["person"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation UpdatePerson($uuid: String!) {
            update_person(uuid: $uuid, first_name: "Jim", last_name: "Roe", institution_name: "SIO") {
                person {
                    first_name
                    last_name
                    institution_name
                }
            }
        }""",
            variables={"uuid": uuid},
            context=user_authenticated(),
        )
    )
    assert Person.objects.all()[0].first_name == "Jim"
    assert Person.objects.all()[0].last_name == "Roe"
    assert Person.objects.all()[0].institution_name == "SIO"


def test_delete_person(snapshot):
    client = Client(schema)
    response = client.execute(create_person_mutation_uuid, context=user_authenticated())
    uuid = response["data"]["create_person"]["person"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeletePerson($uuid: String!) {
            delete_person(uuid: $uuid) {
                person {
                    first_name
                    last_name
                    institution_name
                }
            }
        }""",
            variables={"uuid": uuid},
            context=user_authenticated(),
        )
    )
    assert Person.objects.all().count() == 0


# ===== PlatformType Tests =====
create_platformtype_mutation = """mutation {
        create_platformtype(platformtype_name: "Initial") {
            platformtype {
                platformtype_name
            }
        }
    }"""


def test_all_platformtypes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_platformtypes {
                    platformtype_name
                    uuid
                  }
                }"""
        )
    )


def test_create_platformtype(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_platformtype_mutation, context=user_authenticated())
    )
    assert PlatformType.objects.all()[0].platformtype_name == "Initial"


def test_all_platformtypes(snapshot):
    client = Client(schema)
    client.execute(create_platformtype_mutation, context=user_authenticated())
    response = client.execute(
        """{
                all_platformtypes {
                    platformtype_name
                  }
                }"""
    )
    assert response["data"]["all_platformtypes"][0]["platformtype_name"] == "Initial"
    snapshot.assert_match(response)


def test_update_platformtype(snapshot):
    client = Client(schema)
    client.execute(create_platformtype_mutation, context=user_authenticated())
    assert PlatformType.objects.all()[0].platformtype_name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation {
                update_platformtype(platformtype_name: "Initial", new_platformtype_name: "Updated") {
                    platformtype {
                        platformtype_name
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert PlatformType.objects.all()[0].platformtype_name == "Updated"


def test_delete_platformtype(snapshot):
    client = Client(schema)
    client.execute(create_platformtype_mutation, context=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_platformtype(platformtype_name: "Initial") {
                    platformtype {
                        platformtype_name
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert PlatformType.objects.all().count() == 0


# ===== Platform Tests =====
create_platform_mutation = """mutation {
        create_platform(input: {
            platform_name: "Dorado",
            platformtypes: [
                {
                    platformtype_name: "AUV"
                }
            ]
            operator_org_name: "MBARI"
        }) {
            platform {
                uuid
                platform_name
                operator_org_name
                platform_type {
                    platformtype_name
                }
            }
        }
    }"""


def test_all_platforms_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_platforms {
                    platform_name
                    uuid
                  }
                }"""
        )
    )


def test_create_platform(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_platform_mutation, context=user_authenticated())
    )
    assert Platform.objects.all()[0].platform_name == "Dorado"
    assert Platform.objects.all()[0].operator_org_name == "MBARI"


def test_update_platform(snapshot):
    client = Client(schema)
    response = client.execute(create_platform_mutation, context=user_authenticated())
    uuid = response["data"]["create_platform"]["platform"]["uuid"]
    assert Platform.objects.all()[0].platform_name == "Dorado"

    snapshot.assert_match(
        client.execute(
            """mutation UpdatePlatform($uuid: ID!) {
                update_platform(uuid: $uuid, input: {
                    platform_name: "Updated",
                    platformtypes: [
                        {
                            platformtype_name: "LRAUV"
                        }
                    ]
                    operator_org_name: "SIO"
                }) {
                    platform {
                        platform_name
                        platform_type {
                            platformtype_name
                        }
                        operator_org_name
                    }
                }
            }""",
            variables={"uuid": uuid},
            context=user_authenticated(),
        )
    )
    assert Platform.objects.all()[0].platform_name == "Updated"
    assert Platform.objects.all()[0].platform_type.platformtype_name == "LRAUV"
    assert Platform.objects.all()[0].operator_org_name == "SIO"


def test_delete_platform(snapshot):
    client = Client(schema)
    client.execute(create_platform_mutation, context=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_platform(platform_name: "Dorado") {
                    platform {
                        platform_name
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert Platform.objects.all().count() == 0


# ===== SensorType Tests =====
create_sensortype_mutation = """mutation {
        create_sensortype(sensortype_name: "Initial") {
            sensortype {
                sensortype_name
            }
        }
    }"""


def test_all_sensortypes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_sensortypes {
                    sensortype_name
                    uuid
                  }
                }"""
        )
    )


def test_create_sensortype(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_sensortype_mutation, context=user_authenticated())
    )
    assert SensorType.objects.all()[0].sensortype_name == "Initial"


def test_all_sensortypes(snapshot):
    client = Client(schema)
    client.execute(create_sensortype_mutation, context=user_authenticated())
    response = client.execute(
        """{
                all_sensortypes {
                    sensortype_name
                  }
                }"""
    )
    assert response["data"]["all_sensortypes"][0]["sensortype_name"] == "Initial"
    snapshot.assert_match(response)


def test_update_sensortype(snapshot):
    client = Client(schema)
    client.execute(create_sensortype_mutation, context=user_authenticated())
    assert SensorType.objects.all()[0].sensortype_name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation {
                update_sensortype(sensortype_name: "Initial", new_sensortype_name: "Updated") {
                    sensortype {
                        sensortype_name
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert SensorType.objects.all()[0].sensortype_name == "Updated"


def test_delete_sensortype(snapshot):
    client = Client(schema)
    client.execute(create_sensortype_mutation, context=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_sensortype(sensortype_name: "Initial") {
                    sensortype {
                        sensortype_name
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert SensorType.objects.all().count() == 0


# ===== Sensor Tests =====
create_sensor_mutation = """mutation {
        create_sensor(input: {
            sensortypes: [
                {
                    sensortype_name: "Sonar"
                }
            ],
            model_name: "Initial",
            comment: "Initial comment"
        }) {
            sensor {
                uuid
                model_name
                comment
                sensor_type {
                    sensortype_name
                }
            }
        }
    }"""


def test_all_sensors_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_sensors {
                    uuid
                    model_name
                    comment
                  }
                }"""
        )
    )


def test_create_sensor(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_sensor_mutation, context=user_authenticated())
    )
    assert Sensor.objects.all()[0].model_name == "Initial"


def test_all_sensors(snapshot):
    client = Client(schema)
    client.execute(create_sensor_mutation, context=user_authenticated())
    response = client.execute(
        """{
                all_sensors {
                    model_name
                    comment
                  }
                }"""
    )
    assert response["data"]["all_sensors"][0]["model_name"] == "Initial"
    snapshot.assert_match(response)


def test_update_sensor(snapshot):
    client = Client(schema)
    response = client.execute(create_sensor_mutation, context=user_authenticated())
    uuid = response["data"]["create_sensor"]["sensor"]["uuid"]
    assert Sensor.objects.all()[0].model_name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation UpdateSensor($uuid: ID) {
                update_sensor(uuid: $uuid, model_name: "Updated", comment: "New comment") {
                    sensor {
                        model_name
                        comment
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert Sensor.objects.all()[0].model_name == "Updated"
    assert Sensor.objects.all()[0].comment == "New comment"


def test_delete_sensor(snapshot):
    client = Client(schema)
    response = client.execute(create_sensor_mutation, context=user_authenticated())
    uuid = response["data"]["create_sensor"]["sensor"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeleteSensor($uuid: ID) {
                delete_sensor(uuid: $uuid) {
                    sensor {
                        model_name
                        comment
                    }
                }
            }""",
            context=user_authenticated(),
        )
    )
    assert Sensor.objects.all().count() == 0
