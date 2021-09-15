# Snapshot testing referenced here: https://docs.graphene-python.org/en/latest/testing/
# https://github.com/syrusakbary/snapshottest/#reasons-to-use-this-package
import graphql
import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from graphene.test import Client
from jinja2 import Template

from smdb.models import (
    Compilation,
    Citation,
    DataArchival,
    Expedition,
    Mission,
    Missiontype,
    Note,
    Person,
    Platform,
    Platformtype,
    Sensor,
    Sensortype,
)
from smdb.schema import schema
from smdb.users.models import User

pytestmark = pytest.mark.django_db()


def user_authenticated(anonymous_user=False):
    rf = RequestFactory()
    user, _ = User.objects.get_or_create(username="tester")
    request = rf.post("/graphql/")
    if anonymous_user:
        request.user = AnonymousUser()
    else:
        request.user = user

    return request


# ===== Missiontype Tests =====
create_missiontype_mutation = """mutation {
        create_missiontype(name: "Initial") {
            missiontype {
            name
            }
        }
    }"""


def test_all_missiontypes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_missiontypes {
                    name
                    uuid
                  }
                }"""
        )
    )


def test_create_missiontype_not_authenticated(snapshot):
    client = Client(schema)
    response = client.execute(
        create_missiontype_mutation,
        context_value=user_authenticated(anonymous_user=True),
    )
    snapshot.assert_match(response)
    assert Missiontype.objects.all().count() == 0
    assert "You must be logged in" == response["errors"][0]["message"]


def test_create_missiontype(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_missiontype_mutation, context_value=user_authenticated())
    )
    assert Missiontype.objects.all()[0].name == "Initial"


def test_missiontype_by_name(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation, context_value=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """{
                 missiontype_by_name(name: "Initial") {
                    name
                  }
                }"""
        )
    )
    assert Missiontype.objects.all()[0].name == "Initial"


def test_missiontype_by_name_does_not_exist(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                 missiontype_by_name(name: "DoesNotExist") {
                    name
                  }
                }"""
        )
    )
    assert Missiontype.objects.count() == 0


def test_all_sensortypes(snapshot):
    client = Client(schema)

    client.execute(create_sensortype_mutation, context_value=user_authenticated())
    response = client.execute(
        """{
                all_sensortypes {
                    name
                  }
                }"""
    )
    assert response["data"]["all_sensortypes"][0]["name"] == "Initial"
    snapshot.assert_match(response)


def test_update_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation, context_value=user_authenticated())
    assert Missiontype.objects.all()[0].name == "Initial"
    snapshot.assert_match(
        client.execute(
            """mutation {
                update_missiontype(name: "Initial", new_name: "Updated") {
                    missiontype {
                        name
                    }
                }
            }""",
            context_value=user_authenticated(),
        )
    )
    assert Missiontype.objects.all()[0].name == "Updated"


def test_delete_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation, context_value=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_missiontype(name: "Initial") {
                    missiontype {
                        name
                    }
                }
            }""",
            context_value=user_authenticated(),
        )
    )
    assert Missiontype.objects.all().count() == 0


# ===== Person Tests =====
create_person_template = Template(
    """mutation {
        create_person(input: {
            first_name: "Jane",
            last_name: "Doe",
            institution_name: "MBARI"
        }) {
            person {
                {{ uuid }}
                first_name
                last_name
                institution_name
            }
        }
    }"""
)


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
    create_person_mutation = create_person_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_person_mutation, context_value=user_authenticated())
    )
    assert Person.objects.all()[0].first_name == "Jane"
    assert Person.objects.all()[0].last_name == "Doe"
    assert Person.objects.all()[0].institution_name == "MBARI"


def test_all_persons(snapshot):
    client = Client(schema)
    create_person_mutation = create_person_template.render(uuid="")
    client.execute(create_person_mutation, context_value=user_authenticated())
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
    assert repr(Person.objects.all()[0]) == "<Person: Doe, Jane>"
    snapshot.assert_match(response)


# https://medium.com/@jamesvaresamuel/mutation-and-query-in-graphql-using-python-django-part-2-79d9852a1092
def test_update_person(snapshot):
    client = Client(schema)
    create_person_mutation = create_person_template.render(uuid="uuid")
    response = client.execute(
        create_person_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_person"]["person"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation UpdatePerson($uuid: ID!) {
            update_person(uuid: $uuid, input: {
                first_name: "Jim",
                last_name: "Roe",
                institution_name: "SIO"
            }) {
                person {
                    first_name
                    last_name
                    institution_name
                }
            }
        }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Person.objects.all()[0].first_name == "Jim"
    assert Person.objects.all()[0].last_name == "Roe"
    assert Person.objects.all()[0].institution_name == "SIO"


def test_delete_person(snapshot):
    client = Client(schema)
    create_person_mutation = create_person_template.render(uuid="uuid")
    response = client.execute(
        create_person_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_person"]["person"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeletePerson($uuid: ID!) {
            delete_person(uuid: $uuid) {
                person {
                    first_name
                    last_name
                    institution_name
                }
            }
        }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Person.objects.all().count() == 0


# ===== Platformtype Tests =====
create_platformtype_mutation = """mutation {
        create_platformtype(name: "Initial") {
            platformtype {
                name
            }
        }
    }"""


def test_all_platformtypes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_platformtypes {
                    name
                    uuid
                  }
                }"""
        )
    )


