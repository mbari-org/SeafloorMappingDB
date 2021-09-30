import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_home_view(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200


def test_num_missions(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200
    missions = response.context["missions"]["features"]
    # Depends on missions_notes_5.json fixture being loaded
    assert len(missions) == 5


def test_search_missions(client):
    url = reverse("home")
    response = client.get(url, {"q": "20190308"})
    assert response.status_code == 200
    missions = response.context["missions"]["features"]
    # Depends on missions_notes_5.json fixture being loaded
    # As of 30 Sep 2021 notes_text are also searched, returning 3
    assert len(missions) == 3
