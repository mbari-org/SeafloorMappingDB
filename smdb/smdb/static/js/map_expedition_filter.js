const map = L.map("map_expedition_filter");
const options = { minZoom: 1, maxZoom: 20 };

const gmrt = L.tileLayer.wms(
  "https://www.gmrt.org/services/mapserver/wms_merc?",
  {
    layers: "GMRT",
  }
);
gmrt.addTo(map);

map.fitWorld();
const missions = JSON.parse(
  document.getElementById("missions-data").textContent
);

let feature = L.geoJSON(missions)
  .bindPopup(function (layer) {
    return (
      "<a target='_blank' href='/missions/" +
      layer.feature.properties.slug +
      "'>" +
      layer.feature.properties.slug +
      "</a>: " +
      layer.feature.properties.expedition.name
    );
  })
  .addTo(map);

try {
  map.fitBounds(feature.getBounds(), { padding: [100, 100] });
} catch (err) {
  console.log(err.message);
}

for (var i = 0; i < missions.features.length; i++) {
  var mission = missions.features[i];
  try {
    // Use starting point of mission as marker
    var latlng = L.latLng(
      mission.geometry.coordinates[0][1],
      mission.geometry.coordinates[0][0]
    );
  } catch (err) {
    console.log(mission.properties.slug + ": " + err.message);
    continue;
  }
  var marker = L.marker(latlng, {
    icon: L.divIcon({
      className: "label-mission-name",
      html:
        "<a target='_blank' href='/missions/" +
        mission.properties.slug +
        "'>" +
        mission.properties.slug +
        "</a>",
    }),
  });
  marker.addTo(map);
}

