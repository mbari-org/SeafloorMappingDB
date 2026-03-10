/**
 * map_expedition_filter.js
 *
 * Expeditions page map: nav-track styling, bidirectional hover (map ↔ table),
 * mission name labels, and fixed scrollable table layout — matching the
 * Missions page behaviour.  Filter sidebar and Draw Square are NOT included.
 */

// ---------------------------------------------------------------------------
// Map and base tile layer
// ---------------------------------------------------------------------------
const map = L.map("map_expedition_filter", { minZoom: 2, maxZoom: 18 });
map.zoomControl.setPosition("bottomright");

const gmrt = L.tileLayer.wms(
  "https://www.gmrt.org/services/mapserver/wms_merc?",
  { layers: "GMRT" }
);
gmrt.addTo(map);

// ---------------------------------------------------------------------------
// Load mission GeoJSON passed by the Django view
// ---------------------------------------------------------------------------
const missions = JSON.parse(
  document.getElementById("missions-data").textContent
);

const hasMissions =
  missions && missions.features && missions.features.length > 0;

map.setView([0, 0], 2, { animate: false });

// ---------------------------------------------------------------------------
// Hover state (bidirectional map ↔ table, issue #293)
// ---------------------------------------------------------------------------
var currentHighlightedSlug = null;
var highlightedLabelEls = [];
var highlightedPathEls  = [];
var highlightedRowEls   = [];
var clearHighlightsTimeout = null;
var CLEAR_DEBOUNCE_MS = 80;

function clearAllMissionHighlights() {
  if (!currentHighlightedSlug) return;
  highlightedLabelEls.forEach(function (el) { el.classList.remove("smdb-hover"); });
  highlightedPathEls.forEach(function (p)  { p.classList.remove("smdb-hover"); });
  highlightedRowEls.forEach(function (tr)  { tr.classList.remove("smdb-hover"); });
  highlightedLabelEls = [];
  highlightedPathEls  = [];
  highlightedRowEls   = [];
  currentHighlightedSlug = null;
}

function highlightMission(slug) {
  if (!slug) return;
  if (clearHighlightsTimeout) {
    clearTimeout(clearHighlightsTimeout);
    clearHighlightsTimeout = null;
  }
  if (slug === currentHighlightedSlug) return;

  clearAllMissionHighlights();
  currentHighlightedSlug = slug;

  var escapedSlug = slug.replace(/\\/g, "\\\\").replace(/"/g, '\\"');

  highlightedLabelEls = Array.prototype.slice.call(
    document.querySelectorAll('.label-mission-name[data-mission-slug="' + escapedSlug + '"]')
  );
  highlightedLabelEls.forEach(function (l) {
    l.classList.add("smdb-hover");
    var pane = l.closest(".leaflet-marker-pane");
    if (pane) pane.appendChild(l);
  });

  var mapEl = document.getElementById("map_expedition_filter");
  highlightedPathEls = [];
  if (mapEl) {
    highlightedPathEls = Array.prototype.slice.call(
      mapEl.querySelectorAll('path[data-mission-slug="' + escapedSlug + '"]')
    );
    highlightedPathEls.forEach(function (p) {
      p.classList.add("smdb-hover");
      var parent = p.parentNode;
      if (parent) parent.appendChild(p);
    });
  }

  highlightedRowEls = Array.prototype.slice.call(
    document.querySelectorAll('tr[data-mission-slug="' + escapedSlug + '"]')
  );
  highlightedRowEls.forEach(function (tr) { tr.classList.add("smdb-hover"); });

  var mainTableRow = document.querySelector(
    '#expedition-table-wrapper tr[data-mission-slug="' + escapedSlug + '"]'
  );
  if (mainTableRow) mainTableRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ---------------------------------------------------------------------------
// GeoJSON layer — styled nav-tracks with hover wiring
// ---------------------------------------------------------------------------
function _escapeHtml(text) {
  if (!text) return "";
  return text.toString().replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c];
  });
}

