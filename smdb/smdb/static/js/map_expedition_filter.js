/**
 * map_expedition_filter.js
 *
 * Expeditions page map: nav-track styling, bidirectional hover (map ↔ table),
 * mission name labels, filter sidebar, draw-rectangle bbox search, and fixed
 * scrollable table layout — matching the Missions page behaviour.
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
// Pre-built slug → TR[] index so highlightMission() can do an O(1) row lookup
// instead of scanning all table links on every hover event.
var slugRowIndex = null;

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

  // Use the pre-built slug→row index (built once in attachTableRowHover) for an
  // O(1) lookup — avoids scanning all table links on every hover event.
  highlightedRowEls = [];
  if (slugRowIndex && slugRowIndex[slug]) {
    highlightedRowEls = slugRowIndex[slug].slice();
    highlightedRowEls.forEach(function (tr) { tr.classList.add("smdb-hover"); });
  }
  if (highlightedRowEls.length > 0) {
    highlightedRowEls[0].scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
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
      "<a target='_blank' rel='noopener noreferrer' href='/missions/" + _escapeHtml(slug) + "/'>" +
      _escapeHtml(slug) + "</a>: " + _escapeHtml(expName) +
      "<br>Route: " + _escapeHtml(routeFile)
    );
  })
  .addTo(map);

// ---------------------------------------------------------------------------
// Fit map to mission bounds
// ---------------------------------------------------------------------------
var FALLBACK_CENTER = [36.6, -122.0];
var FALLBACK_ZOOM   = 6;
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
      map.setZoom(map.getZoom() - 1, { animate: false });
      if (map.getZoom() < 3) map.setZoom(3, { animate: false });
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
        html: "<a target='_blank' rel='noopener noreferrer' href='/missions/" + _escapeHtml(slug) + "/'>" + _escapeHtml(slug) + "</a>",
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
// Filter sidebar control
// ---------------------------------------------------------------------------
const FilterControl = L.Control.extend({
  onAdd: function (map) {
    const wrapper = L.DomUtil.create("div", "filter-wrapper");
    wrapper.style.cssText =
      "position:relative;width:40px;height:50px;transition:width 0.3s ease;" +
      "z-index:1000;background:transparent;border:none;box-shadow:none;margin:0;padding:0;";

    const sidebar = L.DomUtil.create("div", "filter-sidebar", wrapper);
    sidebar.id = "filter-sidebar";
    sidebar.style.cssText =
      "position:absolute;left:-250px;top:0;width:250px;max-height:calc(100vh - 60px);" +
      "height:auto;min-height:50px;background:#2d2d2d;box-shadow:2px 0 12px rgba(0,0,0,0.5);" +
      "border-radius:0 4px 4px 0;color:#e0e0e0;transition:left 0.3s ease,height 0.3s ease;" +
      "overflow:hidden;display:flex;flex-direction:column;z-index:999;pointer-events:auto;";

    const buttonWrapper = L.DomUtil.create("div", "filter-button-wrapper", wrapper);
    buttonWrapper.style.cssText =
      "position:absolute;top:5px;left:20px;z-index:1001;width:40px;height:40px;";

    const container = L.DomUtil.create("div", "filter-control", buttonWrapper);
    container.id = "filter-button";
    container.setAttribute("aria-label", "Filter Expeditions");
    const filterTooltip = L.DomUtil.create("span", "map-control-tooltip", buttonWrapper);
    filterTooltip.textContent = "Filter Expeditions";
    filterTooltip.setAttribute("role", "tooltip");

    container.style.cssText =
      "width:40px;height:40px;background:hsla(0,0%,100%,0.75);border-radius:4px;" +
      "cursor:pointer;display:flex;flex-direction:column;align-items:center;" +
      "justify-content:center;box-shadow:0 1px 5px rgba(0,0,0,0.4);position:relative;" +
      "z-index:1001;transition:left 0.3s ease,all 0.2s ease;" +
      "border:1px solid rgba(0,0,0,0.3);outline:none;margin:0;padding:0;";

    const icon = L.DomUtil.create("i", "fas fa-filter", container);
    icon.id = "filter-icon";
    icon.style.cssText = "font-size:18px;color:#007bff;";

    const badge = L.DomUtil.create("span", "filter-count-badge", container);
    badge.id = "filter-count-badge";
    badge.style.cssText =
      "position:absolute;top:-2px;right:-2px;background:#dc3545;color:white;" +
      "border-radius:50%;width:14px;height:14px;font-size:9px;display:none;" +
      "align-items:center;justify-content:center;";

    const header = L.DomUtil.create("div", "filter-sidebar-header", sidebar);
    header.style.cssText =
      "padding:0.5rem;padding-right:50px;border-bottom:1px solid #555;" +
      "background:#1e1e1e;display:flex;justify-content:flex-start;" +
      "align-items:center;flex-shrink:0;";

    const title = L.DomUtil.create("h6", "", header);
    title.textContent = "Filter Expeditions";
    title.style.cssText =
      "margin:0;font-size:0.85rem;font-weight:600;margin-left:0.5rem;" +
      "margin-right:0.5rem;color:#ffffff;";

    const body = L.DomUtil.create("div", "filter-sidebar-body", sidebar);
    body.id = "filter-sidebar-body";
    body.style.cssText =
      "padding:0.5rem 0.5rem 0.25rem 0.5rem;overflow-y:auto;overflow-x:hidden;" +
      "padding-bottom:0.25rem;flex:1 1 auto;min-height:0;" +
      "max-height:calc(50vh - 60px);";

    var clearListenerAdded = false;

    function recalcSidebarHeight() {
      if (!sidebar) return;
      var mapEl = document.getElementById("map_expedition_filter");
      var mapH  = mapEl ? mapEl.clientHeight : Math.round(window.innerHeight * 0.5);
      var b = document.getElementById("filter-sidebar-body");
      if (!b) return;
      var bodyFlex = b.style.flex;
      b.style.flex = "0 0 auto";
      sidebar.style.height = "auto";
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          var natural = sidebar.offsetHeight;
          sidebar.style.height = Math.min(natural, mapH) + "px";
          b.style.flex = bodyFlex || "1";
        });
      });
    }

    const copyForm = function () {
      const formContainer = document.getElementById("filter-form-container");
      if (!formContainer) return false;

      const formWrapper = formContainer.querySelector("#filter-form-expedition");
      if (!formWrapper) return false;

      const form = formWrapper.querySelector("form") || formWrapper;
      if (!form || form.children.length === 0) return false;

      body.innerHTML = "";

      const clonedForm = form.cloneNode(true);
      clonedForm.id = "filter-form-expedition";
      clonedForm.className = "filter-form";
      clonedForm.setAttribute("data-filter-type", "expedition");
      clonedForm.method = "get";
      clonedForm.action = window.location.pathname;
      clonedForm.style.display = "block";

      clonedForm.querySelectorAll("[id]").forEach(function (el) {
        el.id = el.id + "-sidebar";
      });
      clonedForm.querySelectorAll("label[for]").forEach(function (lbl) {
        lbl.setAttribute("for", lbl.getAttribute("for") + "-sidebar");
      });

      clonedForm.querySelectorAll("button").forEach(function (btn) {
        var onclick = btn.getAttribute("onclick");
        var isClearBtn =
          btn.type === "reset" ||
          (btn.id && (btn.id.includes("Cancel") || btn.id.includes("clear"))) ||
          (onclick && onclick.includes("window.location"));
        if (isClearBtn) {
          btn.removeAttribute("onclick");
          btn.onclick = null;
        }
      });

      const filterTypeInput = document.createElement("input");
      filterTypeInput.type = "hidden";
      filterTypeInput.name = "filter_type";
      filterTypeInput.value = "expedition";
      clonedForm.appendChild(filterTypeInput);

      body.appendChild(clonedForm);

      const buttonRow = document.createElement("div");
      buttonRow.className = "button-row mb-3";
      buttonRow.style.cssText =
        "display:flex;align-items:center;gap:0.5rem;margin-top:1.5rem;" +
        "margin-bottom:0.5rem;width:100%;";

      const filterBtn = document.createElement("button");
      filterBtn.type = "submit";
      filterBtn.id = "expeditionFilterSubmit";
      filterBtn.className = "btn btn-primary";
      filterBtn.textContent = "Filter";
      _styleBtn(filterBtn, "#007bff");

      const clearBtn = document.createElement("button");
      clearBtn.type = "reset";
      clearBtn.id = "expeditionFilterCancel";
      clearBtn.className = "btn btn-secondary";
      clearBtn.textContent = "Clear";
      _styleBtn(clearBtn, "#6c757d");

      buttonRow.appendChild(filterBtn);
      buttonRow.appendChild(clearBtn);
      clonedForm.appendChild(buttonRow);

      setTimeout(function () {
        [filterBtn, clearBtn].forEach(function (btn) {
          _styleBtn(btn, btn.classList.contains("btn-primary") ? "#007bff" : "#6c757d");
        });
        buttonRow.style.setProperty("display", "flex", "important");
        buttonRow.style.setProperty("align-items", "center", "important");
      }, 100);

      if (!clearListenerAdded) {
        clearListenerAdded = true;
        body.addEventListener(
          "click",
          function (e) {
            var tgt = e.target;
            var isClear =
              tgt.type === "reset" ||
              (tgt.id &&
                (tgt.id.includes("Cancel") || tgt.id.includes("clear")));
            if (isClear && tgt.closest("#filter-sidebar-body")) {
              e.preventDefault();
              e.stopPropagation();
              e.stopImmediatePropagation();
              sessionStorage.setItem("sidebarOpen", "true");
              var url = new URL(window.location.href);
              ["name", "filter_type", "xmin", "xmax", "ymin", "ymax"].forEach(function (k) {
                url.searchParams.delete(k);
              });
              window.location.href = url.toString();
              return false;
            }
          },
          true
        );
      }

      clonedForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var params = new URLSearchParams(new FormData(clonedForm));
        var url = new URL(window.location.href);
        ["name", "filter_type"].forEach(function (k) { url.searchParams.delete(k); });
        params.forEach(function (val, key) {
          if (val) url.searchParams.append(key, val);
        });
        window.location.href = url.toString();
      });

      body
        .querySelectorAll(
          'input[type="text"], input[type="date"], input[type="search"], select'
        )
        .forEach(function (el) {
          el.style.width = "100%";
          el.style.maxWidth = "230px";
          el.style.fontSize = "0.8rem";
          el.style.padding = "0.3rem";
          el.style.marginBottom = "0.4rem";
          el.style.border = "1px solid #555";
          el.style.borderRadius = "4px";
          el.style.boxSizing = "border-box";
          el.style.backgroundColor = "#1e1e1e";
          el.style.color = "#e0e0e0";
        });

      body.querySelectorAll(".form-group").forEach(function (fg) {
        fg.style.marginBottom = "0.8rem";
        fg.style.marginLeft = "0";
        fg.style.marginRight = "0";
      });

      body.querySelectorAll(".form-label").forEach(function (lbl) {
        lbl.style.fontSize = "0.8rem";
        lbl.style.fontWeight = "500";
        lbl.style.marginBottom = "0.3rem";
        lbl.style.display = "block";
        lbl.style.color = "#e0e0e0";
      });

      body.querySelectorAll(".row, .expeditionRow").forEach(function (row) {
        row.style.marginLeft = "0";
        row.style.marginRight = "0";
        row.style.setProperty("display", "flex", "important");
        row.style.flexWrap = "wrap";
        row.style.flexDirection = "column";
        row.style.setProperty("visibility", "visible", "important");
        row.style.setProperty("opacity", "1", "important");
      });

      body.querySelectorAll(".col-md, [class*='col-']").forEach(function (col) {
        col.style.paddingLeft = "0.25rem";
        col.style.paddingRight = "0.25rem";
        col.style.setProperty("width", "100%", "important");
        col.style.setProperty("flex-basis", "100%", "important");
        col.style.maxWidth = "none";
      });

      var formInBody = body.querySelector("form");
      if (formInBody) {
        formInBody.style.top = "0";
        formInBody.style.position = "relative";
        formInBody.style.width = "100%";
        formInBody.style.marginTop = "0";
        formInBody.style.marginLeft = "0";
        formInBody.style.marginRight = "0";
        formInBody.style.paddingTop = "0";
        formInBody.style.paddingLeft = "0";
        formInBody.style.paddingRight = "0";
      }

      if (typeof setupCheckboxDropdowns === "function") {
        setupCheckboxDropdowns(clonedForm, recalcSidebarHeight);
      }

      setTimeout(function () {
        if (sidebar) {
          sidebar.style.height = "auto";
        }
      }, 150);

      return true;
    };

    var retryCount = 0;
    var maxRetries = 10;
    var tryCopyForm = function () {
      if (copyForm()) {
        // success
      } else {
        retryCount++;
        if (retryCount < maxRetries) setTimeout(tryCopyForm, 300);
      }
    };

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        setTimeout(tryCopyForm, 200);
      });
    } else {
      setTimeout(tryCopyForm, 200);
    }

    // Open / close sidebar
    var sidebarOpen = false;

    function showSidebar() {
      sidebar.style.left = "0px";
      buttonWrapper.style.left = "250px";
      var b = document.getElementById("filter-sidebar-body");
      if (b) {
        var formEl = b.querySelector("form");
        if (formEl) {
          formEl.style.top = "0";
          formEl.style.position = "relative";
          formEl.style.width = "100%";
          formEl.style.marginTop = "0";
          formEl.style.paddingTop = "0";
        }
        sidebar.style.height = "auto";
      }
    }

    function hideSidebar() {
      sidebar.style.left = "-250px";
      buttonWrapper.style.left = "20px";
    }

    if (sessionStorage.getItem("sidebarOpen") === "true") {
      sidebarOpen = true;
      showSidebar();
      sessionStorage.removeItem("sidebarOpen");
    }

    L.DomEvent.on(container, "click", function (e) {
      L.DomEvent.stopPropagation(e);
      sidebarOpen = !sidebarOpen;
      if (sidebarOpen) showSidebar();
      else hideSidebar();
    });

    L.DomEvent.disableClickPropagation(sidebar);
    L.DomEvent.disableScrollPropagation(sidebar);

    return wrapper;
  },
});

const filterControl = new FilterControl({ position: "topleft" });
filterControl.addTo(map);

setTimeout(function () {
  var ctrl = filterControl.getContainer();
  if (ctrl) {
    ctrl.style.background = "transparent";
    ctrl.style.border = "none";
    ctrl.style.boxShadow = "none";
    ctrl.style.outline = "none";
    ctrl.style.margin = "0";
    ctrl.style.padding = "0";
    ctrl.style.width = "auto";
    ctrl.style.height = "auto";
    ctrl.style.minWidth = "0";
    ctrl.style.minHeight = "0";
  }
  var p = ctrl ? ctrl.parentElement : null;
  while (p && p !== document.body) {
    if (
      p.classList.contains("leaflet-control") ||
      p.classList.contains("leaflet-top") ||
      p.classList.contains("leaflet-left")
    ) {
      p.style.boxShadow = "none";
      p.style.background = "transparent";
      p.style.border = "none";
    }
    p = p.parentElement;
  }
}, 100);

// ---------------------------------------------------------------------------
// Draw Rectangle (box search) control
// ---------------------------------------------------------------------------
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var rectangleDrawer = new L.Draw.Rectangle(map, {
  shapeOptions: {
    color: "#FFFF00",
    fillColor: "#FFFF00",
    fillOpacity: 0.2,
    weight: 2,
  },
});

var DrawSquareButton = L.Control.extend({
  onAdd: function (map) {
    var wrapper = L.DomUtil.create("div", "draw-square-wrapper");
    wrapper.style.cssText =
      "position:relative;width:40px;height:40px;background:transparent;" +
      "border:none;box-shadow:none;margin:0;padding:0;";

    var btn = L.DomUtil.create("div", "draw-square-control", wrapper);
    btn.id = "drawSquare-button";
    btn.setAttribute("aria-label", "Draw a square around expeditions to filter by area.");
    var tooltipEl = L.DomUtil.create("span", "map-control-tooltip", wrapper);
    tooltipEl.textContent = "Draw a square to filter expeditions by area";
    tooltipEl.setAttribute("role", "tooltip");
    btn.style.cssText =
      "width:40px;height:40px;background:hsla(0,0%,100%,0.75);border-radius:4px;" +
      "cursor:pointer;display:flex;flex-direction:column;align-items:center;" +
      "justify-content:center;box-shadow:0 1px 5px rgba(0,0,0,0.4);position:relative;" +
      "z-index:1001;transition:all 0.2s ease;border:1px solid rgba(0,0,0,0.3);" +
      "outline:none;margin:0;padding:0;";

    var icon = L.DomUtil.create("i", "fa-regular fa-square", btn);
    icon.id = "draw-square-icon";
    icon.style.fontSize = "22px";
    icon.style.color = "#007bff";
    icon.style.webkitTextStroke = "2.5px #007bff";
    icon.style.webkitTextFillColor = "transparent";
    icon.style.textStroke = "2.5px #007bff";
    icon.style.textFillColor = "transparent";

    L.DomEvent.disableClickPropagation(btn);
    L.DomEvent.on(btn, "click", function (e) {
      L.DomEvent.stopPropagation(e);
      e.preventDefault();
      rectangleDrawer.enable();
    });

    return wrapper;
  },
});

const drawSquareButton = new DrawSquareButton({ position: "topright" });
drawSquareButton.addTo(map);

function styleDrawSquareControl() {
  var ctrl = drawSquareButton.getContainer();
  if (!ctrl) { setTimeout(styleDrawSquareControl, 100); return; }
  var lc = ctrl.closest(".leaflet-control");
  if (!lc) {
    lc = ctrl.parentElement;
    while (lc && !lc.classList.contains("leaflet-control")) {
      lc = lc.parentElement;
    }
  }
  if (lc && lc.classList.contains("leaflet-control")) {
    lc.style.background = "transparent";
    lc.style.border = "none";
    lc.style.boxShadow = "none";
    lc.style.setProperty("margin-top", "10px", "important");
    lc.style.setProperty("transform", "translateX(-10px)", "important");
    lc.style.padding = "0";
    lc.style.width = "auto";
    lc.style.height = "auto";
    lc.style.minHeight = "0";
    lc.style.minWidth = "0";
    lc.classList.add("draw-square-control-wrapper");
    lc.id = "draw-square-control-wrapper";
  } else {
    setTimeout(styleDrawSquareControl, 100);
  }
}
setTimeout(styleDrawSquareControl, 100);

// When user finishes drawing a rectangle: reload page with bbox params.
map.on(L.Draw.Event.CREATED, function (e) {
  if (e.layerType !== "rectangle") return;
  drawnItems.clearLayers();
  drawnItems.addLayer(e.layer);

  var bounds = e.layer.getBounds();
  var url = new URL(window.location.href);
  // Preserve existing name filter if any
  url.searchParams.set("xmin", bounds.getWest());
  url.searchParams.set("ymin", bounds.getSouth());
  url.searchParams.set("xmax", bounds.getEast());
  url.searchParams.set("ymax", bounds.getNorth());
  window.location.href = url.toString();
});

map.on(L.Draw.Event.DELETED, function () {
  drawnItems.clearLayers();
});

// ---------------------------------------------------------------------------
// Restore drawn rectangle and show clear-banner when bbox params are in URL
// ---------------------------------------------------------------------------
(function () {
  var params = new URLSearchParams(window.location.search);
  var xmin = parseFloat(params.get("xmin"));
  var ymin = parseFloat(params.get("ymin"));
  var xmax = parseFloat(params.get("xmax"));
  var ymax = parseFloat(params.get("ymax"));
  if (isNaN(xmin) || isNaN(ymin) || isNaN(xmax) || isNaN(ymax)) return;

  // Redraw the yellow selection rectangle so the user can see the active area filter.
  var sw = L.latLng(ymin, xmin), ne = L.latLng(ymax, xmax);
  var rect = L.rectangle([sw, ne], {
    color: "#FFFF00", fillColor: "#FFFF00", fillOpacity: 0.15, weight: 2,
  });
  drawnItems.addLayer(rect);

  // Show a dismissible banner below the map header.
  var banner = document.createElement("div");
  banner.id = "bbox-active-banner";
  banner.style.cssText =
    "position:fixed;top:150px;left:50%;transform:translateX(-50%);" +
    "background:#fff3cd;border:1px solid #ffc107;border-radius:4px;" +
    "padding:4px 12px;font-size:0.8rem;color:#856404;z-index:1100;" +
    "display:flex;align-items:center;gap:8px;box-shadow:0 1px 4px rgba(0,0,0,0.2);";
  banner.innerHTML =
    "<span>Area filter active</span>" +
    "<a href='#' style='color:#856404;font-weight:700;text-decoration:none;' " +
    "title='Remove area filter' id='bbox-clear-link'>\u00d7 Clear</a>";
  document.body.appendChild(banner);

  document.getElementById("bbox-clear-link").addEventListener("click", function (e) {
    e.preventDefault();
    var url = new URL(window.location.href);
    ["xmin", "ymin", "xmax", "ymax"].forEach(function (k) { url.searchParams.delete(k); });
    window.location.href = url.toString();
  });
})();

// ---------------------------------------------------------------------------
// Map scale
// ---------------------------------------------------------------------------
L.control.scale({ imperial: false, position: "topright", maxWidth: 70 }).addTo(map);

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
// Table hover → highlight map track and label
// Expedition rows hold multiple missions; wire hover to each mission link
// in the Missions column so hovering any link fires highlightMission().
// ---------------------------------------------------------------------------
function attachTableRowHover() {
  slugRowIndex = {};
  var tableWrapper = document.getElementById("expedition-table-wrapper");
  if (!tableWrapper) return;
  tableWrapper.querySelectorAll('td a[href*="/missions/"]').forEach(function (link) {
    var href = (link.getAttribute("href") || "").replace(/\/$/, "");
    var match = href.match(/\/missions\/([^?#]+)$/);
    if (!match || !match[1]) return;
    var slug = match[1];

    var row = link.closest("tr");
    if (row) {
      if (!slugRowIndex[slug]) slugRowIndex[slug] = [];
      if (slugRowIndex[slug].indexOf(row) === -1) slugRowIndex[slug].push(row);
    }

    link.addEventListener("mouseover", function () { highlightMission(slug); });
    link.addEventListener("mouseout", function () {
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

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------
function _styleBtn(btn, borderColor) {
  btn.style.setProperty("height", "38px", "important");
  btn.style.setProperty("width", "auto", "important");
  btn.style.setProperty("min-height", "38px", "important");
  btn.style.setProperty("max-height", "38px", "important");
  btn.style.setProperty("margin", "0px", "important");
  btn.style.setProperty("padding", "6px 12px", "important");
  btn.style.setProperty("line-height", "26px", "important");
  btn.style.setProperty("border", "1px solid " + borderColor, "important");
  btn.style.setProperty("box-sizing", "border-box", "important");
  btn.style.setProperty("flex", "1 1 auto", "important");
  btn.style.setProperty("align-self", "center", "important");
}
