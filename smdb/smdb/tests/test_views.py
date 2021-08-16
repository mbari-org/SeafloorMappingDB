import pytest
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse

from smdb.views import MissionOverView

pytestmark = pytest.mark.django_db

from django.utils.http import urlencode


def test_home_view(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200


def test_num_missions(client):
    url = reverse("home")
    response = client.get(url)
    missions = response.context["missions"]["features"]
    # Depends on missions_notes_5.json fixture being loaded
    assert len(missions) == 5


def test_search_missions(client):
    url = reverse("home")
    response = client.get(url, {"q": "20190308"})
    missions = response.context["missions"]["features"]
    # Depends on missions_notes_5.json fixture being loaded
    assert len(missions) == 2