let feature = L.geoJSON(missions, {
  style: function () {
    return {
      color: "rgb(139, 64, 0)",
      weight: 3.5,
      opacity: 1,
      lineCap: "round",
      lineJoin: "round",
      fill: false,
    };
  },
  onEachFeature: function (feat, layer) {
    var slug = (feat.properties && feat.properties.slug) ? feat.properties.slug : "";
    layer.on("add", function () {
      if (this._path) {
        this._path.classList.add("smdb-track-line", "smdb-geometry-line");
        if (slug) this._path.setAttribute("data-mission-slug", slug);
        this._path.addEventListener("mouseover", function () { highlightMission(slug); });
        this._path.addEventListener("mouseout", function () {
          if (clearHighlightsTimeout) clearTimeout(clearHighlightsTimeout);
          clearHighlightsTimeout = setTimeout(function () {
            clearHighlightsTimeout = null;
            clearAllMissionHighlights();
          }, CLEAR_DEBOUNCE_MS);
        });
      }
    });
  },
})
  .bindPopup(function (layer) {
    var p = layer.feature.properties;
    var slug    = (p && p.slug) ? p.slug : "";
    var expName = (p && p.expedition && p.expedition.name) ? p.expedition.name : "";
    var routeFile = (p && p.route_file) ? p.route_file : "";
    return (
      "<a target='_blank' href='/missions/" + _escapeHtml(slug) + "'>" +
      _escapeHtml(slug) + "</a>: " + _escapeHtml(expName) +
      "<br>Route: " + _escapeHtml(routeFile)
    );
  })
  .addTo(map);

// ---------------------------------------------------------------------------
// Fit map to mission bounds
// ---------------------------------------------------------------------------
var FALLBACK_CENTER = [39.8423, -26.8945];
var FALLBACK_ZOOM   = 3;
map.whenReady(function () {
  map.invalidateSize();
  setTimeout(function () {
    try {
      if (!hasMissions) { map.setView(FALLBACK_CENTER, FALLBACK_ZOOM, { animate: false }); return; }
      var featureLayers = feature.getLayers();
      if (!featureLayers || featureLayers.length === 0) { map.setView(FALLBACK_CENTER, FALLBACK_ZOOM, { animate: false }); return; }
      var bounds;
      try { bounds = feature.getBounds(); }
      catch (e) { map.setView(FALLBACK_CENTER, FALLBACK_ZOOM, { animate: false }); return; }
      if (!bounds || !bounds.isValid || !bounds.isValid()) { map.setView(FALLBACK_CENTER, FALLBACK_ZOOM, { animate: false }); return; }
      var sw = bounds.getSouthWest(), ne = bounds.getNorthEast();
      var latSpan = ne.lat - sw.lat, lngSpan = ne.lng - sw.lng;
      if (isNaN(latSpan) || isNaN(lngSpan) || lngSpan >= 360 || latSpan >= 180) {
        map.setView(FALLBACK_CENTER, FALLBACK_ZOOM, { animate: false }); return;
      }
      var padding = [100, 100];
      var zoomWouldBe = map.getBoundsZoom(bounds, false, padding);
      if (zoomWouldBe < 2 || !isFinite(zoomWouldBe)) { map.setView(FALLBACK_CENTER, FALLBACK_ZOOM, { animate: false }); return; }
      map.fitBounds(bounds, { padding: padding, animate: false });
      if (map.getZoom() < 4) map.setZoom(4, { animate: false });
    } catch (err) {
      map.setView(FALLBACK_CENTER, FALLBACK_ZOOM, { animate: false });
    }
  }, 100);
});

