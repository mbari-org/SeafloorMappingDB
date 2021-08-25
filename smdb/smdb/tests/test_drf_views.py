import json
from typing import Any, Dict

import pytest
from django.urls import reverse
from pytest_assert_utils import assert_model_attrs
from pytest_common_subject import precondition_fixture
from pytest_drf import (
    AsUser,
    Returns200,
    Returns201,
    Returns204,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import pluralized, url_for
from pytest_lambda import lambda_fixture, static_fixture
from rest_framework.test import APIRequestFactory

from smdb.models import MissionType, Person, PlatformType
from smdb.users.models import User

pytestmark = pytest.mark.django_db

tester = lambda_fixture(
    lambda: User.objects.create(
        username="tester",
    )
)


def express_missiontype(missiontype: MissionType) -> Dict[str, Any]:
    factory = APIRequestFactory()
    request = factory.get("api:missiontype-detail")
    return {
        "missiontype_name": missiontype.missiontype_name,
        "url": request.build_absolute_uri(
            reverse(
                "api:missiontype-detail",
                kwargs={"missiontype_name": missiontype.missiontype_name},
            )
        ),
    }


express_missiontypes = pluralized(express_missiontype)


def express_platformtype(platformtype: PlatformType) -> Dict[str, Any]:
    factory = APIRequestFactory()
    request = factory.get("api:platformtype-detail")
    return {
        "platformtype_name": platformtype.platformtype_name,
        "url": request.build_absolute_uri(
            reverse(
                "api:platformtype-detail",
                kwargs={"platformtype_name": platformtype.platformtype_name},
            )
        ),
    }


express_platformtypes = pluralized(express_platformtype)


def express_person(person: Person) -> Dict[str, Any]:
    factory = APIRequestFactory()
    request = factory.get("api:person-detail")
    return {
        "uuid": str(person.uuid),
        "first_name": person.first_name,
        "last_name": person.last_name,
        "institution_name": person.institution_name,
        "url": request.build_absolute_uri(
            reverse(
                "api:person-detail",
                kwargs={"uuid": str(person.uuid)},
            )
        ),
    }


express_persons = pluralized(express_person)


class TestMissionTypeViewSet(ViewSetTest, AsUser("tester")):
    """Modeled after 'But I mainly use ViewSets, not APIViews!'
    section at https://pypi.org/project/pytest-drf/"""

    @pytest.fixture
    def results(self, json):
        """Override 'return json["results"]' in
        /usr/local/lib/python3.8/dist-packages/pytest_drf/views.py"""
        return json

    list_url = lambda_fixture(lambda: url_for("api:missiontype-list"))

    detail_url = lambda_fixture(
        lambda missiontype: url_for(
            "api:missiontype-detail", missiontype.missiontype_name
        )
    )

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        missiontypes = lambda_fixture(
            lambda: [
                MissionType.objects.create(missiontype_name=name)
                for name in ("cruise", "dive", "flight")
            ],
            autouse=True,
        )

        def it_returns_missiontypes(self, missiontypes, results):
            expected = express_missiontypes(
                sorted(
                    missiontypes, key=lambda missiontype: missiontype.missiontype_name
                )
            )
            actual = results
            assert expected == actual

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        """missiontype_name is unique so can use it for lookups"""

        data = static_fixture(
            {
                "missiontype_name": "cruise",
            }
        )
        initial_missiontype = precondition_fixture(
            lambda: set(MissionType.objects.values_list("missiontype_name", flat=True))
        )

        def it_creates_new_missiontype(self, initial_missiontype, json):
            expected = initial_missiontype | {json["missiontype_name"]}
            actual = set(MissionType.objects.values_list("missiontype_name", flat=True))
            assert expected == actual

        def it_sets_expected_attrs(self, data, json):
            missiontype = MissionType.objects.get(
                missiontype_name=json["missiontype_name"]
            )

            expected = data
            assert_model_attrs(missiontype, expected)

        def it_returns_missiontype(self, json):
            missiontype = MissionType.objects.get(
                missiontype_name=json["missiontype_name"]
            )

            expected = express_missiontype(missiontype)
            actual = json
            assert expected == actual

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        missiontype = lambda_fixture(
            lambda: MissionType.objects.create(missiontype_name="dive")
        )

        def it_returns_missiontype(self, missiontype, json):
            expected = express_missiontype(missiontype)
            actual = json
            assert expected == actual

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        missiontype = lambda_fixture(
            lambda: MissionType.objects.create(missiontype_name="dive")
        )
        data = static_fixture(
            {
                "missiontype_name": "updated missiontype_name",
            }
        )

        def it_sets_expected_attrs(self, data, missiontype):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            missiontype.refresh_from_db()

            expected = data
            assert_model_attrs(missiontype, expected)

        def it_returns_missiontype(self, missiontype, json):
            missiontype.refresh_from_db()

            expected = express_missiontype(missiontype)
            actual = json
            assert expected == actual

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        missiontype = lambda_fixture(
            lambda: MissionType.objects.create(missiontype_name="dive_to_delete")
        )

        initial_missiontype = precondition_fixture(
            lambda missiontype: set(  # ensure our to-be-deleted MissionType exists in our set
                MissionType.objects.values_list("missiontype_name", flat=True)
            )
        )

        def it_deletes_missiontype(self, initial_missiontype, missiontype):
            expected = initial_missiontype - {missiontype.missiontype_name}
            actual = set(MissionType.objects.values_list("missiontype_name", flat=True))
            assert expected == actual


class TestPersonViewSet(ViewSetTest, AsUser("tester")):
    """Modeled after 'But I mainly use ViewSets, not APIViews!'
    section at https://pypi.org/project/pytest-drf/"""

    @pytest.fixture
    def results(self, json):
        """Override 'return json["results"]' in
        /usr/local/lib/python3.8/dist-packages/pytest_drf/views.py"""
        return json

    list_url = lambda_fixture(lambda: url_for("api:person-list"))

    detail_url = lambda_fixture(
        lambda person: url_for("api:person-detail", str(person.uuid))
    )

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        persons = lambda_fixture(
            lambda: [
                Person.objects.create(
                    first_name=fn, last_name=ln, institution_name=inst
                )
                for fn, ln, inst in (("Joe", "Bloe", "SIO"), ("Jane", "Doe", "WHOI"))
            ],
            autouse=True,
        )

        def it_returns_persons(self, persons, results):
            expected = express_persons(
                sorted(persons, key=lambda person: str(person.uuid))
            )
            actual = sorted(results, key=lambda k: k["uuid"])
            assert expected == actual

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        """Use uuid for lookups"""

        data = static_fixture(
            {
                "first_name": "Tom",
                "last_name": "Cruise",
                "institution_name": "Hollywood",
            }
        )
        initial_person = precondition_fixture(
            lambda: set(Person.objects.values_list("uuid", flat=True))
        )

        def it_creates_new_person(self, initial_person, json):
            expected = initial_person | {json["uuid"]}
            actual = set((str(Person.objects.values_list("uuid", flat=True)[0]),))
            assert expected == actual

        def a_test_it_sets_expected_attrs(self, data, json):
            person = Person.objects.get(uuid=json["uuid"])

            expected = data
            breakpoint()
            # E         Extra items in the right set:
            # E         UUID('968e03be-9b7d-4cf5-95a6-4377a9796479')
            assert_model_attrs(person, expected)

        def it_returns_person(self, json):
            person = Person.objects.get(uuid=json["uuid"])

            expected = express_person(person)
            actual = json
            assert expected == actual

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        person = lambda_fixture(
            lambda: Person.objects.create(
                first_name="Mike", last_name="McCann", institution_name="MBARI"
            )
        )

        def it_returns_person(self, person, json):
            expected = express_person(person)
            actual = json
            assert expected == actual

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        person = lambda_fixture(
            lambda: Person.objects.create(
                first_name="Mike", last_name="McCann", institution_name="MBARI"
            )
        )
        data = static_fixture(
            {
                "first_name": "Tim",
                "last_name": "Cruiser",
                "institution_name": "Stanford",
            }
        )

        def it_sets_expected_attrs(self, data, person):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            person.refresh_from_db()

            expected = data
            assert_model_attrs(person, expected)

        def it_returns_person(self, person, json):
            person.refresh_from_db()

            expected = express_person(person)
            actual = json
            assert expected == actual

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        person = lambda_fixture(
            lambda: Person.objects.create(
                first_name="Mike", last_name="McCann", institution_name="MBARI"
            )
        )

        initial_person = precondition_fixture(
            lambda person: set(  # ensure our to-be-deleted Person exists in our set
                Person.objects.values_list("uuid", flat=True)
            )
        )

        def it_deletes_person(self, initial_person, person):
            expected = initial_person - {person.uuid}
            actual = set(Person.objects.values_list("uuid", flat=True))
            assert expected == actual


class TestPlatformTypeViewSet(ViewSetTest, AsUser("tester")):
    """Modeled after 'But I mainly use ViewSets, not APIViews!'
    section at https://pypi.org/project/pytest-drf/"""

    @pytest.fixture
    def results(self, json):
        """Override 'return json["results"]' in
        /usr/local/lib/python3.8/dist-packages/pytest_drf/views.py"""
        return json

    list_url = lambda_fixture(lambda: url_for("api:platformtype-list"))

    detail_url = lambda_fixture(
        lambda platformtype: url_for(
            "api:platformtype-detail", str(platformtype.platformtype_name)
        )
    )

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        platformtypes = lambda_fixture(
            lambda: [
                PlatformType.objects.create(platformtype_name="AUV"),
                PlatformType.objects.create(platformtype_name="ship"),
            ],
            autouse=True,
        )

        def it_returns_platformtypes(self, platformtypes, results):
            expected = express_platformtypes(
                sorted(
                    platformtypes,
                    key=lambda platformtype: platformtype.platformtype_name,
                )
            )
            actual = sorted(results, key=lambda k: k["platformtype_name"])

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        """Use platformtype_name for lookups"""

        data = static_fixture(
            {
                "platformtype_name": "ROV",
            }
        )
        initial_platformtype = precondition_fixture(
            lambda: set(
                PlatformType.objects.values_list("platformtype_name", flat=True)
            )
        )

        def it_creates_new_platformtype(self, initial_platformtype, json):
            expected = initial_platformtype | {json["platformtype_name"]}
            actual = set(
                (
                    str(
                        PlatformType.objects.values_list(
                            "platformtype_name", flat=True
                        )[0]
                    ),
                )
            )
            assert expected == actual

        def a_test_it_sets_expected_attrs(self, data, json):
            platformtype = PlatformType.objects.get(
                platformtype_name=json["platformtype_name"]
            )

            expected = data
            breakpoint()
            # E         Extra items in the right set:
            # E         UUID('968e03be-9b7d-4cf5-95a6-4377a9796479')
            assert_model_attrs(platformtype, expected)

        def it_returns_platformtype(self, json):
            platformtype = PlatformType.objects.get(
                platformtype_name=json["platformtype_name"]
            )

            expected = express_platformtype(platformtype)
            actual = json
            assert expected == actual

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        platformtype = lambda_fixture(
            lambda: PlatformType.objects.create(platformtype_name="Sonar")
        )

        def it_returns_platformtype(self, platformtype, json):
            expected = express_platformtype(platformtype)
            actual = json
            assert expected == actual

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        platformtype = lambda_fixture(
            lambda: PlatformType.objects.create(platformtype_name="Drone")
        )
        data = static_fixture(
            {
                "platformtype_name": "LRAUV",
            }
        )

        def it_sets_expected_attrs(self, data, platformtype):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            platformtype.refresh_from_db()

            expected = data
            assert_model_attrs(platformtype, expected)

        def it_returns_platformtype(self, platformtype, json):
            platformtype.refresh_from_db()

            expected = express_platformtype(platformtype)
            actual = json
            assert expected == actual

    class TestDestroy(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        platformtype = lambda_fixture(
            lambda: PlatformType.objects.create(platformtype_name="Glider")
        )

        initial_platformtype = precondition_fixture(
            lambda platformtype: set(  # ensure our to-be-deleted PlatformType exists in our set
                PlatformType.objects.values_list("platformtype_name", flat=True)
            )
        )

        def it_deletes_platformtype(self, initial_platformtype, platformtype):
            expected = initial_platformtype - {platformtype.platformtype_name}
            actual = set(
                PlatformType.objects.values_list("platformtype_name", flat=True)
            )
            assert expected == actual
