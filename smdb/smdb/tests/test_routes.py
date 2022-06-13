import pytest
from django.test import TestCase
from django.urls import reverse


pytestmark = pytest.mark.django_db


class RouteTest(TestCase):
    """Test web site routing."""

    @pytest.mark.django_db
    def test_homepage(self):
        homepage_url = reverse("home")

        response = self.client.get(homepage_url)

        assert response.status_code == 200
        assert response.context["request"].path == "/"

    @pytest.mark.django_db
    def test_compilations(self):
        compilation_url = reverse("compilations")

        response = self.client.get(compilation_url)

        assert response.status_code == 200
        assert response.context["request"].path == "/compilation"

    @pytest.mark.django_db
    def test_homepage(self):
        homepage_url = reverse("home")

        response = self.client.get(homepage_url)

        assert response.status_code == 200
        assert response.context["request"].path == "/"

    @pytest.mark.django_db
    def test_homepage(self):
        homepage_url = reverse("home")

        response = self.client.get(homepage_url)

        assert response.status_code == 200
        assert response.context["request"].path == "/"