def test_create_platformtype(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_platformtype_mutation, context_value=user_authenticated())
    )
    assert Platformtype.objects.all()[0].name == "Initial"


def test_all_platformtypes(snapshot):
    client = Client(schema)
    client.execute(create_platformtype_mutation, context_value=user_authenticated())
    response = client.execute(
        """{
                all_platformtypes {
                    name
                  }
                }"""
    )
    assert response["data"]["all_platformtypes"][0]["name"] == "Initial"
    assert repr(Platformtype.objects.all()[0]) == "<Platformtype: Initial>"
    snapshot.assert_match(response)


def test_update_platformtype(snapshot):
    client = Client(schema)
    client.execute(create_platformtype_mutation, context_value=user_authenticated())
    assert Platformtype.objects.all()[0].name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation {
                update_platformtype(name: "Initial", new_name: "Updated") {
                    platformtype {
                        name
                    }
                }
            }""",
            context_value=user_authenticated(),
        )
    )
    assert Platformtype.objects.all()[0].name == "Updated"


def test_delete_platformtype(snapshot):
    client = Client(schema)
    client.execute(create_platformtype_mutation, context_value=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_platformtype(name: "Initial") {
                    platformtype {
                        name
                    }
                }
            }""",
            context_value=user_authenticated(),
        )
    )
    assert Platformtype.objects.all().count() == 0


# ===== Platform Tests =====
create_platform_template = Template(
    """mutation {
        create_platform(input: {
            name: "Dorado",
            platformtype: {
                    name: "AUV"
            }
            operator_org_name: "MBARI"
        }) {
            platform {
                {{ uuid }}
                name
                operator_org_name
                platformtype {
                    name
                }
            }
        }
    }"""
)


