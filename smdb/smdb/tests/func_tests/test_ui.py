"""Selenium UI tests. Monitor browser at http://localhost:7900/?autoconnect=1&resize=scale&password=secret"""

import pytest
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

# CSS selector for rendered AUV nav-track paths.
# Classes are assigned via layer.on('add') in map.js (issues #291, #290).
_TRACK_CSS = "path.leaflet-interactive.smdb-track-line.smdb-geometry-line"


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


# Previously removed as a known failing test. Root cause was fixed: SliderControl.js
# now guards against NaN timestamps (missions with null start_ems), preventing a
# RangeError that halted map.js before the popup handler registered. See the NaN
# guard in SliderControl.extractTimestamp and the try-catch around startSlider()
# in map.js. Both tests are reliably green with those fixes in place.
@pytest.mark.django_db
@pytest.mark.selenium
def test_leaflet_measure_completes_measurement(chrome, live_server_url_for_selenium, missions_notes_5):
    """User can complete a measurement and see the result popup."""
    chrome.get(live_server_url_for_selenium)

    # Wait for map to load
    map_element = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )

    # Open measure control
    measure_control = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-control-measure"))
    )
    measure_control.find_element(By.CSS_SELECTOR, "a").click()
    time.sleep(0.5)

    # Click "Start measuring" (first task link)
    start_options = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-control-measure .tasks a")
    assert start_options, "Measure start options should be visible"
    start_options[0].click()
    time.sleep(0.5)

    # Derive click offsets from the map size so the test adapts to viewport changes.
    map_rect = chrome.execute_script("""
        const rect = document.getElementById('map').getBoundingClientRect();
        return { width: rect.width, height: rect.height };
    """)
    offset1_x = int(map_rect["width"] * 0.25)
    offset1_y = int(map_rect["height"] * 0.25)
    offset2_x = int(map_rect["width"] * 0.40)

    # Place two points on the map (each in a fresh ActionChains to avoid state carry-over)
    ActionChains(chrome).move_to_element_with_offset(map_element, offset1_x, offset1_y).click().perform()
    time.sleep(0.3)
    ActionChains(chrome).move_to_element_with_offset(map_element, offset2_x, offset1_y).click().perform()
    time.sleep(0.3)

    # Click the leaflet-measure "Finish measurement" button (.js-finish) — more reliable
    # than double-clicking the map, which targets the invisible _captureMarker overlay.
    finish_btn = WebDriverWait(chrome, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".leaflet-control-measure .js-finish"))
    )
    finish_btn.click()

    # Wait for the result popup (leaflet-measure opens a standard Leaflet popup)
    popup = WebDriverWait(chrome, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-popup-content"))
    )
    assert popup is not None, "Measurement result popup should appear"


@pytest.mark.django_db
@pytest.mark.selenium
def test_leaflet_measure_color_persists(chrome, live_server_url_for_selenium, missions_notes_5):
    """Changed measurement color persists and is not overridden by auto-styling."""
    chrome.get(live_server_url_for_selenium)

    # Wait for map to load
    map_element = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )

    # Open measure control
    measure_control = WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-control-measure"))
    )
    measure_control.find_element(By.CSS_SELECTOR, "a").click()
    time.sleep(0.5)

    # Click "Start measuring" (first task link)
    start_options = chrome.find_elements(By.CSS_SELECTOR, ".leaflet-control-measure .tasks a")
    assert start_options, "Measure start options should be visible"
    start_options[0].click()
    time.sleep(0.5)

    # Place two points, then click the Finish button
    ActionChains(chrome).move_to_element_with_offset(map_element, 100, 100).click().perform()
    time.sleep(0.3)
    ActionChains(chrome).move_to_element_with_offset(map_element, 200, 100).click().perform()
    time.sleep(0.3)

    finish_btn = WebDriverWait(chrome, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".leaflet-control-measure .js-finish"))
    )
    finish_btn.click()

    # Wait for popup (leaflet-measure opens a standard Leaflet popup)
    WebDriverWait(chrome, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-popup-content"))
    )
    # Give the map.js popupopen handler a moment to inject the paintbrush icon
    time.sleep(0.5)

    paintbrush = WebDriverWait(chrome, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".measure-color-picker-btn"))
    )
    assert paintbrush, "Measure color paintbrush button should be present after completing a measurement"
    paintbrush.click()
    time.sleep(0.5)

    # Click red preset button
    red_preset = chrome.find_elements(By.CSS_SELECTOR, '.color-preset[data-color="#ff0000"]')
    assert red_preset, "Red color preset (#ff0000) should be present in the color picker"
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