// ---------------------------------------------------------------------------
// Mission name labels at northernmost point of each nav-track
// ---------------------------------------------------------------------------
if (hasMissions && missions.features) {
  var labelPixelOffsetEast  = 8;
  var labelPixelOffsetNorth = 8;
  var labelEntries = [];

  function flattenCoords(geometry) {
    var c = geometry.coordinates;
    if (!c || !c.length) return [];
    if (typeof c[0][0] === "number") return c;
    var out = [];
    for (var k = 0; k < c.length; k++)
      for (var m = 0; m < c[k].length; m++) out.push(c[k][m]);
    return out;
  }

  function updateLabelPositions() {
    for (var e = 0; e < labelEntries.length; e++) {
      var entry = labelEntries[e];
      var pt = map.latLngToContainerPoint(entry.anchor);
      var newPt = L.point(pt.x + labelPixelOffsetEast, pt.y - labelPixelOffsetNorth);
      entry.marker.setLatLng(map.containerPointToLatLng(newPt));
    }
  }

  for (var i = 0; i < missions.features.length; i++) {
    var mission = missions.features[i];
    var coords  = flattenCoords(mission.geometry);
    var slug    = (mission.properties && mission.properties.slug) ? mission.properties.slug : "";
    if (coords.length === 0) continue;

    var maxLat = -Infinity, lngAtMaxLat = coords[0][0];
    for (var j = 0; j < coords.length; j++) {
      if (coords[j][1] > maxLat) { maxLat = coords[j][1]; lngAtMaxLat = coords[j][0]; }
    }

    var anchor = L.latLng(maxLat, lngAtMaxLat);
    var marker = L.marker(anchor, {
      icon: L.divIcon({
        className: "label-mission-name",
        html: "<a target='_blank' href='/missions/" + _escapeHtml(slug) + "'>" + _escapeHtml(slug) + "</a>",
      }),
    });
    labelEntries.push({ marker: marker, anchor: anchor });

    (function (missionSlug) {
      marker.on("add", function () {
        var el = this._icon;
        if (!el || !missionSlug) return;
        el.setAttribute("data-mission-slug", missionSlug);
        el.setAttribute("data-track-side", "left");
        el.addEventListener("mouseover", function () { highlightMission(missionSlug); });
        el.addEventListener("mouseout", function () {
          if (clearHighlightsTimeout) clearTimeout(clearHighlightsTimeout);
          clearHighlightsTimeout = setTimeout(function () {
            clearHighlightsTimeout = null;
            clearAllMissionHighlights();
          }, CLEAR_DEBOUNCE_MS);
        });
      });
    })(slug);

    marker.addTo(map);
  }
  updateLabelPositions();
  map.on("zoomend moveend", updateLabelPositions);
}

// ---------------------------------------------------------------------------
// Fixed scrollable table layout (table sits below map, above footer)
// ---------------------------------------------------------------------------
function initTableLayout() {
  var mapEl        = document.getElementById("map_expedition_filter");
  var tableWrapper = document.getElementById("expedition-table-wrapper");
  if (!tableWrapper || !mapEl) return;

  var footerEl = document.getElementById("footer");
  var footerH  = footerEl ? footerEl.offsetHeight : 0;

  var mapBottom = Math.round(mapEl.getBoundingClientRect().bottom);
  tableWrapper.style.position        = "fixed";
  tableWrapper.style.top             = mapBottom + "px";
  tableWrapper.style.left            = "0";
  tableWrapper.style.right           = "0";
  tableWrapper.style.bottom          = footerH + "px";
  tableWrapper.style.overflowY       = "auto";
  tableWrapper.style.overflowX       = "auto";
  tableWrapper.style.backgroundColor = "#fff";
  tableWrapper.style.zIndex          = "1";
  tableWrapper.style.marginTop       = "";
  tableWrapper.style.height          = "";
}

setTimeout(initTableLayout, 150);
window.addEventListener("resize", function () {
  if (map) map.invalidateSize();
  setTimeout(initTableLayout, 50);
});

var mapElForObserver = document.getElementById("map_expedition_filter");
if (mapElForObserver && typeof ResizeObserver !== "undefined") {
  var layoutTimeout = null;
  new ResizeObserver(function () {
    if (layoutTimeout) clearTimeout(layoutTimeout);
    layoutTimeout = setTimeout(function () { layoutTimeout = null; initTableLayout(); }, 50);
  }).observe(mapElForObserver);
}

// ---------------------------------------------------------------------------
// Table row hover → highlight map track and label
// ---------------------------------------------------------------------------
function attachTableRowHover() {
  document.querySelectorAll("tr[data-mission-slug]").forEach(function (tr) {
    var slug = tr.getAttribute("data-mission-slug");
    if (!slug) return;
    tr.addEventListener("mouseover", function () { highlightMission(slug); });
    tr.addEventListener("mouseout", function () {
      if (clearHighlightsTimeout) clearTimeout(clearHighlightsTimeout);
      clearHighlightsTimeout = setTimeout(function () {
        clearHighlightsTimeout = null;
        clearAllMissionHighlights();
      }, CLEAR_DEBOUNCE_MS);
    });
  });
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", attachTableRowHover);
} else {
  attachTableRowHover();
}
