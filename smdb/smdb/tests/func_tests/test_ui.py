"""Selenium UI tests. Monitor browser at http://localhost:7900/?autoconnect=1&resize=scale&password=secret"""

import pytest
from selenium.webdriver.common.by import By


@pytest.mark.django_db
@pytest.mark.selenium
def test_visit_site_with_chrome(chrome, live_server_url_for_selenium, missions_notes_5):
    """Home page loads with title and shows 5 missions from fixture."""
    chrome.get(live_server_url_for_selenium)
    assert "SeafloorMappingDB" in chrome.title
    number = chrome.find_element(By.ID, "num-missions").text
    assert number == "5"


@pytest.mark.django_db
@pytest.mark.selenium
def test_spatial_bounds_link(chrome, live_server_url_for_selenium, missions_notes_5):
    """Map bounds element exists and use_bounds/search can be clicked."""
    chrome.get(live_server_url_for_selenium)
    # Example map-bounds text: '36.6395, -122.0825; 36.8486, -121.7299'
    initial_bounds = chrome.find_element(By.ID, "map-bounds").text
    # Transform to query params and trigger search
    req_str = f"xmin={initial_bounds.split(';')[0].split(',')[1].strip()}&"
    req_str += f"xmax={initial_bounds.split(';')[1].split(',')[1].strip()}&"
    req_str += f"ymin={initial_bounds.split(';')[0].split(',')[0].strip()}&"
    req_str += f"ymax={initial_bounds.split(';')[1].split(',')[0].strip()}"
    chrome.find_element(By.ID, "use_bounds").click()
    chrome.find_element(By.ID, "searchbtn").click()
    # TODO: Assert URL contains req_str when front-end updates URL as expected
    print(f"{chrome.current_url = }")