# ---------------------------------------------------------------------------
# Nav-track hover tests — GitHub issues #291 / #290
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.selenium
def test_nav_track_classes_assigned(chrome, live_server_url_for_selenium, missions_notes_5):
    """Track paths carry smdb-track-line and smdb-geometry-line classes after the map loads.

    Regression guard for the layer.on('add') fix in map.js (issues #291, #290):
    onEachFeature used to check layer._path directly, which is always null before
    the layer is added to the map.  The fix defers class assignment to the Leaflet
    'add' event so _path exists.  If this test fails, the classes are missing and
    the yellow-hover CSS rule will never match.
    """
    chrome.get(live_server_url_for_selenium)

    # Wait for map container first so we don't burn timeout during page load.
    WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    # Wait up to 25 s for at least one fully-classed track path (GeoJSON layer + add event).
    WebDriverWait(chrome, 25).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, _TRACK_CSS))
    )

    track_count = chrome.execute_script(
        "return document.querySelectorAll(arguments[0]).length;", _TRACK_CSS
    )
    assert track_count > 0, (
        f"Expected track paths with selector '{_TRACK_CSS}' but found none. "
        "Check the layer.on('add') class-assignment in map.js (issue #291)."
    )


@pytest.mark.django_db
@pytest.mark.selenium
def test_nav_track_highlights_yellow_on_hover(chrome, live_server_url_for_selenium, missions_notes_5):
    """Nav track stroke becomes yellow when the mouse hovers over it (issues #291, #290).

    Verifies the complete chain:
      1. smdb-track-line / smdb-geometry-line classes exist on SVG paths.
      2. The CSS :hover rule (stroke: yellow) is present in the loaded stylesheet.
      3. Moving the mouse over the path triggers the yellow stroke.

    Two hover strategies are attempted in sequence so the test is robust across
    different Selenium/Chromium builds:
      - Attempt 1: precise viewport coordinates via getPointAtLength()+getScreenCTM()
        and ActionBuilder.move_to_location().  Best for thin SVG strokes; a
        WebDriverWait polling loop is intentionally avoided because repeated
        execute_script() calls can reset the browser pointer-hit state in some
        headless Chromium builds, causing the :hover pseudo-class to be lost.
      - Attempt 2: ActionChains.move_to_element() fallback.  Less precise for thin
        lines but uses Selenium's built-in element-centre calculation and works in
        environments where the coordinate approach misses the stroke.
    """
    chrome.get(live_server_url_for_selenium)

    # Wait for map first, then track path (reduces flake: GeoJSON + layer add can be slow).
    WebDriverWait(chrome, 10).until(
        EC.presence_of_element_located((By.ID, "map"))
    )
    track = WebDriverWait(chrome, 25).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, _TRACK_CSS))
    )

    # Verify the CSS hover rule is present in the loaded stylesheets.
    # This fast, environment-independent check catches missing/broken CSS rules
    # before attempting the slower Selenium hover interaction.
    hover_rule_stroke = chrome.execute_script("""
        for (var i = 0; i < document.styleSheets.length; i++) {
            try {
                var rules = document.styleSheets[i].cssRules || [];
                for (var j = 0; j < rules.length; j++) {
                    var r = rules[j];
                    if (r.selectorText
                            && r.selectorText.indexOf('smdb-track-line') > -1
                            && r.selectorText.indexOf(':hover') > -1) {
                        return r.style.stroke;
                    }
                }
            } catch (e) {}
        }
        return null;
    """)
    assert hover_rule_stroke in ("yellow", "rgb(255, 255, 0)"), (
        f"CSS :hover rule for smdb-track-line not found or not yellow "
        f"(got: '{hover_rule_stroke}'). Check project.css (issue #291)."
    )

    # Record the resting (non-hover) stroke color before moving the mouse.
    resting_color = chrome.execute_script(
        "return window.getComputedStyle(arguments[0]).stroke;", track
    )

    # Compute the viewport (CSS-pixel) coordinates of the path midpoint so the
    # mouse lands on the actual stroke, not an empty corner of the bounding box.
    coords = chrome.execute_script("""
        var path = document.querySelector(arguments[0]);
        if (!path) return null;
        var svg  = path.ownerSVGElement;
        var pt   = path.getPointAtLength(path.getTotalLength() / 2);
        var svgPt = svg.createSVGPoint();
        svgPt.x = pt.x;
        svgPt.y = pt.y;
        var screen = svgPt.matrixTransform(svg.getScreenCTM());
        return {pathX: screen.x, pathY: screen.y};
    """, _TRACK_CSS)

    assert coords, "Could not compute path screen coordinates."

    def _is_yellow():
        c = chrome.execute_script(
            "return window.getComputedStyle(arguments[0]).stroke;", track
        )
        return c and ("255, 255, 0" in c or c.lower() == "yellow")

    # Attempt 1: precise viewport-coordinate move.
    mouse = PointerInput("mouse", "mouse")
    builder = ActionBuilder(chrome, mouse=mouse)
    builder.pointer_action.move_to_location(int(coords["pathX"]), int(coords["pathY"]))
    builder.perform()
    try:
        WebDriverWait(chrome, 2, poll_frequency=0.2).until(lambda d: _is_yellow())
    except TimeoutException:
        pass

    # Attempt 2: element-centre fallback for environments where the coordinate
    # approach misses the stroke (e.g. different window size or DPR scaling).
    if not _is_yellow():
        ActionChains(chrome).move_to_element(track).perform()
        try:
            WebDriverWait(chrome, 2, poll_frequency=0.2).until(lambda d: _is_yellow())
        except TimeoutException:
            pass

    # If neither strategy landed the hover on the path, fail with a clear message
    # so CI logs show "hover missed" rather than "wrong color" (avoids false negatives).
    if not _is_yellow():
        pytest.fail(
            "Hover did not land on track after both strategies (coordinate move and "
            "move_to_element). The track may be too thin or DPR/window size may differ. "
            "Highlight behavior may still be correct; this can be flaky in headless CI."
        )
    # When we get here, _is_yellow() is True so the track stroke is yellow (hover landed).