def test_all_platforms_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_platforms {
                    name
                    uuid
                  }
                }"""
        )
    )


def test_create_platform(snapshot):
    client = Client(schema)
    create_platform_mutation = create_platform_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_platform_mutation, context_value=user_authenticated())
    )
    assert Platform.objects.all()[0].name == "Dorado"
    assert Platform.objects.all()[0].operator_org_name == "MBARI"


def test_all_platforms(snapshot):
    client = Client(schema)
    create_platform_mutation = create_platform_template.render(uuid="")
    client.execute(create_platform_mutation, context_value=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """{
                all_platforms {
                    name
                  }
                }"""
        )
    )
    assert repr(Platform.objects.all()[0]) == "<Platform: Dorado (MBARI)>"


def test_update_platform(snapshot):
    client = Client(schema)
    create_platform_mutation = create_platform_template.render(uuid="uuid")
    response = client.execute(
        create_platform_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_platform"]["platform"]["uuid"]
    assert Platform.objects.all()[0].name == "Dorado"

    snapshot.assert_match(
        client.execute(
            """mutation UpdatePlatform($uuid: ID!) {
                update_platform(uuid: $uuid, input: {
                    name: "Updated",
                    platformtype: {
                            name: "LRAUV"
                    }
                    operator_org_name: "SIO"
                }) {
                    platform {
                        name
                        platformtype {
                            name
                        }
                        operator_org_name
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Platform.objects.all()[0].name == "Updated"
    assert Platform.objects.all()[0].platformtype.name == "LRAUV"
    assert Platform.objects.all()[0].operator_org_name == "SIO"


def test_delete_platform(snapshot):
    client = Client(schema)
    create_platform_mutation = create_platform_template.render(uuid="uuid")
    response = client.execute(
        create_platform_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_platform"]["platform"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeletePlatform($uuid: ID!) {
                delete_platform(uuid: $uuid) {
                    platform {
                        name
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Platform.objects.all().count() == 0


# ===== Sensortype Tests =====
create_sensortype_mutation = """mutation {
        create_sensortype(name: "Initial") {
            sensortype {
                name
            }
        }
    }"""


def test_all_sensortypes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_sensortypes {
                    name
                    uuid
                  }
                }"""
        )
    )


def test_create_sensortype(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(create_sensortype_mutation, context_value=user_authenticated())
    )
    assert Sensortype.objects.all()[0].name == "Initial"


def test_all_sensortypes(snapshot):
    client = Client(schema)
    client.execute(create_sensortype_mutation, context_value=user_authenticated())
    response = client.execute(
        """{
                all_sensortypes {
                    name
                  }
                }"""
    )
    assert response["data"]["all_sensortypes"][0]["name"] == "Initial"
    snapshot.assert_match(response)
    assert repr(Sensortype.objects.all()[0]) == "<Sensortype: Initial>"


def test_update_sensortype(snapshot):
    client = Client(schema)
    client.execute(create_sensortype_mutation, context_value=user_authenticated())
    assert Sensortype.objects.all()[0].name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation {
                update_sensortype(name: "Initial", new_name: "Updated") {
                    sensortype {
                        name
                    }
                }
            }""",
            context_value=user_authenticated(),
        )
    )
    assert Sensortype.objects.all()[0].name == "Updated"


def test_delete_sensortype(snapshot):
    client = Client(schema)
    client.execute(create_sensortype_mutation, context_value=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_sensortype(name: "Initial") {
                    sensortype {
                        name
                    }
                }
            }""",
            context_value=user_authenticated(),
        )
    )
    assert Sensortype.objects.all().count() == 0


# ===== Sensor Tests =====
create_sensor_template = Template(
    """mutation {
        create_sensor(input: {
            sensortype: {
                name: "Sonar"
            },
            model_name: "Initial",
            comment: "Initial comment"
        }) {
            sensor {
                {{ uuid }}
                model_name
                comment
                sensortype {
                    name
                }
            }
        }
    }"""
)


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
    create_sensor_mutation = create_sensor_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_sensor_mutation, context_value=user_authenticated())
    )
    assert Sensor.objects.all()[0].model_name == "Initial"


def test_all_sensors(snapshot):
    client = Client(schema)
    create_sensor_mutation = create_sensor_template.render(uuid="")
    client.execute(create_sensor_mutation, context_value=user_authenticated())
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
    assert repr(Sensor.objects.all()[0]) == "<Sensor: Sonar(Initial)>"


def test_update_sensor(snapshot):
    client = Client(schema)
    create_sensor_mutation = create_sensor_template.render(uuid="uuid")
    response = client.execute(
        create_sensor_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_sensor"]["sensor"]["uuid"]
    assert Sensor.objects.all()[0].model_name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation UpdateSensor($uuid: ID) {
                update_sensor(uuid: $uuid, input: {
                    model_name: "Updated",
                    comment: "New comment"
                }) {
                    sensor {
                        model_name
                        comment
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Sensor.objects.all()[0].model_name == "Updated"
    assert Sensor.objects.all()[0].comment == "New comment"


def test_delete_sensor(snapshot):
    client = Client(schema)
    create_sensor_mutation = create_sensor_template.render(uuid="uuid")
    response = client.execute(
        create_sensor_mutation, context_value=user_authenticated()
    )
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
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Sensor.objects.all().count() == 0


# ===== Expedition Tests =====
create_expedition_template = Template(
    """mutation {
        create_expedition(input: {
            chiefscientist: {first_name: "Walter", last_name: "Munk", institution_name: "SIO"},
            expd_path_name: "/mbari/SeafloorMapping/2019/20190308m1",
            investigator: {first_name: "Henry", last_name: "Stommel", institution_name: "SIO"},
            start_date_iso: "1998-07-01",
            end_date_iso: "1998-07-20",
            name: "Initial"}) {
            expedition {
                {{ uuid }}
                name
                start_date
                end_date
                investigator {
                    first_name
                    last_name
                }
                chiefscientist {
                    first_name
                    last_name
                }
                expd_path_name
            }
        }
    }"""
)


def test_all_expeditions_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_expeditions {
                    name
                    start_date
                    end_date
                    expd_path_name
                  }
                }"""
        )
    )


def test_create_expedition(snapshot):
    client = Client(schema)
    create_expedition_mutation = create_expedition_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_expedition_mutation, context_value=user_authenticated())
    )
    assert Expedition.objects.filter(name="Initial")[0].name == "Initial"


