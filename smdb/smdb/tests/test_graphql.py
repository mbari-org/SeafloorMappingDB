# Snapshot testing referenced here: https://docs.graphene-python.org/en/latest/testing/
import pytest
from django.contrib.auth import get_user_model
from graphene.test import Client

from smdb.schema import schema

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_all_missiontypes_empty(snapshot):
    client = Client(schema)
    # This will create a snapshot dir and a snapshot file
    # the first time the test is executed, with the response
    # of the execution.
    snapshot.assert_match(
        client.execute(
            """{ allMissiontypes {
                    uuid
                    missiontypeName
                }}"""
        )
    )
