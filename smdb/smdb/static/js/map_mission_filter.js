/**
 * map_mission_filter.js
 *
 * Missions page map with filter sidebar and box-drawing rectangle search.
 * Mirrors the home page (map.js) filter / draw capabilities, scoped to
 * missions only (no Expedition / Compilation filter type dropdown).
 */

// ---------------------------------------------------------------------------
// Map and base tile layer
// ---------------------------------------------------------------------------
const map = L.map("map_mission_filter");

// Move the default zoom control out of topleft so the filter button sits there cleanly.
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

// Set an initial world view; whenReady() will zoom to mission bounds.
map.setView([39.8423, -26.8945], 3, { animate: false });

let feature = L.geoJSON(missions, {
  style: function () {
    return {
      color: "rgb(139, 64, 0)", // rust — matches home page GMRT default
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
        this._path.addEventListener("mouseover", function () {
          this.classList.add("smdb-hover");
          var sel = 'tr[data-mission-slug="' + CSS.escape(slug) + '"]';
          document.querySelectorAll(sel).forEach(function (tr) { tr.classList.add("smdb-hover"); });
          document.querySelectorAll('.label-mission-name[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (lbl) { lbl.classList.add("smdb-hover"); });
        });
        this._path.addEventListener("mouseout", function () {
          this.classList.remove("smdb-hover");
          var sel = 'tr[data-mission-slug="' + CSS.escape(slug) + '"]';
          document.querySelectorAll(sel).forEach(function (tr) { tr.classList.remove("smdb-hover"); });
          document.querySelectorAll('.label-mission-name[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (lbl) { lbl.classList.remove("smdb-hover"); });
        });
      }
    });
  },
})
  .bindPopup(function (layer) {
    return (
      "<a target='_blank' href='/missions/" +
      layer.feature.properties.slug +
      "'>" +
      layer.feature.properties.slug +
      "</a>: " +
      layer.feature.properties.expedition.name +
      "<br>Route: " +
      layer.feature.properties.route_file
    );
  })
  .addTo(map);