def test_expedition_by_name(snapshot):
    client = Client(schema)
    create_expedition_mutation = create_expedition_template.render(uuid="")
    client.execute(create_expedition_mutation, context_value=user_authenticated())
    snapshot.assert_match(
        client.execute(
            """{
                 expedition_by_name(name: "Initial") {
                    name
                  }
                }"""
        )
    )
    assert Expedition.objects.filter(name="Initial")[0].name == "Initial"


def test_expedition_by_name_does_not_exist(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                 expedition_by_name(name: "DoesNotExist") {
                    name
                  }
                }"""
        )
    )
    # Only the 5 Expeditions loaded by the test fixture
    assert Expedition.objects.count() == 5


def test_all_expeditions(snapshot):
    client = Client(schema)
    create_expedition_mutation = create_expedition_template.render(uuid="")
    client.execute(create_expedition_mutation, context_value=user_authenticated())
    response = client.execute(
        """{
                all_expeditions {
                    name
                    start_date
                    end_date
                    expd_path_name
                  }
                }"""
    )
    assert response["data"]["all_expeditions"][-1]["name"] == "Initial"
    snapshot.assert_match(response)
    assert (
        repr(Expedition.objects.filter(name="Initial")[0])
        == "<Expedition: Initial (/mbari/SeafloorMapping/2019/20190308m1)>"
    )


def test_update_expedition(snapshot):
    client = Client(schema)
    create_expedition_mutation = create_expedition_template.render(uuid="uuid")
    response = client.execute(
        create_expedition_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_expedition"]["expedition"]["uuid"]
    assert Expedition.objects.get(name="Initial").name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation UpdateExpedition($uuid: ID) {
                update_expedition(uuid: $uuid, input: {
                    name: "Updated"
                    start_date_iso: "2020-01-01"
                    end_date_iso: "2021-02-02"
                    investigator: {
                        first_name: "John"
                        last_name: "Doe"
                        institution_name: "Tester"
                    }
                    chiefscientist: {
                        first_name: "Jane"
                        last_name: "Roe"
                        institution_name: "Tester"
                    }
                    expd_path_name: "/a/directory/path"
                }) {
                    expedition {
                        name
                        start_date
                        end_date
                        investigator {
                            first_name
                            last_name
                        }
                        chiefscientist {
                            first_name
                            last_name
                        }
                        expd_path_name
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Expedition.objects.get(name="Updated").name == "Updated"


def test_delete_expedition(snapshot):
    client = Client(schema)
    create_expedition_mutation = create_expedition_template.render(uuid="uuid")
    response = client.execute(
        create_expedition_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_expedition"]["expedition"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeleteExpedition($uuid: ID) {
                delete_expedition(uuid: $uuid) {
                    expedition {
                        name
                        start_date
                        end_date
                        investigator {
                            first_name
                            last_name
                        }
                        chiefscientist {
                            first_name
                            last_name
                        }
                        expd_path_name
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Expedition.objects.filter(name="Initial").count() == 0


# ===== Compilation Tests =====
create_compilation_template = Template(
    """mutation {
        create_compilation(input: {
            comment: "Initial comment.",
            dir_name: "/a/dir/name",
            path_name: "/a/path/name",
            figures_dir_path: "/figures/path",
            grid_bounds: "SRID=4326;POLYGON ((-121.94 36.69, -121.94 36.69, -121.93 36.69, -121.93 36.69, -121.94 36.69))",
            kml_filename: "file.kml",
            navadjust_dir_path: "/nav/adjust/path/",
            proc_datalist_filename: "proc.datalist-1",
            thumbnail_filename: "thumbnail.png",
            update_status: 10}) {
            compilation {
                {{ uuid }}
                comment
                dir_name
                path_name
                figures_dir_path
                grid_bounds
                kml_filename
                navadjust_dir_path
                proc_datalist_filename
                thumbnail_filename
                update_status
            }
        }
    }"""
)
compilation_query = """{
                all_compilations {
                    comment
                    dir_name
                    path_name
                    figures_dir_path
                    grid_bounds
                    kml_filename
                    navadjust_dir_path
                    proc_datalist_filename
                    thumbnail_filename
                    update_status
                  }
                }"""


def test_all_compilations_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(client.execute(compilation_query))


def test_create_compilation(snapshot):
    client = Client(schema)
    create_compilation_mutation = create_compilation_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_compilation_mutation, context_value=user_authenticated())
    )
    assert Compilation.objects.all()[0].comment == "Initial comment."


def test_all_compilations(snapshot):
    client = Client(schema)
    create_compilation_mutation = create_compilation_template.render(uuid="")
    client.execute(create_compilation_mutation, context_value=user_authenticated())
    response = client.execute(compilation_query)
    assert response["data"]["all_compilations"][0]["comment"] == "Initial comment."
    snapshot.assert_match(response)
    assert repr(Compilation.objects.all()[0]) == "<Compilation: /a/dir/name>"


def test_update_compilation(snapshot):
    client = Client(schema)
    create_compilation_mutation = create_compilation_template.render(uuid="uuid")
    response = client.execute(
        create_compilation_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_compilation"]["compilation"]["uuid"]
    assert Compilation.objects.all()[0].comment == "Initial comment."

    snapshot.assert_match(
        client.execute(
            """mutation UpdateCompilation($uuid: ID) {
        update_compilation(uuid: $uuid, input: {
            comment: "Updated comment.",
            dir_name: "/b/dir/name",
            path_name: "/b/path/name",
            figures_dir_path: "/figures/path2",
            grid_bounds: "SRID=4326;POLYGON ((-121.893 36.775, -121.893 36.794, -121.869 36.794, -121.869 36.775, -121.893 36.775))",
            kml_filename: "file2.kml",
            navadjust_dir_path: "/new/adjust/path/",
            proc_datalist_filename: "proc.datalist-2",
            thumbnail_filename: "thumbnail2.png",
            update_status: 10}) {
            compilation {
                comment
                dir_name
                path_name
                figures_dir_path
                grid_bounds
                kml_filename
                navadjust_dir_path
                proc_datalist_filename
                thumbnail_filename
                update_status
            }
        }
    }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Compilation.objects.all()[0].comment == "Updated comment."


