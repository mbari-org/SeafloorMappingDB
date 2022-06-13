import pytest
from django.test import TestCase
from django.urls import reverse


pytestmark = pytest.mark.django_db


class RouteTest(TestCase):
    """Test web site basic functionality"""

    @pytest.mark.django_db
    def test_homepage(self):
        homepage_url = reverse("home")

        response = self.client.get(homepage_url)

        assert response.status_code == 200
        assert response.context["request"].path == "/"
