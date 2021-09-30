import pytest

from django.core.management import call_command
from smdb.models import Mission, Missiontype, Person, Platformtype
from smdb.users.models import User

from smdb.users.tests.factories import UserFactory

from smdb.tests.factories import MissiontypeFactory, PersonFactory, PlatformtypeFactory

##from smdb.tests.factories import MissionFactory


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Create smdb/smdb/fixtures/missions_notes_5.json thusly:
    1. smdb/manage.py flush
    2. rm /media/thumbnails/*.jpg
    3. smdb/scripts/load.py --bootstrap --notes --clobber --limit 5 --noinput -v
    4. smdb/manage.py dumpdata smdb -o smdb/smdb/fixtures/missions_notes_5.json
    5. Save the .json file from VS Code so that it's formatted for version controlled edits
    6. smdb/manage.py createsuperuser
    See: https://pytest-django.readthedocs.io/en/latest/database.html#populate-the-database-with-initial-test-data
    """
    with django_db_blocker.unblock():
        call_command("loaddata", "missions_notes_5.json")


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def missiontype() -> Missiontype:
    return MissiontypeFactory()


@pytest.fixture
def person() -> Person:
    return PersonFactory()


@pytest.fixture
def platformtype() -> Platformtype:
    return PlatformtypeFactory()


""" Waiting for serialization
@pytest.fixture
def mission() -> Mission:
    return MissionFactory()
"""
