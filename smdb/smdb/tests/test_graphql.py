# Snapshot testing referenced here: https://docs.graphene-python.org/en/latest/testing/
# https://github.com/syrusakbary/snapshottest/#reasons-to-use-this-package

import pytest
from graphene.test import Client

from smdb.models import MissionType
from smdb.schema import schema

pytestmark = pytest.mark.django_db

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
    snapshot.assert_match(client.execute(create_missiontype_mutation))
    assert MissionType.objects.all()[0].missiontype_name == "Initial"


@pytest.mark.django_db
def test_update_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation)
    assert MissionType.objects.all()[0].missiontype_name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation {
                update_missiontype(missiontype_name: "Initial", new_missiontype_name: "Updated") {
                    missiontype {
                    missiontype_name
                    }
                }
            }"""
        )
    )
    assert MissionType.objects.all()[0].missiontype_name == "Updated"


def test_delete_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation)
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_missiontype(missiontype_name: "Initial") {
                    missiontype {
                    missiontype_name
                    }
                }
            }"""
        )
    )
    assert MissionType.objects.all().count() == 0
