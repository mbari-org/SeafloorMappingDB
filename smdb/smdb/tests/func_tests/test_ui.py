"""Selenium UI tests. Monitor browser at http://localhost:7900/?autoconnect=1&resize=scale&password=secret"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


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


@pytest.mark.django_db
@pytest.mark.selenium
def test_leaflet_measure_tool_opens(chrome, live_server_url_for_selenium, missions_notes_5):
    """Leaflet-measure control exists and can be activated."""
    chrome.get(live_server_url_for_selenium)
    
    # Wait for map to load
    WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    
    # Wait for leaflet-measure control to be present
    measure_control = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-control-measure"))
    )
    
    # Find and click the measure button (has fa-ruler icon)
    measure_button = measure_control.find_element(By.CSS_SELECTOR, "a")
    measure_button.click()
    
    # Wait a moment for the menu to open
    time.sleep(0.5)
    
    # Verify the measurement options appear
    measure_options = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-control-measure .tasks a")
    assert len(measure_options) > 0, "Measure tool options should be visible"


@pytest.mark.django_db
@pytest.mark.selenium
def test_leaflet_measure_capture_marker_appears(chrome, live_server_url_for_selenium, missions_notes_5):
    """Green capture marker (moving dot) appears when creating a measurement."""
    chrome.get(live_server_url_for_selenium)
    
    # Wait for map to load
    map_element = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    
    # Open measure control
    measure_control = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-control-measure"))
    )
    measure_button = measure_control.find_element(By.CSS_SELECTOR, "a")
    measure_button.click()
    time.sleep(0.5)
    
    # Click "Create a new measurement" (first option)
    measure_options = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-control-measure .tasks a")
    if measure_options:
        measure_options[0].click()
        time.sleep(0.5)
    
    # Verify capture marker exists (large div icon with green circle)
    # The capture marker has a width > 100px
    capture_markers = chrome.execute_script("""
        const markers = document.querySelectorAll('.leaflet-marker-icon, .leaflet-div-icon');
        return Array.from(markers).filter(m => {
            const width = parseFloat(m.style.width);
            return width > 100;
        }).length;
    """)
    
    assert capture_markers > 0, "Capture marker (green moving dot) should be visible"
    
    # Verify the marker has green styling
    has_green_marker = chrome.execute_script("""
        const markers = document.querySelectorAll('.leaflet-marker-icon circle, .leaflet-div-icon circle');
        return Array.from(markers).some(circle => {
            const stroke = circle.getAttribute('stroke') || circle.style.stroke;
            return stroke && stroke.includes('ABE67E'); // Green color
        });
    """)
    
    assert has_green_marker, "Capture marker should have green color (#ABE67E)"


@pytest.mark.django_db
@pytest.mark.selenium
def test_leaflet_measure_completes_measurement(chrome, live_server_url_for_selenium, missions_notes_5):
    """User can complete a measurement and see the result popup."""
    chrome.get(live_server_url_for_selenium)
    
    # Wait for map to load
    map_element = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    
    # Open measure control and start measurement
    measure_control = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-control-measure"))
    )
    measure_button = measure_control.find_element(By.CSS_SELECTOR, "a")
    measure_button.click()
    time.sleep(0.5)
    
    # Click "Create a new measurement"
    measure_options = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-control-measure .tasks a")
    if measure_options:
        measure_options[0].click()
        time.sleep(0.5)
    
    # Get map center and size for clicking
    map_rect = chrome.execute_script("""
        const map = document.getElementById('map');
        const rect = map.getBoundingClientRect();
        return {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2,
            width: rect.width,
            height: rect.height
        };
    """)
    
    # Click on map to add points (2 points to create a line)
    actions = ActionChains(chrome)
    actions.move_to_element_with_offset(map_element, 100, 100).click().perform()
    time.sleep(0.3)
    actions.move_to_element_with_offset(map_element, 200, 100).click().perform()
    time.sleep(0.3)
    
    # Finish the measurement (click Finish button or double-click)
    actions.move_to_element_with_offset(map_element, 200, 100).double_click().perform()
    time.sleep(1)
    
    # Verify measurement result appears (popup with measurement data)
    measurement_results = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-popup-content")
    assert len(measurement_results) > 0, "Measurement result popup should appear"


@pytest.mark.django_db
@pytest.mark.selenium
def test_leaflet_measure_color_picker(chrome, live_server_url_for_selenium, missions_notes_5):
    """Color picker icon appears in measurement popup and can be clicked."""
    chrome.get(live_server_url_for_selenium)
    
    # Wait for map to load
    map_element = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    
    # Open measure control and start measurement
    measure_control = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-control-measure"))
    )
    measure_button = measure_control.find_element(By.CSS_SELECTOR, "a")
    measure_button.click()
    time.sleep(0.5)
    
    # Click "Create a new measurement"
    measure_options = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-control-measure .tasks a")
    if measure_options:
        measure_options[0].click()
        time.sleep(0.5)
    
    # Create a simple measurement (2 clicks)
    actions = ActionChains(chrome)
    actions.move_to_element_with_offset(map_element, 100, 100).click().perform()
    time.sleep(0.3)
    actions.move_to_element_with_offset(map_element, 200, 100).double_click().perform()
    time.sleep(1)
    
    # Verify paintbrush icon exists in the popup
    paintbrush_icons = chrome.find_elements(By.CSS_SELECTOR, ".measure-color-picker-btn")
    assert len(paintbrush_icons) > 0, "Color picker paintbrush icon should be visible in measurement popup"
    
    # Click the paintbrush icon
    if paintbrush_icons:
        paintbrush_icons[0].click()
        time.sleep(0.5)
        
        # Verify color picker popup appears
        color_picker_popup = chrome.find_elements(By.CSS_SELECTOR, ".measure-color-picker-popup")
        assert len(color_picker_popup) > 0, "Color picker popup should appear after clicking paintbrush"
        
        # Verify color input exists
        color_input = chrome.find_elements(By.ID, "measureColorInput")
        assert len(color_input) > 0, "Color input field should exist in color picker"


@pytest.mark.django_db
@pytest.mark.selenium
def test_leaflet_measure_color_persists(chrome, live_server_url_for_selenium, missions_notes_5):
    """Changed measurement color persists and is not overridden by auto-styling."""
    chrome.get(live_server_url_for_selenium)
    
    # Wait for map to load
    map_element = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    
    # Open measure control and create a measurement
    measure_control = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-control-measure"))
    )
    measure_button = measure_control.find_element(By.CSS_SELECTOR, "a")
    measure_button.click()
    time.sleep(0.5)
    
    measure_options = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-control-measure .tasks a")
    if measure_options:
        measure_options[0].click()
        time.sleep(0.5)
    
    # Create measurement
    actions = ActionChains(chrome)
    actions.move_to_element_with_offset(map_element, 100, 100).click().perform()
    time.sleep(0.3)
    actions.move_to_element_with_offset(map_element, 200, 100).double_click().perform()
    time.sleep(1)
    
    # Open color picker and change color to red
    paintbrush = chrome.find_elements(By.CSS_SELECTOR, ".measure-color-picker-btn")
    if paintbrush:
        paintbrush[0].click()
        time.sleep(0.5)
        
        # Click red preset button
        red_preset = chrome.find_elements(By.CSS_SELECTOR, '.color-preset[data-color="#ff0000"]')
        if red_preset:
            red_preset[0].click()
            time.sleep(0.3)
            
            # Click Apply button
            apply_button = chrome.find_element(By.ID, "applyColorBtn")
            apply_button.click()
            time.sleep(1)
            
            # Verify the measurement path has red color and user-color marker
            has_user_color = chrome.execute_script("""
                const paths = document.querySelectorAll('path.leaflet-interactive');
                for (let path of paths) {
                    const container = path.closest('.smdb-measure-user-color');
                    if (container) {
                        const stroke = path.style.stroke || path.getAttribute('stroke');
                        if (stroke && (stroke.includes('255, 0, 0') || stroke.includes('#ff0000') || stroke.includes('rgb(255, 0, 0)'))) {
                            return true;
                        }
                    }
                }
                return false;
            """)
            
            assert has_user_color, "User-chosen red color should persist on the measurement"


@pytest.mark.django_db
@pytest.mark.selenium
def test_track_lines_have_rust_color(chrome, live_server_url_for_selenium, missions_notes_5):
    """Track lines display with rust/brown color on GMRT basemap."""
    chrome.get(live_server_url_for_selenium)
    
    # Wait for map and tracks to load
    WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    time.sleep(2)  # Give time for tracks to render
    
    # Verify track lines exist
    track_lines = chrome.execute_script("""
        return document.querySelectorAll('path.smdb-track-line').length;
    """)
    
    assert track_lines > 0, "Track lines should be visible on the map"
    
    # Verify track lines have rust color (rgb(139, 64, 0))
    has_rust_color = chrome.execute_script("""
        const tracks = document.querySelectorAll('path.smdb-track-line');
        for (let track of tracks) {
            const stroke = track.style.stroke || track.getAttribute('stroke');
            if (stroke && (stroke.includes('139, 64, 0') || stroke.includes('rgb(139, 64, 0)'))) {
                return true;
            }
        }
        return false;
    """)
    
    assert has_rust_color, "Track lines should have rust color (rgb(139, 64, 0))"