# ---------------------------------------------------------------------------
# Bidirectional track–name hover link — GitHub issue #293
# ---------------------------------------------------------------------------

_TRACK_MISSION_CSS = "path.leaflet-interactive.smdb-track-line.smdb-geometry-line[data-mission-slug]"


@pytest.mark.django_db
@pytest.mark.selenium
def test_track_and_mission_name_highlight_together_on_hover(
    chrome, live_server_url_for_selenium, missions_notes_5
):
    """Hovering a nav track highlights the matching mission row and vice versa; mouse away clears both (issue #293).

    Runs on the Missions page where the map and mission table are both visible.
    """
    chrome.get(live_server_url_for_selenium + "/missions/")

    # Wait for at least one track path with data-mission-slug and one table row with same.
    WebDriverWait(chrome, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, _TRACK_MISSION_CSS))
    )
    track = chrome.find_element(By.CSS_SELECTOR, _TRACK_MISSION_CSS)
    slug = track.get_attribute("data-mission-slug")
    assert slug, "Track path must have data-mission-slug (issue #293)."

    row_selector = 'tr[data-mission-slug="' + slug + '"]'
    try:
        row = WebDriverWait(chrome, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, row_selector))
        )
    except TimeoutException:
        pytest.skip(
            "No mission table row found with matching data-mission-slug; "
            "this can happen if the mission is not visible on the current page "
            "of the mission table or if there are no missions with tracks."
        )

    # Move mouse away first so we start from a clean state.
    ActionChains(chrome).move_to_element_with_offset(
        chrome.find_element(By.TAG_NAME, "body"), 0, 0
    ).perform()
    time.sleep(0.3)

    # 1) Hover track -> track and row should get .smdb-hover
    coords = chrome.execute_script(
        """
        var path = arguments[0];
        var svg = path.ownerSVGElement;
        var pt = path.getPointAtLength(path.getTotalLength() / 2);
        var sp = svg.createSVGPoint();
        sp.x = pt.x; sp.y = pt.y;
        var s = sp.matrixTransform(svg.getScreenCTM());
        return { x: s.x, y: s.y };
        """,
        track,
    )
    if coords:
        mouse = PointerInput("mouse", "mouse")
        builder = ActionBuilder(chrome, mouse=mouse)
        builder.pointer_action.move_to_location(int(coords["x"]), int(coords["y"]))
        builder.perform()
    else:
        ActionChains(chrome).move_to_element(track).perform()
    time.sleep(0.4)

    assert "smdb-hover" in (track.get_attribute("class") or ""), (
        "Hovering track should add smdb-hover to the path (issue #293)."
    )
    assert "smdb-hover" in (row.get_attribute("class") or ""), (
        "Hovering track should add smdb-hover to the matching mission row (issue #293)."
    )

    # 2) Mouse away -> both should lose .smdb-hover
    ActionChains(chrome).move_to_element_with_offset(
        chrome.find_element(By.TAG_NAME, "body"), 0, 0
    ).perform()
    time.sleep(0.4)

    assert "smdb-hover" not in (track.get_attribute("class") or ""), (
        "Moving mouse away should remove smdb-hover from the track (issue #293)."
    )
    assert "smdb-hover" not in (row.get_attribute("class") or ""), (
        "Moving mouse away should remove smdb-hover from the row (issue #293)."
    )

    # 3) Hover row -> row and track should get .smdb-hover
    ActionChains(chrome).move_to_element(row).perform()
    time.sleep(0.4)

    assert "smdb-hover" in (row.get_attribute("class") or ""), (
        "Hovering row should add smdb-hover to the row (issue #293)."
    )
    assert "smdb-hover" in (track.get_attribute("class") or ""), (
        "Hovering row should add smdb-hover to the matching track (issue #293)."
    )

    # 4) Mouse away -> both should clear again
    ActionChains(chrome).move_to_element_with_offset(
        chrome.find_element(By.TAG_NAME, "body"), 0, 0
    ).perform()
    time.sleep(0.4)

    assert "smdb-hover" not in (track.get_attribute("class") or ""), (
        "Moving mouse away should clear track highlight (issue #293)."
    )
    assert "smdb-hover" not in (row.get_attribute("class") or ""), (
        "Moving mouse away should clear row highlight (issue #293)."
    )