def test_delete_compilation(snapshot):
    client = Client(schema)
    create_compilation_mutation = create_compilation_template.render(uuid="uuid")
    response = client.execute(
        create_compilation_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_compilation"]["compilation"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeleteCompilation($uuid: ID) {
                delete_compilation(uuid: $uuid) {
                    compilation {
                        comment
                        dir_name
                        path_name
                        figures_dir_path
                        grid_bounds
                        kml_filename
                        navadjust_dir_path
                        proc_datalist_filename
                        thumbnail_filename
                        update_status
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Compilation.objects.all().count() == 0


# ===== Mission Tests =====
create_mission_template = Template(
    """mutation {
        create_mission(input: {
            name: "Initial",
            grid_bounds: "SRID=4326;POLYGON ((-121.893 36.775, -121.893 36.794, -121.869 36.794, -121.869 36.775, -121.893 36.775))",
            expedition: {name: "Initial expedition name"},
            missiontype: {name: "Initial missiontype"},
            platform: {name: "Initial platform", platformtype: {name: "PT1"}},
            start_date: "2021-03-03",
            end_date: "2021-04-04",
            start_depth: 1500,
            start_point: "SRID=4326;POINT (-121.893 36.775)",
            quality_comment: "Q",
            repeat_survey: false,
            comment: "Initial comment.",
            notes_filename: "file.notes",
            region_name: "region1"
            site_detail: "site detail",
            thumbnail_filename: "thumbnail.png",
            kml_filename: "kml_file.kml",
            compilation: {dir_name: "Initial compilation"},
            update_status: 5,
            sensors: {comment: "C", model_name: "M", sensortype: {name: "ST1"}},
            data_archivals: [ {doi: "doi://da_initial/1", archival_db_name: "DA Initial 1"},
                              {doi: "doi://da_initial/2", archival_db_name: "DA Initial 2"},
                            ],
            citations: [ {doi: "doi://c_initial/1", full_reference: "C Initial 1"},
                         {doi: "doi://c_initial/2", full_reference: "C Initial 2"},
                       ],
            }) {
            mission {
                {{ uuid }}
                name
                grid_bounds
                expedition {
                    name
                }
                missiontype {
                    name
                }
                platform {
                    name
                }
                start_date
                end_date
                start_depth
                start_point
                quality_comment
                repeat_survey
                comment
                notes_filename
                region_name
                site_detail
                thumbnail_filename
                kml_filename
                compilation {
                    dir_name
                }
                update_status
                sensors {
                    sensortype {
                        name
                    }
                    model_name
                }
                data_archivals {
                    doi
                    archival_db_name
                }
                citations {
                    doi
                    full_reference
                }
            }
        }
    }"""
)
mission_query = """{
                all_missions {
                    comment
                    grid_bounds
                    kml_filename
                    thumbnail_filename
                    update_status
                  }
                }"""


def test_all_missions_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(client.execute(mission_query))


def test_create_mission(snapshot):
    client = Client(schema)
    create_mission_mutation = create_mission_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_mission_mutation, context_value=user_authenticated())
    )
    assert Mission.objects.filter(name="Initial")[0].name == "Initial"


def test_all_missions(snapshot):
    client = Client(schema)
    create_mission_mutation = create_mission_template.render(uuid="")
    client.execute(create_mission_mutation, context_value=user_authenticated())
    response = client.execute(mission_query)
    assert Mission.objects.filter(name="Initial")[0].name == "Initial"
    snapshot.assert_match(response)
    assert repr(Mission.objects.filter(name="Initial")[0]) == "<Mission: Initial>"
    # Test the .display_ methods that are used by the Django admin
    assert Mission.objects.filter(name="Initial")[0].display_sensor() == "ST1(M)"
    assert (
        Mission.objects.filter(name="Initial")[0].display_data_archival()
        == "doi://da_initial/1, doi://da_initial/2"
    )
    assert (
        Mission.objects.filter(name="Initial")[0].display_citation()
        == "doi://c_initial/1, doi://c_initial/2"
    )


def test_update_mission(snapshot):
    client = Client(schema)
    create_mission_mutation = create_mission_template.render(uuid="uuid")
    response = client.execute(
        create_mission_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_mission"]["mission"]["uuid"]
    assert Mission.objects.filter(name="Initial")[0].name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation UpdateMission($uuid: ID!) {
                update_mission(uuid: $uuid, input: {
                    name: "Updated",
                    grid_bounds: "SRID=4326;POLYGON ((-121.893 36.775, -121.893 36.794, -121.869 36.794, -121.869 36.775, -121.893 36.775))",
                    expedition: {name: "Added expedition"},
                    missiontype: {name: "Added missiontype"},
                    platform: {name: "Added platform", platformtype: {name: "PT2"}},
                    start_date: "2021-05-05",
                    end_date: "2021-06-06",
                    start_depth: 1700,
                    start_point: "SRID=4326;POINT (-121.993 36.875)",
                    quality_comment: "R",
                    repeat_survey: true,
                    comment: "Updates comment.",
                    notes_filename: "file2.notes",
                    region_name: "region2",
                    site_detail: "site detail 2",
                    thumbnail_filename: "tumbnail2.png",
                    kml_filename: "Added kml_file.kml",
                    compilation: {dir_name: "Updated compilation"},
                    update_status: 6,
                    sensors: {comment: "C", model_name: "M", sensortype: {name: "T1"}},
                    data_archivals: [ {doi: "doi://da_updated/1", archival_db_name: "DA Updated 1"},
                                      {doi: "doi://da_updated/2", archival_db_name: "DA Updated 2"},
                                    ],
                    citations: [ {doi: "doi://c_updated/1", full_reference: "C Updated 1"},
                                 {doi: "doi://c_updated/2", full_reference: "C Updated 2"},
                               ],
                    }) {
                    mission {
                        name
                        grid_bounds
                        expedition {
                            name
                        }
                        missiontype {
                            name
                        }
                        platform {
                            name
                        }
                        start_date
                        end_date
                        start_depth
                        start_point
                        quality_comment
                        repeat_survey
                        comment
                        notes_filename
                        region_name
                        site_detail
                        thumbnail_filename
                        kml_filename
                        compilation {
                            dir_name
                        }
                        update_status
                        sensors {
                            sensortype {
                                name
                            }
                            model_name
                        }
                        data_archivals {
                            doi
                            archival_db_name
                        }
                        citations {
                            doi
                            full_reference
                        }
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Mission.objects.filter(name="Updated")[0].name == "Updated"


def test_delete_mission(snapshot):
    client = Client(schema)
    create_mission_mutation = create_mission_template.render(uuid="uuid")
    response = client.execute(
        create_mission_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_mission"]["mission"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeleteMission($uuid: ID) {
                delete_mission(uuid: $uuid) {
                    mission {
                        comment
                        grid_bounds
                        kml_filename
                        thumbnail_filename
                        update_status
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Mission.objects.filter(name="Initial").count() == 0


# ===== DataArchival Tests =====
create_dataarchival_template = Template(
    """mutation {
        create_dataarchival(input: {
            doi: "doi://123456/hello",
            archival_db_name: "Initial Archival",
            missions: [ {name: "M1", expedition: {name: "EN1", expd_path_name: "PN1"}},
                        {name: "M2", expedition: {name: "EN2", expd_path_name: "PN2"}},
                      ],
            }) {
            dataarchival {
                {{ uuid }}
                doi
                archival_db_name
                missions {
                    name
                    expedition {
                        name
                        expd_path_name
                    }
                }
            }
        }
    }"""
)
dataarchival_query = """{
                all_dataarchivals {
                    doi
                    archival_db_name
                    missions {
                        name
                        expedition {
                            name
                            expd_path_name
                        }
                    }
                  }
                }"""


def test_all_dataarchivals_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(client.execute(dataarchival_query))


def test_create_dataarchival(snapshot):
    client = Client(schema)
    create_dataarchival_mutation = create_dataarchival_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_dataarchival_mutation, context_value=user_authenticated())
    )
    assert DataArchival.objects.all()[0].doi == "doi://123456/hello"
    assert DataArchival.objects.all()[0].missions.all()[0].name == "M1"
    assert DataArchival.objects.all()[0].missions.all()[1].name == "M2"


def test_all_dataarchivals(snapshot):
    client = Client(schema)
    create_dataarchival_mutation = create_dataarchival_template.render(uuid="")
    client.execute(create_dataarchival_mutation, context_value=user_authenticated())
    response = client.execute(dataarchival_query)
    assert DataArchival.objects.all()[0].doi == "doi://123456/hello"
    snapshot.assert_match(response)


def test_update_dataarchival(snapshot):
    client = Client(schema)
    create_dataarchival_mutation = create_dataarchival_template.render(uuid="uuid")
    response = client.execute(
        create_dataarchival_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_dataarchival"]["dataarchival"]["uuid"]
    assert DataArchival.objects.all()[0].doi == "doi://123456/hello"

    snapshot.assert_match(
        client.execute(
            """mutation UpdateDataArchival($uuid: ID!) {
                update_dataarchival(uuid: $uuid, input: {
                    doi: "doi://7890/hello",
                    archival_db_name: "Updated Archival",
                    missions: [ {name: "M3", expedition: {name: "EN3", expd_path_name: "PN3"}},
                                {name: "M4", expedition: {name: "EN4", expd_path_name: "PN4"}},
                            ],
                    }) {
                    dataarchival {
                        doi
                        archival_db_name
                        missions {
                            name
                            expedition {
                                name
                                expd_path_name
                            }
                        }
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert DataArchival.objects.all()[0].doi == "doi://7890/hello"
    assert DataArchival.objects.all()[0].missions.all()[0].name == "M3"
    assert DataArchival.objects.all()[0].missions.all()[1].name == "M4"


def test_delete_dataarchival(snapshot):
    client = Client(schema)
    create_dataarchival_mutation = create_dataarchival_template.render(uuid="uuid")
    response = client.execute(
        create_dataarchival_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_dataarchival"]["dataarchival"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeleteDataArchival($uuid: ID) {
                delete_dataarchival(uuid: $uuid) {
                    dataarchival {
                        doi
                        archival_db_name
                        missions {
                            name
                            expedition {
                                name
                                expd_path_name
                            }
                        }
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert DataArchival.objects.count() == 0


# ===== Citation Tests =====
create_citation_template = Template(
    """mutation {
        create_citation(input: {
            doi: "doi://123456/hello",
            full_reference: "Initial Reference",
            missions: [ {name: "M1", expedition: {name: "EN1", expd_path_name: "PN1"}},
                        {name: "M2", expedition: {name: "EN2", expd_path_name: "PN2"}},
                      ],
            }) {
            citation {
                {{ uuid }}
                doi
                full_reference
                missions {
                    name
                    expedition {
                        name
                        expd_path_name
                    }
                }
            }
        }
    }"""
)
citation_query = """{
                all_citations {
                    doi
                    full_reference
                    missions {
                        name
                        expedition {
                            name
                            expd_path_name
                        }
                    }
                  }
                }"""


def test_all_citations_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(client.execute(citation_query))


def test_create_citation(snapshot):
    client = Client(schema)
    create_citation_mutation = create_citation_template.render(uuid="")
    snapshot.assert_match(
        client.execute(create_citation_mutation, context_value=user_authenticated())
    )
    assert Citation.objects.all()[0].doi == "doi://123456/hello"


def test_all_citations(snapshot):
    client = Client(schema)
    create_citation_mutation = create_citation_template.render(uuid="")
    client.execute(create_citation_mutation, context_value=user_authenticated())
    response = client.execute(citation_query)
    assert Citation.objects.all()[0].doi == "doi://123456/hello"
    snapshot.assert_match(response)


def test_update_citation(snapshot):
    client = Client(schema)
    create_citation_mutation = create_citation_template.render(uuid="uuid")
    response = client.execute(
        create_citation_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_citation"]["citation"]["uuid"]
    assert Citation.objects.all()[0].doi == "doi://123456/hello"

    snapshot.assert_match(
        client.execute(
            """mutation UpdateCitation($uuid: ID!) {
                update_citation(uuid: $uuid, input: {
                    doi: "doi://7890/hello",
                    full_reference: "Updated Reference",
                    missions: [ {name: "M3", expedition: {name: "EN3", expd_path_name: "PN3"}},
                                {name: "M4", expedition: {name: "EN4", expd_path_name: "PN4"}},
                            ],
                    }) {
                    citation {
                        doi
                        full_reference
                        missions {
                            name
                            expedition {
                                name
                                expd_path_name
                            }
                        }
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Citation.objects.all()[0].doi == "doi://7890/hello"


def test_delete_citation(snapshot):
    client = Client(schema)
    create_citation_mutation = create_citation_template.render(uuid="uuid")
    response = client.execute(
        create_citation_mutation, context_value=user_authenticated()
    )
    uuid = response["data"]["create_citation"]["citation"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeleteCitation($uuid: ID) {
                delete_citation(uuid: $uuid) {
                    citation {
                        doi
                        full_reference
                        missions {
                            name
                            expedition {
                                name
                                expd_path_name
                            }
                        }
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    assert Citation.objects.count() == 0


# ===== Note Tests =====
multi_line_text = (
    """Here is some text that may be in a Note.\nAnd another line of text."""
)
create_note_template = Template(
    """mutation CreateNote($text: String!) {
        create_note(input: {
            text: $text
            mission: {name: "Mn1_test", expedition: {name: "ENn1", expd_path_name: "PNn1"}},
            }) {
            note {
                {{ uuid }}
                text
                mission {
                    name
                    expedition {
                        name
                        expd_path_name
                    }
                }
            }
        }
    }"""
)
# Do not return verbose text from 5 Missions in text fixture
note_query = """{
                all_notes {
                    mission {
                        name
                        expedition {
                            name
                            expd_path_name
                        }
                    }
                  }
                }"""


def test_all_notes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(client.execute(note_query))


def test_create_note(snapshot):
    client = Client(schema)
    create_note_mutation = create_note_template.render(uuid="")
    snapshot.assert_match(
        client.execute(
            create_note_mutation,
            variable_values={"text": multi_line_text},
            context_value=user_authenticated(),
        )
    )
    assert Note.objects.filter(mission__name="Mn1_test")[0].text.startswith(
        "Here is some text"
    )


def test_all_notes(snapshot):
    client = Client(schema)
    create_note_mutation = create_note_template.render(uuid="")
    client.execute(
        create_note_mutation,
        variable_values={"text": multi_line_text},
        context_value=user_authenticated(),
    )
    response = client.execute(note_query)
    assert Note.objects.filter(mission__name="Mn1_test")[0].text.startswith(
        "Here is some text"
    )
    snapshot.assert_match(response)
    assert (
        repr(Note.objects.filter(mission__name="Mn1_test")[0])
        == "<Note: Notes for Mn1_test>"
    )


def test_update_note(snapshot):
    client = Client(schema)
    create_note_mutation = create_note_template.render(uuid="uuid")
    response = client.execute(
        create_note_mutation,
        variable_values={"text": multi_line_text},
        context_value=user_authenticated(),
    )
    uuid = response["data"]["create_note"]["note"]["uuid"]

    snapshot.assert_match(
        client.execute(
            """mutation UpdateNote($uuid: ID!, $text: String!) {
                update_note(uuid: $uuid, input: {
                    text: $text,
                    mission: {name: "Mn1_updated", expedition: {name: "EN3", expd_path_name: "PN3"}},
                    }) {
                    note {
                        text
                        mission {
                            name
                            expedition {
                                name
                                expd_path_name
                            }
                        }
                    }
                }
            }""",
            variable_values={"uuid": uuid, "text": "Updated single line of text."},
            context_value=user_authenticated(),
        )
    )
    assert (
        Note.objects.filter(mission__name="Mn1_updated")[0].text
        == "Updated single line of text."
    )


def test_delete_note(snapshot):
    client = Client(schema)
    create_note_mutation = create_note_template.render(uuid="uuid")
    response = client.execute(
        create_note_mutation,
        variable_values={"text": multi_line_text},
        context_value=user_authenticated(),
    )
    uuid = response["data"]["create_note"]["note"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeleteNote($uuid: ID) {
                delete_note(uuid: $uuid) {
                    note {
                        text
                        mission {
                            name
                            expedition {
                                name
                                expd_path_name
                            }
                        }
                    }
                }
            }""",
            variable_values={"uuid": uuid},
            context_value=user_authenticated(),
        )
    )
    # Initial number of Notes from the text fixture
    assert Note.objects.count() == 5
