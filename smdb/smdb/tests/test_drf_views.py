import json
import pytest
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from smdb.api.views import PersonViewSet
from smdb.models import MissionType, Person, PlatformType
from smdb.users.models import User
from smdb.tests.factories import PersonFactory

pytestmark = pytest.mark.django_db


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
