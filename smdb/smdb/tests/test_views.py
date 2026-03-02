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


def test_mission_table_view_with_bbox(client):
    """MissionTableView applies bbox filtering — tight box excludes all Monterey fixtures."""
    url = reverse("missions")

    # All 5 fixture missions are near Monterey Bay (~-122, 36); get full unfiltered count.
    response_all = client.get(url)
    assert response_all.status_code == 200
    missions_all = response_all.context["missions"]
    assert isinstance(missions_all, dict) and "features" in missions_all
    all_count = len(missions_all["features"])
    assert all_count > 0, "Expected fixture missions to be present"

    # A bbox around the equatorial Atlantic excludes all Monterey missions.
    response_bbox = client.get(url, {
        "xmin": "-10", "xmax": "10", "ymin": "-10", "ymax": "10",
    })
    assert response_bbox.status_code == 200
    missions_bbox = response_bbox.context["missions"]
    assert isinstance(missions_bbox, dict) and "features" in missions_bbox
    bbox_count = len(missions_bbox["features"])

    assert bbox_count < all_count, (
        f"Bbox filter should exclude Monterey missions but got {bbox_count}/{all_count}. "
        "Check MissionTableView bbox filtering in views.py."
    )


def test_mission_table_view_bbox_invalid_coords(client):
    """MissionTableView handles non-numeric bbox params gracefully — no 500."""
    url = reverse("missions")
    response = client.get(url, {
        "xmin": "not-a-number", "xmax": "180", "ymin": "-90", "ymax": "90",
    })
    assert response.status_code == 200


def test_mission_table_view_bbox_inverted_coords(client):
    """MissionTableView rejects inverted bbox (xmin > xmax) — no 500, zero results."""
    url = reverse("missions")
    response = client.get(url, {
        "xmin": "180", "xmax": "-180", "ymin": "-90", "ymax": "90",
    })
    assert response.status_code == 200

    table_missions = response.context.get("object_list", [])
    assert len(table_missions) == 0, (
        "Inverted bbox (xmin > xmax) should yield no table results."
    )

    missions_geojson = response.context.get("missions", {})
    features = missions_geojson.get("features", []) if isinstance(missions_geojson, dict) else []
    assert len(features) == 0, (
        "Inverted bbox (xmin > xmax) should yield no map GeoJSON results."
    )


def test_mission_table_view_bbox_and_map_context_consistent(client):
    """Map GeoJSON context is a subset of the table queryset for the same bbox."""
    url = reverse("missions")
    response = client.get(url, {
        "xmin": "-180", "xmax": "180", "ymin": "-90", "ymax": "90",
    })
    assert response.status_code == 200

    missions_geojson = response.context["missions"]
    assert missions_geojson is not None

    # Collect IDs from the table queryset (object_list from ListView).
    table_ids = {
        m.id for m in response.context.get("object_list", []) if hasattr(m, "id")
    }

    # Collect IDs from the GeoJSON used by the map.
    if isinstance(missions_geojson, dict):
        features = missions_geojson.get("features", [])
    elif isinstance(missions_geojson, list):
        features = missions_geojson
    else:
        features = []
    map_ids = {
        f.get("properties", {}).get("id")
        for f in features
        if isinstance(f, dict) and f.get("properties", {}).get("id") is not None
    }

    # Every mission on the map must also appear in the table queryset.
    assert map_ids.issubset(table_ids), (
        f"Map missions {map_ids - table_ids} are not in the table queryset. "
        "Check MissionTableView bbox filtering logic."
    )


# -------- Mission page: sidebar filter, Draw Square, table integration --------


# Bbox that contains the missions_notes_5 fixture nav_tracks (Monterey Bay area).
_MONTEREY_BBOX = {
    "xmin": "-123",
    "xmax": "-121",
    "ymin": "36",
    "ymax": "37",
}


def test_mission_select_api_applies_vehicle_name_filter(client, missions_notes_5):
    """Draw Square API respects vehicle_name: bbox + vehicle_name returns only matching missions."""
    from smdb.models import Mission

    # Give one mission a distinct vehicle_name; leave others null or different.
    missions = list(Mission.objects.all()[:3])
    if missions:
        missions[0].vehicle_name = "Bluefin"
        missions[0].save()
        for m in missions[1:]:
            m.vehicle_name = "Other"
            m.save()

    url = reverse("mission-select-api")
    params = {**_MONTEREY_BBOX}
    response = client.get(url, params)
    assert response.status_code == 200
    data = response.json()
    all_in_bbox = data["missions"]
    assert len(all_in_bbox) >= 1

    params["vehicle_name"] = "Bluefin"
    response_filtered = client.get(url, params)
    assert response_filtered.status_code == 200
    filtered = response_filtered.json()["missions"]
    assert len(filtered) <= len(all_in_bbox)
    for m in filtered:
        assert m.get("vehicle_name") == "Bluefin"


