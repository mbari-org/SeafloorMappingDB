import pytest
from django.urls import resolve, reverse

from smdb.models import MissionType, Person, PlatformType

pytestmark = pytest.mark.django_db


def test_missiontype_list():
    assert reverse("api:missiontype-list") == "/api/missiontypes/"
    assert resolve("/api/missiontypes/").view_name == "api:missiontype-list"


def test_missiontype_detail(missiontype: MissionType):
    assert (
        reverse(
            "api:missiontype-detail",
            kwargs={"missiontype_name": missiontype.missiontype_name},
        )
        == f"/api/missiontypes/{missiontype.missiontype_name}/"
    )
    assert (
        resolve(f"/api/missiontypes/{missiontype.missiontype_name}/").view_name
        == "api:missiontype-detail"
    )


def test_person_list():
    assert reverse("api:person-list") == "/api/persons/"
    assert resolve("/api/persons/").view_name == "api:person-list"


def test_person_detail(person: Person):
    assert (
        reverse(
            "api:person-detail",
            kwargs={"uuid": person.uuid},
        )
        == f"/api/persons/{person.uuid}/"
    )
    assert resolve(f"/api/persons/{person.uuid}/").view_name == "api:person-detail"


def test_platformtype_list():
    assert reverse("api:platformtype-list") == "/api/platformtypes/"
    assert resolve("/api/platformtypes/").view_name == "api:platformtype-list"


def test_platformtype_detail(platformtype: PlatformType):
    assert (
        reverse(
            "api:platformtype-detail",
            kwargs={"uuid": platformtype.uuid},
        )
        == f"/api/platformtypes/{platformtype.uuid}/"
    )
    assert (
        resolve(f"/api/platformtypes/{platformtype.uuid}/").view_name
        == "api:platformtype-detail"
    )


""" Waiting for proper serialization
def test_mission_list():
    assert reverse("api:mission-list") == "/api/missions/"
    assert resolve("/api/missions/").view_name == "api:mission-list"


def test_mission_detail(mission: Mission):
    assert (
        reverse("api:mission-detail", kwargs={"mission_name": mission.mission_name})
        == f"/api/missions/{mission.mission_name}/"
    )
    assert (
        resolve(f"/api/mission/{mission.mission_name}/").view_name
        == "api:mission-detail"
    )
"""