// Create Filter Control as Leaflet control (top-left of map)
const FilterControl = L.Control.extend({
  onAdd: function (map) {
    // Create wrapper that contains sidebar and button
    const wrapper = L.DomUtil.create("div", "filter-wrapper");
    wrapper.style.position = "relative";
    wrapper.style.width = "40px";
    wrapper.style.height = "50px";
    wrapper.style.transition = "width 0.3s ease";
    wrapper.style.zIndex = "1000";
    wrapper.style.backgroundColor = "transparent";
    wrapper.style.border = "none";
    wrapper.style.boxShadow = "none";
    wrapper.style.margin = "0";
    wrapper.style.padding = "0";

    // Sidebar panel
    const sidebar = L.DomUtil.create("div", "filter-sidebar", wrapper);
    sidebar.id = "filter-sidebar";
    sidebar.style.position = "absolute";
    sidebar.style.left = "-220px";
    sidebar.style.top = "0";
    sidebar.style.width = "220px";
    sidebar.style.maxHeight = "250vh";
    sidebar.style.height = "auto";
    sidebar.style.minHeight = "50px";
    sidebar.style.backgroundColor = "#2d2d2d";
    sidebar.style.boxShadow = "2px 0 12px rgba(0,0,0,0.5)";
    sidebar.style.borderRadius = "0 4px 4px 0";
    sidebar.style.color = "#e0e0e0";
    sidebar.style.transition = "left 0.3s ease, height 0.3s ease";
    sidebar.style.overflow = "hidden";
    sidebar.style.display = "flex";
    sidebar.style.flexDirection = "column";
    sidebar.style.zIndex = "999";
    sidebar.style.pointerEvents = "auto";

    // Filter button
    const container = L.DomUtil.create("div", "filter-control", wrapper);
    container.id = "filter-button";
    container.style.width = "40px";
    container.style.height = "40px";
    container.style.backgroundColor = "hsla(0, 0%, 100%, 0.75)";
    container.style.borderRadius = "4px";
    container.style.cursor = "pointer";
    container.style.display = "flex";
    container.style.flexDirection = "column";
    container.style.alignItems = "center";
    container.style.justifyContent = "center";
    container.style.boxShadow = "0 1px 5px rgba(0,0,0,0.4)";
    container.style.position = "absolute";
    container.style.top = "5px";
    container.style.left = "20px";
    container.style.zIndex = "1001";
    container.style.transition = "left 0.3s ease, background-color 0.2s ease";
    container.style.border = "none";
    container.style.outline = "none";
    container.style.margin = "0";
    container.style.padding = "0";

    // Filter icon
    const icon = L.DomUtil.create("i", "fas fa-filter", container);
    icon.id = "filter-icon";
    icon.style.fontSize = "18px";
    icon.style.color = "#007bff";

    // Badge
    const badge = L.DomUtil.create("span", "filter-count-badge", container);
    badge.id = "filter-count-badge";
    badge.style.position = "absolute";
    badge.style.top = "-2px";
    badge.style.right = "-2px";
    badge.style.background = "#dc3545";
    badge.style.color = "white";
    badge.style.borderRadius = "50%";
    badge.style.width = "14px";
    badge.style.height = "14px";
    badge.style.fontSize = "9px";
    badge.style.display = "none";

    // Header
    const header = L.DomUtil.create("div", "filter-sidebar-header", sidebar);
    header.style.padding = "0.5rem";
    header.style.paddingRight = "50px";
    header.style.borderBottom = "1px solid #555";
    header.style.background = "#1e1e1e";
    header.style.display = "flex";
    header.style.justifyContent = "flex-start";
    header.style.alignItems = "center";
    header.style.flexShrink = "0";

    const title = L.DomUtil.create("h6", "", header);
    title.textContent = "Filters";
    title.style.margin = "0";
    title.style.fontSize = "0.85rem";
    title.style.fontWeight = "600";
    title.style.marginLeft = "0.5rem";
    title.style.marginRight = "0.5rem";
    title.style.color = "#ffffff";

    // Filter type selector dropdown
    const filterTypeSelect = L.DomUtil.create("select", "filter-type-select", header);
    filterTypeSelect.id = "filter-type-select";
    filterTypeSelect.style.marginLeft = "0.5rem";
    filterTypeSelect.style.padding = "0.2rem 0.4rem";
    filterTypeSelect.style.fontSize = "0.75rem";
    filterTypeSelect.style.backgroundColor = "#2d2d2d";
    filterTypeSelect.style.color = "#e0e0e0";
    filterTypeSelect.style.border = "1px solid #555";
    filterTypeSelect.style.borderRadius = "4px";
    filterTypeSelect.style.cursor = "pointer";

    const optionMission = L.DomUtil.create("option", "", filterTypeSelect);
    optionMission.value = "mission";
    optionMission.textContent = "Missions";

    const optionExpedition = L.DomUtil.create("option", "", filterTypeSelect);
    optionExpedition.value = "expedition";
    optionExpedition.textContent = "Expeditions";
    optionExpedition.selected = true;

    const optionCompilation = L.DomUtil.create("option", "", filterTypeSelect);
    optionCompilation.value = "compilation";
    optionCompilation.textContent = "Compilations";

    // Body
    const body = L.DomUtil.create("div", "filter-sidebar-body", sidebar);
    body.id = "filter-sidebar-body";
    body.style.padding = "0.5rem 0.5rem 0.75rem 0.5rem";
    body.style.flex = "1";
    body.style.minHeight = "200px";
    body.style.maxHeight = "calc(80vh - 60px)";

    // Function to copy and style form based on selected filter type
    const copyForm = function (filterType = "expedition") {
      const formContainer = document.getElementById("filter-form-container");
      if (!formContainer) {
        console.warn("Filter form container not found");
        return false;
      }

      const formId = `filter-form-${filterType}`;
      const form = formContainer.querySelector(`#${formId}`);
      if (!form) {
        console.warn(`Filter form ${formId} not found in container`);
        return false;
      }

      if (form.children.length === 0) {
        console.warn("Filter form is empty - may need to wait for Django rendering");
        return false;
      }

      body.innerHTML = "";

      const clonedForm = form.cloneNode(true);
      clonedForm.id = `filter-form-${filterType}`;
      clonedForm.className = "filter-form";
      clonedForm.setAttribute("data-filter-type", filterType);
      clonedForm.method = "get";
      clonedForm.action = "";
      clonedForm.style.display = "block";

      body.appendChild(clonedForm);

      const fieldCount = body.querySelectorAll(
        'input:not([type="hidden"]), select, textarea'
      ).length;
      console.log("Form copied to sidebar. Fields found:", fieldCount);

      if (fieldCount === 0) {
        console.warn("No form fields found after cloning - form may not be rendered yet");
        return false;
      }

      // Style inputs and selects
      const inputs = body.querySelectorAll(
        'input[type="text"], input[type="date"], input[type="search"], select'
      );
      inputs.forEach((el) => {
        el.style.width = "100%";
        el.style.maxWidth = "200px";
        el.style.fontSize = "0.8rem";
        el.style.padding = "0.3rem";
        el.style.marginBottom = "0.4rem";
        el.style.border = "1px solid #555";
        el.style.borderRadius = "4px";
        el.style.boxSizing = "border-box";
        el.style.backgroundColor = "#1e1e1e";
        el.style.color = "#e0e0e0";
      });

      body.querySelectorAll('.quality-checkboxes input[type="checkbox"]').forEach((cb) => {
        cb.style.width = "14px";
        cb.style.height = "14px";
        cb.style.marginRight = "0.4rem";
        cb.style.marginTop = "0.2rem";
        cb.style.cursor = "pointer";
      });

      body.querySelectorAll(".quality-checkboxes label").forEach((lbl) => {
        lbl.style.fontSize = "0.75rem";
        lbl.style.display = "flex";
        lbl.style.alignItems = "center";
        lbl.style.marginBottom = "0.3rem";
        lbl.style.cursor = "pointer";
        lbl.style.color = "#e0e0e0";
      });

      body.querySelectorAll(".quality-checkboxes ul").forEach((ul) => {
        ul.style.listStyle = "none";
        ul.style.paddingLeft = "0";
        ul.style.marginBottom = "0";
        ul.style.color = "#e0e0e0";
      });

      body.querySelectorAll(".quality-checkboxes li").forEach((li) => {
        li.style.marginBottom = "0.4rem";
        li.style.display = "flex";
        li.style.alignItems = "center";
        li.style.color = "#e0e0e0";
      });

      body.querySelectorAll(".form-group").forEach((fg) => {
        fg.style.marginBottom = "0.8rem";
        fg.style.marginLeft = "0";
        fg.style.marginRight = "0";
      });

      body.querySelectorAll(".form-label").forEach((lbl) => {
        lbl.style.fontSize = "0.8rem";
        lbl.style.fontWeight = "500";
        lbl.style.marginBottom = "0.3rem";
        lbl.style.display = "block";
        lbl.style.color = "#e0e0e0";
      });

      body.querySelectorAll("button.btn").forEach((btn) => {
        btn.style.fontSize = "0.75rem";
        btn.style.padding = "0.4rem 0.6rem"; // Reduced horizontal padding
        // Check if buttons are in a row - if so, make them share the row width
        const parentRow = btn.closest(".row");
        const parentColumn = btn.closest("[class*='col-']");
        if (parentRow && parentRow.querySelectorAll("button.btn").length > 1) {
          // Multiple buttons in same row - make them narrower to fit side by side
              // Ensure the column container doesn't force full width
              if (parentColumn) {
                parentColumn.style.flex = "1 1 auto";
                parentColumn.style.minWidth = "0";
                parentColumn.style.maxWidth = "none";
                parentColumn.style.width = "auto";
                parentColumn.style.flexBasis = "auto";
              }
          btn.style.width = "100%";
          btn.style.minWidth = "60px";
          btn.style.maxWidth = "none";
          btn.style.marginRight = "0.3rem";
          btn.style.marginTop = "0.2rem";
        } else {
          // Single button - full width
          btn.style.width = "100%";
          btn.style.maxWidth = "200px";
          btn.style.marginTop = "0.2rem";
        }
        btn.style.boxSizing = "border-box";
        if (btn.classList.contains("btn-primary")) {
          btn.style.backgroundColor = "#007bff";
          btn.style.color = "#ffffff";
        } else if (btn.classList.contains("btn-secondary")) {
          btn.style.backgroundColor = "#6c757d";
          btn.style.color = "#ffffff";
        }
      });

      const formInBody = body.querySelector("form");
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

      body.querySelectorAll(".row, .missionRow").forEach((row) => {
        row.style.marginLeft = "0";
        row.style.marginRight = "0";
        // Ensure rows display as flex to keep items on same row
        row.style.display = "flex";
        row.style.flexWrap = "wrap";
        row.style.flexDirection = "row";
        // Override Bootstrap's default row display
        row.style.setProperty("display", "flex", "important");
      });

      body.querySelectorAll(".col-md, [class*='col-']").forEach((col) => {
        col.style.paddingLeft = "0.25rem";
        col.style.paddingRight = "0.25rem";
        // For button rows, make columns flexible
        const parentRow = col.closest(".row");
        if (parentRow && parentRow.querySelectorAll("button.btn").length > 1) {
          col.style.flex = "1 1 auto";
          col.style.minWidth = "0";
          col.style.maxWidth = "none";
          col.style.width = "auto";
          col.style.flexBasis = "auto";
          // Override Bootstrap's default column width
          col.style.setProperty("width", "auto", "important");
          col.style.setProperty("flex-basis", "auto", "important");
        }
      });

      setTimeout(function () {
        if (sidebar) {
          const bodyHeight = body.scrollHeight;
          const header = sidebar.querySelector(".filter-sidebar-header");
          const headerHeight = header ? header.offsetHeight : 50;
          const totalHeight = bodyHeight + headerHeight + 10;
          const maxHeight = window.innerHeight * 0.8;
          sidebar.style.height = Math.min(totalHeight, maxHeight) + "px";
        }
      }, 100);

      return true;
    };

    // Current filter type (default to expedition)
    let currentFilterType = "expedition";

    // Function to switch filter type and reload form
    const switchFilterType = function (newFilterType) {
      currentFilterType = newFilterType;
      body.innerHTML = "";
      if (copyForm(currentFilterType)) {
        setTimeout(function () {
          const inputs = body.querySelectorAll(
            'input[type="text"], input[type="date"], input[type="search"], select'
          );
          inputs.forEach((el) => {
            el.style.width = "100%";
            el.style.maxWidth = "200px";
            el.style.fontSize = "0.8rem";
            el.style.padding = "0.3rem";
            el.style.marginBottom = "0.4rem";
            el.style.border = "1px solid #555";
            el.style.borderRadius = "4px";
            el.style.boxSizing = "border-box";
            el.style.backgroundColor = "#1e1e1e";
            el.style.color = "#e0e0e0";
          });

          body.querySelectorAll("button.btn").forEach((btn) => {
            btn.style.fontSize = "0.75rem";
            btn.style.padding = "0.4rem 0.6rem"; // Reduced horizontal padding
            // Check if buttons are in a row - if so, make them share the row width
            const parentRow = btn.closest(".row");
            const parentColumn = btn.closest("[class*='col-']");
            if (parentRow && parentRow.querySelectorAll("button.btn").length > 1) {
              // Multiple buttons in same row - make them narrower to fit side by side
              // Ensure the column container doesn't force full width
              if (parentColumn) {
                parentColumn.style.flex = "1 1 auto";
                parentColumn.style.minWidth = "0";
                parentColumn.style.maxWidth = "none";
              }
              btn.style.width = "100%";
              btn.style.minWidth = "60px";
              btn.style.maxWidth = "none";
              btn.style.marginRight = "0.3rem";
              btn.style.marginTop = "0.2rem";
            } else {
              // Single button - full width
              btn.style.width = "100%";
              btn.style.maxWidth = "200px";
              btn.style.marginTop = "0.2rem";
            }
            btn.style.boxSizing = "border-box";
            if (btn.classList.contains("btn-primary")) {
              btn.style.backgroundColor = "#007bff";
              btn.style.color = "#ffffff";
            } else if (btn.classList.contains("btn-secondary")) {
              btn.style.backgroundColor = "#6c757d";
              btn.style.color = "#ffffff";
            }
          });

          body.querySelectorAll(".form-label").forEach((lbl) => {
            lbl.style.fontSize = "0.8rem";
            lbl.style.fontWeight = "500";
            lbl.style.marginBottom = "0.3rem";
            lbl.style.display = "block";
            lbl.style.color = "#e0e0e0";
          });
        }, 100);
      }
    };

    // Add event listener to filter type dropdown
    L.DomEvent.on(filterTypeSelect, "change", function (e) {
      const newFilterType = e.target.value;
      switchFilterType(newFilterType);
    });

    // Try copying form with retries
    let retryCount = 0;
    const maxRetries = 10;
    const tryCopyForm = function () {
      if (copyForm(currentFilterType)) {
        console.log(`Form successfully copied to sidebar (${currentFilterType})`);
      } else {
        retryCount++;
        if (retryCount < maxRetries) {
          console.log(
            `Retrying form copy (attempt ${retryCount}/${maxRetries})...`
          );
          setTimeout(tryCopyForm, 300);
        } else {
          console.error("Failed to copy form after", maxRetries, "attempts");
        }
      }
    };

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        setTimeout(tryCopyForm, 200);
      });
    } else {
      setTimeout(tryCopyForm, 200);
    }

    let sidebarOpen = false;

    function showSidebar() {
      sidebar.style.left = "0px";
      container.style.left = "220px";

      const body = document.getElementById("filter-sidebar-body");
      if (body) {
        const formInBody = body.querySelector("form");
        if (formInBody) {
          formInBody.style.top = "0";
          formInBody.style.position = "relative";
          formInBody.style.width = "100%";
          formInBody.style.marginTop = "0";
          formInBody.style.marginLeft = "0";
          formInBody.style.marginRight = "0";
          formInBody.style.paddingTop = "0";
        }

        const bodyHeight = body.scrollHeight;
        const headerHeight =
          sidebar.querySelector(".filter-sidebar-header")?.offsetHeight || 50;
        const totalHeight = bodyHeight + headerHeight + 10;
        sidebar.style.height =
          Math.min(totalHeight, window.innerHeight * 0.8) + "px";
      }
    }

    function hideSidebar() {
      if (!sidebarOpen) {
        sidebar.style.left = "-220px";
        container.style.left = "20px";
      }
    }

    L.DomEvent.on(container, "click", function (e) {
      L.DomEvent.stopPropagation(e);

      icon.classList.remove("rotate-out", "rotate-in");

      sidebarOpen = !sidebarOpen;

      if (sidebarOpen) {
        icon.classList.add("rotate-out");
        setTimeout(function () {
          icon.className = "fas fa-times";
          icon.style.fontSize = "18px";
          icon.style.color = "#007bff";
          icon.classList.remove("rotate-out");
          icon.classList.add("rotate-in");
          showSidebar();
        }, 150);
      } else {
        icon.classList.add("rotate-out");
        setTimeout(function () {
          icon.className = "fas fa-filter";
          icon.style.fontSize = "18px";
          icon.style.color = "#007bff";
          icon.classList.remove("rotate-out");
          icon.classList.add("rotate-in");
          hideSidebar();
        }, 150);
      }
    });

    L.DomEvent.disableClickPropagation(sidebar);
    L.DomEvent.disableScrollPropagation(sidebar);

    return wrapper;
  },
});