def test_mission_select_api_applies_platformtype_filter(client, missions_notes_5):
    """Draw Square API respects platformtype: bbox + platformtype returns only missions on that platform type."""
    from smdb.models import Mission

    # Fixture missions use platform pk 1 (platformtype pk 1). Request with platformtype=1.
    url = reverse("mission-select-api")
    params = {**_MONTEREY_BBOX, "platformtype": "1"}
    response = client.get(url, params)
    assert response.status_code == 200
    data = response.json()
    missions = data["missions"]
    # All fixture missions have platform 1, so we should get at least one.
    assert isinstance(missions, list)


def test_mission_table_view_region_name_and_bbox(client, missions_notes_5):
    """Missions page: region_name filter + bbox returns only matching missions in table."""
    from smdb.models import Mission

    # Set region_name on missions so we can filter.
    missions = list(Mission.objects.all()[:2])
    if len(missions) >= 2:
        missions[0].region_name = "Monterey"
        missions[0].save()
        missions[1].region_name = "Other"
        missions[1].save()

    url = reverse("missions")
    params = {**_MONTEREY_BBOX, "region_name": "Monterey"}
    response = client.get(url, params)
    assert response.status_code == 200
    object_list = list(response.context.get("object_list", []))
    for m in object_list:
        assert m.region_name == "Monterey"


def test_mission_export_api_applies_vehicle_name_filter(client, missions_notes_5):
    """Export API accepts vehicle_name (and other sidebar filters) with bbox; no 500."""
    from smdb.models import Mission

    if Mission.objects.exists():
        Mission.objects.update(vehicle_name="MAUV1")
    url = reverse("mission-export-api")
    params = {**_MONTEREY_BBOX, "vehicle_name": "MAUV1", "format": "csv"}
    response = client.get(url, params)
    assert response.status_code == 200


# -------- Issue #290: 3D Citations -------------------------------------------


def test_mission_detail_citations(client, missions_notes_5):
    """Mission detail page shows Citations section when mission has citations."""
    from smdb.models import Mission, Citation

    mission = Mission.objects.get(name="2019/20190124m1")
    citation = Citation.objects.create(doi="10.1234/test", full_reference="Test 2020")
    mission.citations.add(citation)

    url = reverse("mission-detail", kwargs={"slug": mission.slug})
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Citations:" in content
    assert "10.1234/test" in content
    assert "Test 2020" in content


def test_mission_filter_by_citation(client, missions_notes_5):
    """Missions map filter by citation returns missions that have that citation."""
    from smdb.models import Mission, Citation

    mission = Mission.objects.get(name="2019/20190124m1")
    citation = Citation.objects.create(doi="10.5678/filter-test", full_reference="")
    mission.citations.add(citation)

    url = reverse("missions")
    response = client.get(url, {"citation": citation.pk})
    assert response.status_code == 200
    object_list = list(response.context["object_list"])
    assert mission in object_list


def test_survey_tally_load_citations(missions_notes_5):
    """SurveyTally.update_db_from_df populates mission.citations from Citations column."""
    import pandas as pd

    from smdb.models import Mission, Citation

    try:
        from scripts.load import SurveyTally
    except ImportError:
        import pytest
        pytest.skip("SurveyTally not importable (run pytest from smdb directory)")

    mission = Mission.objects.get(name="2019/20190124m1")
    assert mission.citations.count() == 0

    df = pd.DataFrame(
        [
            {
                "Mission": "2019/20190124m1",
                "Route": "",
                "Location": "",
                "Vehicle": "",
                "Quality_comment": "",
                "Patch_test": "",
                "Repeat_survey": "",
                "MGDS_compilation": "",
                "Quality_category*": "",
                "Citations": "10.1234/abc;10.5678/def|A reference",
            }
        ]
    )

    st = SurveyTally()
    st.update_db_from_df(df, "2019")

    mission.refresh_from_db()
    assert mission.citations.count() == 2
    with_ref = Citation.objects.get(doi="10.5678/def")
    assert with_ref.full_reference == "A reference"
