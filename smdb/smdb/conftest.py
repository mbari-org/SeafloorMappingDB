import pytest

from django.core.management import call_command
from smdb.models import Mission, MissionType, Person, PlatformType
from smdb.users.models import User

from smdb.users.tests.factories import UserFactory

from smdb.tests.factories import MissionTypeFactory, PersonFactory, PlatformTypeFactory

##from smdb.tests.factories import MissionFactory


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "missions_notes_5.json")


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def missiontype() -> MissionType:
    return MissionTypeFactory()


@pytest.fixture
def person() -> Person:
    return PersonFactory()


@pytest.fixture
def platformtype() -> PlatformType:
    return PlatformTypeFactory()


""" Waiting for serialization
@pytest.fixture
def mission() -> Mission:
    return MissionFactory()
"""
