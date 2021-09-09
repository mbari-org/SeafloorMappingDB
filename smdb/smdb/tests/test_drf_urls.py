import pytest
from django.urls import resolve, reverse

from smdb.models import MissionType, Person, PlatformType

pytestmark = pytest.mark.django_db


def test_missiontype_list():
    assert reverse("api:missiontype-list") == "/api/v1/missiontype/"
    assert resolve("/api/v1/missiontype/").view_name == "api:missiontype-list"


def test_missiontype_detail(missiontype: MissionType):
    assert (
        reverse(
            "api:missiontype-detail",
            kwargs={"name": missiontype.name},
        )
        == f"/api/v1/missiontype/{missiontype.name}/"
    )
    assert (
        resolve(f"/api/v1/missiontype/{missiontype.name}/").view_name
        == "api:missiontype-detail"
    )


def test_person_list():
    assert reverse("api:person-list") == "/api/v1/persons/"
    assert resolve("/api/v1/persons/").view_name == "api:person-list"


def test_person_detail(person: Person):
    assert (
        reverse(
            "api:person-detail",
            kwargs={"uuid": person.uuid},
        )
        == f"/api/v1/persons/{person.uuid}/"
    )
    assert resolve(f"/api/v1/persons/{person.uuid}/").view_name == "api:person-detail"


def test_platformtype_list():
    assert reverse("api:platformtype-list") == "/api/v1/platformtype/"
    assert resolve("/api/v1/platformtype/").view_name == "api:platformtype-list"


def test_platformtype_detail(platformtype: PlatformType):
    assert (
        reverse(
            "api:platformtype-detail",
            kwargs={"name": platformtype.name},
        )
        == f"/api/v1/platformtype/{platformtype.name}/"
    )
    assert (
        resolve(f"/api/v1/platformtype/{platformtype.name}/").view_name
        == "api:platformtype-detail"
    )


""" Waiting for proper serialization
def test_mission_list():
    assert reverse("api:mission-list") == "/api/v1/missions/"
    assert resolve("/api/v1/missions/").view_name == "api:mission-list"


def test_mission_detail(mission: Mission):
    assert (
        reverse("api:mission-detail", kwargs={"name": mission.name})
        == f"/api/v1/missions/{mission.name}/"
    )
    assert (
        resolve(f"/api/v1/mission/{mission.name}/").view_name
        == "api:mission-detail"
    )
"""
