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
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from smdb.api.views import PersonViewSet
from smdb.models import MissionType
from smdb.tests.factories import PersonFactory
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


class TestMissionType(ViewSetTest, AsUser("tester")):
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

        def test_it_returns_missiontypes(self, missiontypes, results):
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

        def test_it_creates_new_missiontype(self, initial_missiontype, json):
            expected = initial_missiontype | {json["missiontype_name"]}
            actual = set(MissionType.objects.values_list("missiontype_name", flat=True))
            assert expected == actual

        def test_it_sets_expected_attrs(self, data, json):
            missiontype = MissionType.objects.get(
                missiontype_name=json["missiontype_name"]
            )

            expected = data
            assert_model_attrs(missiontype, expected)

        def test_it_returns_missiontype(self, json):
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

        def test_it_returns_missiontype(self, missiontype, json):
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

        def test_it_sets_expected_attrs(self, data, missiontype):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            missiontype.refresh_from_db()

            expected = data
            assert_model_attrs(missiontype, expected)

        def test_it_returns_missiontype(self, missiontype, json):
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

        def test_it_deletes_missiontype(self, initial_missiontype, missiontype):
            expected = initial_missiontype - {missiontype.missiontype_name}
            actual = set(MissionType.objects.values_list("missiontype_name", flat=True))
            assert expected == actual


# See Viewsets section at:
# https://dev.to/sherlockcodes/pytest-with-django-rest-framework-from-zero-to-hero-8c4
class TestPersonViewSet:
    def test_list(self):
        response = APIClient().get(reverse("api:person-list"))
        # "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # = Arrange an authenticated request to the view
        factory = APIRequestFactory()
        request = factory.get("api:person-list")
        user, _ = User.objects.get_or_create(username="test_user")
        force_authenticate(request, user=user)
        view = PersonViewSet.as_view({"get": "list"})

        # = Mock
        PersonFactory().save()

        # = Act
        response = view(request).render()

        # = Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(json.loads(response.content)) == 1

    """def test_create(self):
        # = Arrange the data to perform a create post
        valid_data_dict = serializers.serialize(
            "json",
            [
                PersonFactory(),
            ],
        )
        ##valid_data_dict.del('uuid')
        factory = APIRequestFactory()
        request = factory.post(
            reverse("api:person-list"),
            content_type="application/json",
            ##data=json.dumps(valid_data_dict),
            data=valid_data_dict,
        )
        user, _ = User.objects.get_or_create(username="test_user")
        force_authenticate(request, user=user)

        # = Act
        view = PersonViewSet.as_view({"post": "create"})
        response = view(request).render()

        # = Assert
        breakpoint()
        assert response.status_code == 201
        assert json.loads(response.content) == valid_data_dict
"""