// Add filter control to map at top-left
const filterControl = new FilterControl({ position: "topleft" });
filterControl.addTo(map);

// Remove Leaflet's default control styling
setTimeout(function () {
  const controlContainer = filterControl.getContainer();
  if (controlContainer && controlContainer.parentElement) {
    const leafletControlDiv = controlContainer.parentElement;
    if (leafletControlDiv.classList.contains("leaflet-control")) {
      leafletControlDiv.style.background = "transparent";
      leafletControlDiv.style.border = "none";
      leafletControlDiv.style.boxShadow = "none";
      leafletControlDiv.style.margin = "0";
      leafletControlDiv.style.padding = "0";
      leafletControlDiv.style.width = "auto";
      leafletControlDiv.style.height = "auto";
      leafletControlDiv.style.minHeight = "0";
      leafletControlDiv.style.minWidth = "0";
    }
  }

  const wrapper = controlContainer;
  if (wrapper) {
    wrapper.style.background = "transparent";
    wrapper.style.border = "none";
    wrapper.style.boxShadow = "none";
    wrapper.style.outline = "none";
    wrapper.style.margin = "0";
    wrapper.style.padding = "0";
    wrapper.style.width = "auto";
    wrapper.style.height = "auto";
    wrapper.style.minWidth = "0";
    wrapper.style.minHeight = "0";
  }

  let parent = controlContainer.parentElement;
  while (parent && parent !== document.body) {
    if (
      parent.classList.contains("leaflet-control") ||
      parent.classList.contains("leaflet-top") ||
      parent.classList.contains("leaflet-left")
    ) {
      parent.style.boxShadow = "none";
      parent.style.background = "transparent";
      parent.style.border = "none";
    }
    parent = parent.parentElement;
  }
}, 100);
