import pytest
from django.urls import reverse

from smdb.models import Mission, Missiontype

pytestmark = pytest.mark.django_db


class TestAdmin:
    def test_missiontype_changelist(self, admin_client):
        url = reverse("admin:smdb_missiontype_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_missiontype_search(self, admin_client):
        url = reverse("admin:smdb_missiontype_changelist")
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    def test_missiontype_add(self, admin_client):
        url = reverse("admin:smdb_missiontype_add")
        response = admin_client.get(url)
        assert response.status_code == 200

        response = admin_client.post(
            url,
            data={
                "name": "test",
            },
        )
        assert response.status_code == 302
        assert Missiontype.objects.filter(name="test").exists()

    def test_mission_search(self, admin_client):
        url = reverse("admin:smdb_mission_changelist")
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    def test_expedition_search(self, admin_client):
        url = reverse("admin:smdb_expedition_changelist")
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    """
    def test_add_mission(self, admin_client):
        # Adding a Mission requires several more fields than just name
        url = reverse("admin:smdb_mission_add")
        response = admin_client.get(url)
        assert response.status_code == 200

        response = admin_client.post(
            url,
            data={
                "name": "test",
            },
        )
        # A successful post (add) has 302 code
        assert response.status_code == 302
        assert Mission.objects.filter(name="test").exists()

    def test_view_mission(self, admin_client):
        mission = Mission.objects.get(username="admin")
        url = reverse("admin:smdb_mission_change", kwargs={"object_id": mission.pk})
        response = admin_client.get(url)
        assert response.status_code == 200
    """
