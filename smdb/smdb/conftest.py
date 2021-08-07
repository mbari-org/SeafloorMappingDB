import pytest

from smdb.models import MissionType
from smdb.users.models import User

from smdb.users.tests.factories import UserFactory

from smdb.tests.factories import MissionTypeFactory

##from smdb.tests.factories import MissionFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def missiontype() -> MissionType:
    return MissionTypeFactory()


""" Waiting for serialization
@pytest.fixture
def mission() -> Mission:
    return MissionFactory()
"""
