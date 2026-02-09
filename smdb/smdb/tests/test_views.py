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


def test_home_view_with_tmin_tmax_dates(client):
    """Test that tmin/tmax date filtering works without TypeError."""
    url = reverse("home")
    # Test with valid date strings (YYYY-MM-DD format)
    response = client.get(url, {"tmin": "2019-01-01", "tmax": "2019-12-31"})
    assert response.status_code == 200
    missions = response.context["missions"]["features"]
    # Should return missions within the date range (or empty if none match)
    assert isinstance(missions, list)


def test_home_view_with_tmin_tmax_empty_strings(client):
    """Test that empty tmin/tmax strings don't cause errors."""
    url = reverse("home")
    response = client.get(url, {"tmin": "", "tmax": ""})
    assert response.status_code == 200
    missions = response.context["missions"]["features"]
    assert isinstance(missions, list)


def test_home_view_with_tmin_only(client):
    """Test that missing tmax doesn't cause errors."""
    url = reverse("home")
    response = client.get(url, {"tmin": "2019-01-01"})
    assert response.status_code == 200
    missions = response.context["missions"]["features"]
    assert isinstance(missions, list)


def test_home_view_with_invalid_date_format(client):
    """Test that invalid date formats are handled gracefully."""
    url = reverse("home")
    # Invalid date format should not cause TypeError
    response = client.get(url, {"tmin": "invalid-date", "tmax": "also-invalid"})
    assert response.status_code == 200
    missions = response.context["missions"]["features"]
    assert isinstance(missions, list)


def test_mission_select_api_requires_spatial_bounds(client):
    """Test MissionSelectAPIView returns 400 when spatial bounds are missing."""
    url = reverse("mission-select-api")
    response = client.get(url, {"tmin": "2019-01-01", "tmax": "2019-12-31"})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "bounds" in data["error"].lower()


def test_mission_select_api_with_tmin_tmax(client):
    """Test MissionSelectAPIView with tmin/tmax date filtering."""
    url = reverse("mission-select-api")
    response = client.get(url, {
        "xmin": "-180", "xmax": "180", "ymin": "-90", "ymax": "90",
        "tmin": "2019-01-01", "tmax": "2019-12-31",
    })
    assert response.status_code == 200
    data = response.json()
    assert "missions" in data
    assert isinstance(data["missions"], list)


def test_mission_select_api_with_empty_dates(client):
    """Test MissionSelectAPIView with empty tmin/tmax strings (bounds required)."""
    url = reverse("mission-select-api")
    response = client.get(url, {
        "xmin": "-180", "xmax": "180", "ymin": "-90", "ymax": "90",
        "tmin": "", "tmax": "",
    })
    assert response.status_code == 200
    data = response.json()
    assert "missions" in data


def test_mission_select_api_with_invalid_dates(client):
    """Test MissionSelectAPIView handles invalid date formats."""
    url = reverse("mission-select-api")
    response = client.get(url, {
        "xmin": "-180", "xmax": "180", "ymin": "-90", "ymax": "90",
        "tmin": "not-a-date", "tmax": "also-not-a-date",
    })
    assert response.status_code == 200
    data = response.json()
    assert "missions" in data


def test_mission_export_api_with_tmin_tmax(client):
    """Test MissionExportAPIView with tmin/tmax date filtering."""
    url = reverse("mission-export-api")
    # Export API requires spatial bounds
    response = client.get(url, {
        "xmin": "-180", "xmax": "180", "ymin": "-90", "ymax": "90",
        "tmin": "2019-01-01", "tmax": "2019-12-31"
    })
    # Should not return 500 error (may return 400 if no missions match, but not 500)
    assert response.status_code != 500


def test_mission_export_api_with_empty_dates(client):
    """Test MissionExportAPIView with empty tmin/tmax strings."""
    url = reverse("mission-export-api")
    response = client.get(url, {
        "xmin": "-180", "xmax": "180", "ymin": "-90", "ymax": "90",
        "tmin": "", "tmax": ""
    })
    # Should not return 500 error
    assert response.status_code != 500