// Fit map to mission bounds once the map is ready.
map.whenReady(function () {
  map.invalidateSize();
  setTimeout(function () {
    try {
      if (!hasMissions) {
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      var featureLayers = feature.getLayers();
      if (!featureLayers || featureLayers.length === 0) {
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      var bounds;
      try {
        bounds = feature.getBounds();
      } catch (e) {
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      if (!bounds || !bounds.isValid || !bounds.isValid()) {
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      var sw = bounds.getSouthWest();
      var ne = bounds.getNorthEast();
      var latSpan = ne.lat - sw.lat;
      var lngSpan = ne.lng - sw.lng;
      if (
        lngSpan >= 360 ||
        latSpan >= 180 ||
        isNaN(latSpan) ||
        isNaN(lngSpan) ||
        lngSpan > 350 ||
        latSpan > 170
      ) {
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      map.fitBounds(bounds, { padding: [100, 100] });
    } catch (err) {
      // console.log(err.message);
      map.setView([39.8423, -26.8945], 3, { animate: false });
    }
  }, 100);
});

// Mission name labels (markers beside start of each track — issue #293: offset + hover link)
if (hasMissions && missions.features) {
  var labelOffsetDeg = 0.0012;
  for (var i = 0; i < missions.features.length; i++) {
    var mission = missions.features[i];
    var coords = mission.geometry.coordinates;
    var slug = (mission.properties && mission.properties.slug) ? mission.properties.slug : "";
    var lat0, lng0, latlng;
    try {
      lat0 = coords[0][1];
      lng0 = coords[0][0];
      latlng = L.latLng(lat0, lng0);
    } catch (err) {
      continue;
    }
    // Offset label perpendicular to first segment so it sits beside the track, not on it.
    if (coords.length >= 2) {
      var lat1 = coords[1][1];
      var lng1 = coords[1][0];
      var dlat = lat1 - lat0;
      var dlng = lng1 - lng0;
      var len = Math.sqrt(dlat * dlat + dlng * dlng) || 1;
      var perpLat = (-dlng / len) * labelOffsetDeg;
      var perpLng = (dlat / len) * labelOffsetDeg;
      latlng = L.latLng(lat0 + perpLat, lng0 + perpLng);
    }
    var marker = L.marker(latlng, {
      icon: L.divIcon({
        className: "label-mission-name",
        html:
          "<a target='_blank' href='/missions/" +
          (mission.properties.slug ? mission.properties.slug : "") +
          "'>" +
          (mission.properties.slug ? mission.properties.slug : "") +
          "</a>",
      }),
    });
    (function (missionSlug) {
      marker.on("add", function () {
        var el = this._icon;
        if (!el || !missionSlug) return;
        el.setAttribute("data-mission-slug", missionSlug);
        el.addEventListener("mouseover", function () {
          el.classList.add("smdb-hover");
          var sel = 'path[data-mission-slug="' + CSS.escape(missionSlug) + '"]';
          var mapEl = document.getElementById("map_mission_filter");
          if (mapEl) mapEl.querySelectorAll(sel).forEach(function (p) { p.classList.add("smdb-hover"); });
          document.querySelectorAll('tr[data-mission-slug="' + CSS.escape(missionSlug) + '"]').forEach(function (tr) { tr.classList.add("smdb-hover"); });
        });
        el.addEventListener("mouseout", function () {
          el.classList.remove("smdb-hover");
          var mapEl = document.getElementById("map_mission_filter");
          if (mapEl) mapEl.querySelectorAll('path[data-mission-slug="' + CSS.escape(missionSlug) + '"]').forEach(function (p) { p.classList.remove("smdb-hover"); });
          document.querySelectorAll('tr[data-mission-slug="' + CSS.escape(missionSlug) + '"]').forEach(function (tr) { tr.classList.remove("smdb-hover"); });
        });
      });
    })(slug);
    marker.addTo(map);
  }
}

// ---------------------------------------------------------------------------
// Filter sidebar control (missions only — no expedition / compilation tabs)
// ---------------------------------------------------------------------------
const FilterControl = L.Control.extend({
  onAdd: function (map) {
    // Outer wrapper — Leaflet positions this div.
    const wrapper = L.DomUtil.create("div", "filter-wrapper");
    wrapper.style.cssText =
      "position:relative;width:40px;height:50px;transition:width 0.3s ease;" +
      "z-index:1000;background:transparent;border:none;box-shadow:none;margin:0;padding:0;";

    // Sidebar panel (slides out from left).
    const sidebar = L.DomUtil.create("div", "filter-sidebar", wrapper);
    sidebar.id = "filter-sidebar";
    sidebar.style.cssText =
      "position:absolute;left:-250px;top:0;width:250px;max-height:250vh;" +
      "height:auto;min-height:50px;background:#2d2d2d;box-shadow:2px 0 12px rgba(0,0,0,0.5);" +
      "border-radius:0 4px 4px 0;color:#e0e0e0;transition:left 0.3s ease,height 0.3s ease;" +
      "overflow:hidden;display:flex;flex-direction:column;z-index:999;pointer-events:auto;";

    // Toggle button.
    const container = L.DomUtil.create("div", "filter-control", wrapper);
    container.id = "filter-button";
    container.title = "Filter Missions";
    container.style.cssText =
      "width:40px;height:40px;background:hsla(0,0%,100%,0.75);border-radius:4px;" +
      "cursor:pointer;display:flex;flex-direction:column;align-items:center;" +
      "justify-content:center;box-shadow:0 1px 5px rgba(0,0,0,0.4);position:absolute;" +
      "top:5px;left:20px;z-index:1001;transition:left 0.3s ease,all 0.2s ease;" +
      "border:1px solid rgba(0,0,0,0.3);outline:none;margin:0;padding:0;";

    const icon = L.DomUtil.create("i", "fas fa-filter", container);
    icon.id = "filter-icon";
    icon.style.cssText = "font-size:18px;color:#007bff;";

    // Badge (hidden by default — could show active filter count).
    const badge = L.DomUtil.create("span", "filter-count-badge", container);
    badge.id = "filter-count-badge";
    badge.style.cssText =
      "position:absolute;top:-2px;right:-2px;background:#dc3545;color:white;" +
      "border-radius:50%;width:14px;height:14px;font-size:9px;display:none;" +
      "align-items:center;justify-content:center;";

    // Header.
    const header = L.DomUtil.create("div", "filter-sidebar-header", sidebar);
    header.style.cssText =
      "padding:0.5rem;padding-right:50px;border-bottom:1px solid #555;" +
      "background:#1e1e1e;display:flex;justify-content:flex-start;" +
      "align-items:center;flex-shrink:0;";

    const title = L.DomUtil.create("h6", "", header);
    title.textContent = "Filter Missions";
    title.style.cssText =
      "margin:0;font-size:0.85rem;font-weight:600;margin-left:0.5rem;" +
      "margin-right:0.5rem;color:#ffffff;";

    // Body — the crispy form is cloned into here.
    const body = L.DomUtil.create("div", "filter-sidebar-body", sidebar);
    body.id = "filter-sidebar-body";
    body.style.cssText =
      "padding:0.5rem 0.5rem 0.25rem 0.5rem;overflow-y:auto;overflow-x:hidden;" +
      "padding-bottom:0.25rem;flex:1;min-height:200px;" +
      "max-height:calc(50vh - 60px);";

    // ------------------------------------------------------------------
    // copyForm — clone the hidden crispy form into the sidebar body
    // ------------------------------------------------------------------
    // Guard flag: the body "Clear" listener must only be added once even
    // if copyForm() is retried multiple times by the retry loop below.
    var clearListenerAdded = false;

    // -----------------------------------------------------------------------
    // recalcSidebarHeight — recompute sidebar height after a dropdown opens
    // or closes (CheckboxSelectMultiple accordion).
    // -----------------------------------------------------------------------
    function recalcSidebarHeight() {
      if (!sidebar) return;
      var mapEl = document.getElementById("map_mission_filter");
      var mapH  = mapEl ? mapEl.clientHeight : Math.round(window.innerHeight * 0.5);
      var b = document.getElementById("filter-sidebar-body");
      if (!b) return;
      var hdrH = sidebar.querySelector(".filter-sidebar-header")
        ? sidebar.querySelector(".filter-sidebar-header").offsetHeight
        : 50;
      var pad =
        parseFloat(window.getComputedStyle(b).paddingTop) +
        parseFloat(window.getComputedStyle(b).paddingBottom);
      sidebar.style.height =
        Math.min(b.scrollHeight + hdrH + pad, mapH) + "px";
    }

    // -----------------------------------------------------------------------
    // setupCheckboxDropdowns — turn each CheckboxSelectMultiple group into a
    // collapsible accordion.
    //
    // crispy-forms + Bootstrap 5 renders CheckboxSelectMultiple as:
    //   <div id="div_id_FIELD[-sidebar]" class="mb-3">   ← field wrapper
    //     <fieldset>
    //       <legend class="form-label">LABEL</legend>    ← toggle target
    //       <div>                                        ← checkbox panel
    //         <div class="form-check">
    //           <input type="checkbox" ...>
    //           <label class="form-check-label">...</label>
    //         </div>
    //         ...
    //       </div>
    //     </fieldset>
    //   </div>
    // -----------------------------------------------------------------------
    function setupCheckboxDropdowns(formEl) {
      formEl.querySelectorAll('[id^="div_id_"]').forEach(function (outerDiv) {
        var checks = outerDiv.querySelectorAll(".form-check");
        if (checks.length === 0) return;  // not a checkbox group

        // The legend (or label) is the field-level heading element.
        var toggleEl = outerDiv.querySelector("legend") ||
                       outerDiv.querySelector("label.form-label");
        if (!toggleEl) return;

        // The checkbox panel is the direct parent of the .form-check items.
        var panel = checks[0].parentElement;
        if (!panel) return;

        // Style the legend as a clickable dropdown toggle — identical to the
        // <select> elements in the sidebar (background #1e1e1e, white text).
        var TOGGLE_BG     = "#1e1e1e";
        var TOGGLE_BORDER = "#555";

        toggleEl.style.cssText =
          "display:flex;justify-content:space-between;align-items:center;" +
          "width:100%;max-width:230px;padding:0.3rem;box-sizing:border-box;" +
          "background:" + TOGGLE_BG + ";border:1px solid " + TOGGLE_BORDER + ";" +
          "border-radius:4px;cursor:pointer;color:#e0e0e0;font-size:0.8rem;" +
          "margin-bottom:0;user-select:none;display:flex;" +
          "justify-content:space-between;align-items:center;";

        // Use the same Bootstrap 5 chevron SVG that <select> uses, white-tinted.
        var caret = document.createElement("span");
        caret.innerHTML = "&#8964;";   // ⌄ downward chevron
        caret.style.cssText =
          "font-size:0.9rem;font-weight:bold;line-height:1;" +
          "transition:transform 0.2s;flex-shrink:0;color:#e0e0e0;";
        toggleEl.appendChild(caret);

        // Hover: match project.css .form-control:hover exactly —
        //   box-shadow: inset 0 1px 1px rgba(0,0,0,0.075), 0 0 8px cornflowerblue
        // The sidebar <select> elements get this via the CSS rule; we apply it
        // inline here so the legend toggle is pixel-identical.
        toggleEl.addEventListener("mouseenter", function () {
          toggleEl.style.boxShadow =
            "inset 0 1px 1px rgba(0,0,0,0.075), 0 0 8px cornflowerblue";
        });
        toggleEl.addEventListener("mouseleave", function () {
          toggleEl.style.boxShadow = "none";
        });

        // Remove <fieldset> browser-default border and padding so the toggle
        // and panel sit flush with each other.
        var fieldset = outerDiv.querySelector("fieldset");
        if (fieldset) {
          fieldset.style.cssText = "border:none;padding:0;margin:0;min-width:0;";
        }

        // Style the checkbox panel.
        panel.style.cssText =
          "padding:0.15rem 0 0.15rem 10px;margin:0;" +
          "background:#2a2a2a;border:1px solid #555;border-top:none;" +
          "border-radius:0 0 4px 4px;";
        panel.querySelectorAll(".form-check").forEach(function (chk) {
          // Only override vertical spacing — Bootstrap 5 needs padding-left:1.5em
          // to position the floated checkbox input correctly; touching it moves
          // the checkboxes hard-left outside their labels.
          chk.style.marginBottom = "0";
          chk.style.paddingTop = "0.15rem";
          chk.style.paddingBottom = "0.15rem";
          chk.style.minHeight = "unset";
        });
        panel.querySelectorAll(".form-check-label").forEach(function (lbl) {
          lbl.style.color = "#e0e0e0";
          lbl.style.fontSize = "0.8rem";
          lbl.style.cursor = "pointer";
          lbl.style.margin = "0";
        });

        // Start collapsed; auto-open if any item is already checked.
        var hasChecked = !!panel.querySelector("input[type='checkbox']:checked");
        panel.style.display = hasChecked ? "block" : "none";
        if (hasChecked) caret.style.transform = "rotate(180deg)";

        // Toggle open/close on legend click.
        toggleEl.addEventListener("click", function (e) {
          e.preventDefault();
          var open = panel.style.display !== "none";
          panel.style.display = open ? "none" : "block";
          caret.style.transform = open ? "" : "rotate(180deg)";
          setTimeout(recalcSidebarHeight, 50);
        });
      });
    }

    const copyForm = function () {
      const formContainer = document.getElementById("filter-form-container");
      if (!formContainer) return false;

      const formWrapper = formContainer.querySelector("#filter-form-mission");
      if (!formWrapper) return false;

      const form = formWrapper.querySelector("form") || formWrapper;
      if (!form || form.children.length === 0) return false;

      body.innerHTML = "";

      const clonedForm = form.cloneNode(true);
      clonedForm.id = "filter-form-mission";
      clonedForm.className = "filter-form";
      clonedForm.setAttribute("data-filter-type", "mission");
      clonedForm.method = "get";
      clonedForm.action = window.location.pathname;
      clonedForm.style.display = "block";

      // Suffix every id in the clone with "-sidebar" so they don't collide
      // with the hidden original form's ids (duplicate IDs break label
      // targeting and any querySelector/getElementById that assumes uniqueness).
      clonedForm.querySelectorAll("[id]").forEach(function (el) {
        el.id = el.id + "-sidebar";
      });
      clonedForm.querySelectorAll("label[for]").forEach(function (lbl) {
        lbl.setAttribute("for", lbl.getAttribute("for") + "-sidebar");
      });

      // Remove any onclick attributes left by crispy forms Clear buttons
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

      // Hidden input so views.py knows this is a mission filter submission.
      const filterTypeInput = document.createElement("input");
      filterTypeInput.type = "hidden";
      filterTypeInput.name = "filter_type";
      filterTypeInput.value = "mission";
      clonedForm.appendChild(filterTypeInput);

      body.appendChild(clonedForm);

      // Dynamically-created Filter / Clear button row.
      const buttonRow = document.createElement("div");
      buttonRow.className = "button-row mb-3";
      buttonRow.style.cssText =
        "display:flex;align-items:center;gap:0.5rem;margin-top:1.5rem;" +
        "margin-bottom:0.5rem;width:100%;";

      const filterBtn = document.createElement("button");
      filterBtn.type = "submit";
      filterBtn.id = "missionFilterSubmit";
      filterBtn.className = "btn btn-primary";
      filterBtn.textContent = "Filter";
      _styleBtn(filterBtn, "#007bff");

      const clearBtn = document.createElement("button");
      clearBtn.type = "reset";
      clearBtn.id = "missionFilterCancel";
      clearBtn.className = "btn btn-secondary";
      clearBtn.textContent = "Clear";
      _styleBtn(clearBtn, "#6c757d");

      buttonRow.appendChild(filterBtn);
      buttonRow.appendChild(clearBtn);
      clonedForm.appendChild(buttonRow);

      // Re-apply button sizes after DOM is settled.
      setTimeout(function () {
        [filterBtn, clearBtn].forEach(function (btn) {
          _styleBtn(btn, btn.classList.contains("btn-primary") ? "#007bff" : "#6c757d");
        });
        buttonRow.style.setProperty("display", "flex", "important");
        buttonRow.style.setProperty("align-items", "center", "important");
      }, 100);

      // Clear button: stay on Missions page, strip filter params.
      // Only attach once — copyForm() may be retried and would otherwise
      // register duplicate handlers on each attempt.
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
            [
              "name", "region_name", "vehicle_name", "platformtype",
              "quality_categories", "patch_test",
              "repeat_survey", "mgds_compilation", "citation", "expedition__name",
              "filter_type", "q", "xmin", "xmax", "ymin", "ymax",
              "tmin", "tmax",
            ].forEach(function (k) { url.searchParams.delete(k); });
            window.location.href = url.toString();
            return false;
          }
        },
        true
      );
      } // end if (!clearListenerAdded)

      // Form submit: reload Missions page with filter params in URL.
      clonedForm.addEventListener("submit", function (e) {
        e.preventDefault();
        var params = new URLSearchParams(new FormData(clonedForm));
        var url = new URL(window.location.href);
        [
          "name", "region_name", "vehicle_name", "platformtype",
          "quality_categories", "patch_test",
          "repeat_survey", "mgds_compilation", "citation", "expedition__name",
          "filter_type",
        ].forEach(function (k) { url.searchParams.delete(k); });
        // Use append (not set) to preserve all checkbox values for multi-select fields.
        params.forEach(function (val, key) {
          if (val) url.searchParams.append(key, val);
        });
        window.location.href = url.toString();
      });

      // Style form inputs for the dark sidebar theme.
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

      // Strip crispy-forms row/column chrome to fit the narrow sidebar.
      body.querySelectorAll(".row, .missionRow").forEach(function (row) {
        row.style.marginLeft = "0";
        row.style.marginRight = "0";
        row.style.setProperty("display", "flex", "important");
        row.style.flexWrap = "wrap";
        row.style.flexDirection = "column"; // stack fields vertically
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

      // Fix form positioning overrides from project.css.
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

      // Convert CheckboxSelectMultiple groups into collapsible accordions.
      setupCheckboxDropdowns(clonedForm);

      // Auto-adjust sidebar height.
      setTimeout(function () {
        if (sidebar) {
          var bodyH = body.scrollHeight;
          var headerH =
            sidebar.querySelector(".filter-sidebar-header")
              ? sidebar.querySelector(".filter-sidebar-header").offsetHeight
              : 50;
          var bodyPad =
            parseFloat(window.getComputedStyle(body).paddingTop) +
            parseFloat(window.getComputedStyle(body).paddingBottom);
          sidebar.style.height =
            Math.min(bodyH + headerH + bodyPad, window.innerHeight * 0.8) +
            "px";
        }
      }, 150);

      return true;
    };

    // Retry logic — Django template rendering may not be complete immediately.
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

    // ------------------------------------------------------------------
    // Open / close sidebar
    // ------------------------------------------------------------------
    var sidebarOpen = false;

    function showSidebar() {
      sidebar.style.left = "0px";
      container.style.left = "250px";
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
        var bodyH = b.scrollHeight;
        var hdrH =
          sidebar.querySelector(".filter-sidebar-header")
            ? sidebar.querySelector(".filter-sidebar-header").offsetHeight
            : 50;
        var pad =
          parseFloat(window.getComputedStyle(b).paddingTop) +
          parseFloat(window.getComputedStyle(b).paddingBottom);
        var mapEl2 = document.getElementById("map_mission_filter");
        var mapH2  = mapEl2 ? mapEl2.clientHeight : Math.round(window.innerHeight * 0.5);
        sidebar.style.height = Math.min(bodyH + hdrH + pad, mapH2) + "px";
      }
    }

    function hideSidebar() {
      sidebar.style.left = "-250px";
      container.style.left = "20px";
    }

    // Re-open sidebar after Clear button reloads the page.
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

// Strip Leaflet's default control border/shadow/margin from the filter control wrapper.
// Leaflet adds the leaflet-control class to ctrl itself (the onAdd() return value),
// not to its parent — so we reset ctrl directly, then walk up to clear parents too.
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
    color: "#FFFF00",       // yellow, same as home page
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
    btn.title = "Draw a rectangle to search for missions in that area.";
    btn.style.cssText =
      "width:40px;height:40px;background:hsla(0,0%,100%,0.75);border-radius:4px;" +
      "cursor:pointer;display:flex;flex-direction:column;align-items:center;" +
      "justify-content:center;box-shadow:0 1px 5px rgba(0,0,0,0.4);position:relative;" +
      "z-index:1001;transition:all 0.2s ease;border:1px solid rgba(0,0,0,0.3);" +
      "outline:none;margin:0;padding:0;";

    var icon = L.DomUtil.create("i", "fa-regular fa-square", btn);
    icon.id = "draw-square-icon";
    icon.style.fontSize = "22px";
    icon.style.color = "#007bff";             // drives SVG currentColor fill
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

// Strip Leaflet's default styling from the draw-square control wrapper.
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
setTimeout(styleDrawSquareControl, 500);

// Store drawn-rectangle bounds globally for use by exportMissions().
window.drawnRectangleBounds = null;

// When user finishes drawing a rectangle: show the results panel.
map.on(L.Draw.Event.CREATED, function (e) {
  if (e.layerType !== "rectangle") return;
  drawnItems.clearLayers();
  drawnItems.addLayer(e.layer);

  var bounds = e.layer.getBounds();
  var bbox = {
    xmin: bounds.getWest(),
    ymin: bounds.getSouth(),
    xmax: bounds.getEast(),
    ymax: bounds.getNorth(),
  };
  window.drawnRectangleBounds = bbox;

  // Collect any active filter params from the current URL.
  var urlParams = new URLSearchParams(window.location.search);
  var filterParams = {};
  [
    "name", "region_name", "quality_categories", "patch_test",
    "repeat_survey", "mgds_compilation", "citation", "expedition__name",
    "filter_type", "q", "tmin", "tmax",
  ].forEach(function (k) {
    if (urlParams.has(k)) filterParams[k] = urlParams.get(k);
  });
  filterParams.xmin = bbox.xmin;
  filterParams.xmax = bbox.xmax;
  filterParams.ymin = bbox.ymin;
  filterParams.ymax = bbox.ymax;

  showResultsPanel(true);
  updateResultsPanel("Loading missions...", []);
  fetchFilteredMissions(filterParams);
});

// When the drawn layer is deleted: clear bounds but keep panel open.
map.on(L.Draw.Event.DELETED, function () {
  drawnItems.clearLayers();
  window.drawnRectangleBounds = null;
});

// ---------------------------------------------------------------------------
// Map scale
// ---------------------------------------------------------------------------
L.control.scale({ imperial: false, position: "topright", maxWidth: 70 }).addTo(map);

// ---------------------------------------------------------------------------
// Results panel
// ---------------------------------------------------------------------------
function showResultsPanel(loading) {
  var panel = document.getElementById("selection-results-panel");
  if (!panel) {
    panel = document.createElement("div");
    panel.id = "selection-results-panel";
    panel.className = "selection-results-panel";
    panel.innerHTML =
      '<div class="selection-results-header">' +
        '<h5>Selected Missions</h5>' +
        '<button type="button" class="btn-close" onclick="hideResultsPanel()" aria-label="Close">\xd7</button>' +
      "</div>" +
      '<div class="selection-results-body">' +
        '<div id="selection-results-content"></div>' +
      "</div>" +
      '<div class="resize-handle resize-handle-n"></div>' +
      '<div class="resize-handle resize-handle-e"></div>' +
      '<div class="resize-handle resize-handle-s"></div>' +
      '<div class="resize-handle resize-handle-w"></div>' +
      '<div class="resize-handle resize-handle-ne"></div>' +
      '<div class="resize-handle resize-handle-nw"></div>' +
      '<div class="resize-handle resize-handle-se"></div>' +
      '<div class="resize-handle resize-handle-sw"></div>';
    document.body.appendChild(panel);

    // Stop map interactions when mouse is over the panel.
    panel.addEventListener("click",     function (e) { e.stopPropagation(); });
    panel.addEventListener("mousedown", function (e) { e.stopPropagation(); });
    panel.addEventListener("wheel", function (e) {
      e.stopPropagation();
      var b = panel.querySelector(".selection-results-body");
      if (b && b.scrollHeight > b.clientHeight) {
        e.preventDefault();
        b.scrollTop += e.deltaY;
        e.stopImmediatePropagation();
      }
    }, { passive: false });

    // Drag-to-move the panel.
    var isDragging = false, dragOffX = 0, dragOffY = 0;
    var panelHeader = panel.querySelector(".selection-results-header");
    if (panelHeader) {
      panelHeader.addEventListener("mousedown", function (e) {
        if (e.target.classList.contains("btn-close")) return;
        isDragging = true;
        var rect = panel.getBoundingClientRect();
        dragOffX = e.clientX - rect.left;
        dragOffY = e.clientY - rect.top;
        panel.style.transform = "none";
        e.preventDefault();
      });
    }
    document.addEventListener("mousemove", function (e) {
      if (!isDragging) return;
      panel.style.left = e.clientX - dragOffX + "px";
      panel.style.top  = e.clientY - dragOffY + "px";
    });
    document.addEventListener("mouseup", function () { isDragging = false; });

    // Resize handles.
    _attachResizeHandles(panel);
  }

  panel.style.display = "flex";
  if (loading) {
    var content = document.getElementById("selection-results-content");
    if (content)
      content.innerHTML =
        '<div class="alert alert-info m-3">Loading missions\u2026</div>';
  }
}

function hideResultsPanel() {
  var panel = document.getElementById("selection-results-panel");
  if (panel) panel.style.display = "none";
  drawnItems.clearLayers();
  window.drawnRectangleBounds = null;
}

function updateResultsPanel(message, missions) {
  var content = document.getElementById("selection-results-content");
  if (!content) return;

  if (!missions || missions.length === 0) {
    content.innerHTML = message
      ? '<div class="alert alert-secondary m-3">' + _escapeHtml(message) + "</div>"
      : '<div class="alert alert-info m-3">No missions found in the selected area.</div>';
    return;
  }

  var html =
    '<div class="selection-results-info p-3 border-bottom">' +
      "<strong>" +
      missions.length +
      " mission" +
      (missions.length !== 1 ? "s" : "") +
      " found</strong>" +
      '<div class="mt-2 d-flex justify-content-end">' +
        '<a href="#" class="btn btn-sm btn-primary" style="min-width:120px;margin-right:20px;" ' +
        'onclick="exportMissions(\'csv\')">Export CSV</a>' +
        '<a href="#" class="btn btn-sm btn-success" style="min-width:120px;" ' +
        'onclick="exportMissions(\'excel\')">Export Excel</a>' +
      "</div>" +
    "</div>" +
    '<div class="table-responsive">' +
    '<table class="table table-sm table-striped table-hover">' +
    '<thead class="table-light sticky-top"><tr>' +
    "<th>Name</th><th>Start Date</th><th>Region</th>" +
    "<th>Track Length</th><th>Start Depth</th><th>Vehicle</th><th>Expedition</th>" +
    "</tr></thead><tbody>";

  missions.forEach(function (m) {
    var missionSlug = m.slug ? String(m.slug) : "";
    html +=
      "<tr" + (missionSlug ? ' data-mission-slug="' + _escapeHtml(missionSlug) + '"' : "") + ">" +
      '<td><a href="/missions/' +
      (m.slug ? encodeURIComponent(m.slug) : "") +
      '/">' +
      _escapeHtml(m.name) +
      "</a></td>" +
      "<td>" + (m.start_date ? _escapeHtml(String(m.start_date)) : "-") + "</td>" +
      "<td>" + (m.region_name ? _escapeHtml(String(m.region_name)) : "-") + "</td>" +
      "<td>" + (m.track_length ? _escapeHtml(String(m.track_length)) : "-") + "</td>" +
      "<td>" + (m.start_depth ? _escapeHtml(String(m.start_depth)) : "-") + "</td>" +
      "<td>" + (m.vehicle_name ? _escapeHtml(String(m.vehicle_name)) : "-") + "</td>" +
      "<td>" + (m.expedition_name ? _escapeHtml(String(m.expedition_name)) : "-") + "</td>" +
      "</tr>";
  });

  html += "</tbody></table></div>";
  content.innerHTML = html;

  // Bidirectional hover: row hover highlights track (issue #293).
  content.querySelectorAll("tr[data-mission-slug]").forEach(function (tr) {
    var slug = tr.getAttribute("data-mission-slug");
    if (!slug) return;
    tr.addEventListener("mouseover", function () {
      tr.classList.add("smdb-hover");
      var mapEl = document.getElementById("map_mission_filter");
      if (mapEl) mapEl.querySelectorAll('path[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (p) { p.classList.add("smdb-hover"); });
      document.querySelectorAll('.label-mission-name[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (lbl) { lbl.classList.add("smdb-hover"); });
    });
    tr.addEventListener("mouseout", function () {
      tr.classList.remove("smdb-hover");
      var mapEl = document.getElementById("map_mission_filter");
      if (mapEl) mapEl.querySelectorAll('path[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (p) { p.classList.remove("smdb-hover"); });
      document.querySelectorAll('.label-mission-name[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (lbl) { lbl.classList.remove("smdb-hover"); });
    });
  });

  window.selectedMissions = missions;
}

function fetchFilteredMissions(filterParams) {
  var qs = Object.keys(filterParams)
    .map(function (k) {
      var v = filterParams[k];
      return encodeURIComponent(k) + "=" + encodeURIComponent(v != null ? String(v) : "");
    })
    .join("&");

  fetch("/api/v1/missions/select?" + qs)
    .then(function (resp) {
      return resp.text().then(function (text) {
        if (!resp.ok) {
          var msg = "Request failed (" + resp.status + ")";
          try { var d = JSON.parse(text); if (d && d.error) msg = d.error; } catch (e) {}
          throw new Error(msg);
        }
        return text ? JSON.parse(text) : {};
      });
    })
    .then(function (data) {
      updateResultsPanel("", data.missions || []);
    })
    .catch(function (err) {
      updateResultsPanel(
        "Error loading missions. " + (err.message || "Please try again."),
        []
      );
    });
}

function exportMissions(format) {
  var bbox = window.drawnRectangleBounds;
  if (!bbox && drawnItems && drawnItems.getLayers().length > 0) {
    var layer = drawnItems.getLayers()[0];
    if (layer instanceof L.Rectangle) {
      var b = layer.getBounds();
      bbox = {
        xmin: b.getWest(), ymin: b.getSouth(),
        xmax: b.getEast(), ymax: b.getNorth(),
      };
    }
  }
  if (!bbox) {
    alert("No selection area found. Please draw a rectangle first.");
    return;
  }

  var urlParams = new URLSearchParams(window.location.search);
  var filterParams = {};
  [
    "name", "region_name", "quality_categories", "patch_test",
    "repeat_survey", "mgds_compilation", "citation", "expedition__name",
    "filter_type", "q", "tmin", "tmax",
  ].forEach(function (k) {
    if (urlParams.has(k)) filterParams[k] = urlParams.get(k);
  });
  filterParams.xmin = bbox.xmin;
  filterParams.xmax = bbox.xmax;
  filterParams.ymin = bbox.ymin;
  filterParams.ymax = bbox.ymax;
  filterParams.format = format;

  var qs = Object.keys(filterParams)
    .map(function (k) {
      var v = filterParams[k];
      var vStr = v != null ? String(v) : "";
      return encodeURIComponent(k) + "=" + encodeURIComponent(vStr);
    })
    .join("&");

  window.location.href = "/api/v1/missions/export?" + qs;
}

// ---------------------------------------------------------------------------
// Private helpers
// ---------------------------------------------------------------------------
function _escapeHtml(text) {
  if (!text) return "";
  return text
    .toString()
    .replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c];
    });
}

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

// ---------------------------------------------------------------------------
// initTableLayout — pins #mission-table-wrapper to the viewport as a fixed
// element that starts exactly at the map's visual bottom edge and extends to
// the top of the footer.  Using position:fixed means the wrapper is completely
// independent of document-flow quirks (top:150px CSS on the map, Leaflet's
// inline position:relative, etc.) — the layout is driven purely by the
// viewport-relative coordinates returned by getBoundingClientRect().
//
// Side-effects:
//   • The footer is also fixed to the viewport bottom so it stays visible.
//   • The table body is the only thing that scrolls (overflow-y:auto).
// ---------------------------------------------------------------------------
function initTableLayout() {
  var mapEl        = document.getElementById("map_mission_filter");
  var tableWrapper = document.getElementById("mission-table-wrapper");
  if (!tableWrapper || !mapEl) return;

  // 1. Pin the footer to the viewport bottom so it sits above the table.
  var footerEl = document.getElementById("footer");
  var footerH  = 0;
  if (footerEl) {
    footerH = footerEl.offsetHeight;
    footerEl.style.position        = "fixed";
    footerEl.style.bottom          = "0";
    footerEl.style.left            = "0";
    footerEl.style.right           = "0";
    footerEl.style.zIndex          = "2";
    footerEl.style.backgroundColor = "#fff";
  }

  // 2. Fix the table wrapper between the map's visual bottom and the footer.
  //    getBoundingClientRect().bottom already accounts for the CSS top:150px
  //    visual offset (if it's active), scroll position, and viewport geometry.
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
  // Clear any legacy margin/height set by the old approach.
  tableWrapper.style.marginTop = "";
  tableWrapper.style.height    = "";
}

// Run once after the page settles (map needs a moment to render its final
// geometry), then keep in sync with viewport resizes.
setTimeout(initTableLayout, 150);
window.addEventListener("resize", function () {
  if (map) { map.invalidateSize(); }
  setTimeout(initTableLayout, 50);
});

function _attachResizeHandles(panel) {
  var handles = panel.querySelectorAll(".resize-handle");
  handles.forEach(function (handle) {
    handle.addEventListener("mousedown", function (e) {
      if (handle.classList.contains("scrollbar-active")) return;
      e.preventDefault();
      e.stopPropagation();
      var startX = e.clientX, startY = e.clientY;
      var rect = panel.getBoundingClientRect();
      var startW = rect.width, startH = rect.height;
      var startL = rect.left, startT = rect.top;
      var isN  = handle.classList.contains("resize-handle-n");
      var isS  = handle.classList.contains("resize-handle-s");
      var isE  = handle.classList.contains("resize-handle-e");
      var isW  = handle.classList.contains("resize-handle-w");
      var isNE = handle.classList.contains("resize-handle-ne");
      var isNW = handle.classList.contains("resize-handle-nw");
      var isSE = handle.classList.contains("resize-handle-se");
      var isSW = handle.classList.contains("resize-handle-sw");

      panel.style.transform = "none";

      function onMove(ev) {
        var dx = ev.clientX - startX, dy = ev.clientY - startY;
        if (isE  || isNE || isSE) panel.style.width  = Math.max(300, startW + dx) + "px";
        if (isW  || isNW || isSW) { panel.style.width = Math.max(300, startW - dx) + "px"; panel.style.left = startL + dx + "px"; }
        if (isS  || isSE || isSW) panel.style.height = Math.max(200, startH + dy) + "px";
        if (isN  || isNE || isNW) { panel.style.height = Math.max(200, startH - dy) + "px"; panel.style.top = startT + dy + "px"; }
      }
      function onUp() {
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
      }
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onUp);
    });
  });
}

// Attach bidirectional hover to main mission table rows (django_tables2) — issue #293.
function attachMissionTableRowHover() {
  var mapEl = document.getElementById("map_mission_filter");
  if (!mapEl) return;
  document.querySelectorAll("tr[data-mission-slug]").forEach(function (tr) {
    if (tr.closest("#selection-results-content")) return;
    var slug = tr.getAttribute("data-mission-slug");
    if (!slug) return;
    tr.addEventListener("mouseover", function () {
      tr.classList.add("smdb-hover");
      mapEl.querySelectorAll('path[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (p) { p.classList.add("smdb-hover"); });
      document.querySelectorAll('.label-mission-name[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (lbl) { lbl.classList.add("smdb-hover"); });
    });
    tr.addEventListener("mouseout", function () {
      tr.classList.remove("smdb-hover");
      mapEl.querySelectorAll('path[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (p) { p.classList.remove("smdb-hover"); });
      document.querySelectorAll('.label-mission-name[data-mission-slug="' + CSS.escape(slug) + '"]').forEach(function (lbl) { lbl.classList.remove("smdb-hover"); });
    });
  });
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", attachMissionTableRowHover);
} else {
  attachMissionTableRowHover();
}
