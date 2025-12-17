// /lib/leaflet.css
// /lib/leaflet-measure.css
// /lib/leaflet.js
// /lib/esri-leaflet.js
// /lib/esri-leaflet-vector.js
// /lib/Leaflet.GoogleMutant.js
// /lib/leaflet-google.js
// /lib/leaflet-measure.js
// /lib/easybutton.js
// include project.js

// L.mapbox.accessToken =
//   "pk.eyJ1Ijoic2FsYW15IiwiYSI6ImNsNTl6ODAyeTF5aTYzZHBvc3ZjeWJqeHMifQ.8qQduUOn78kIp6gHtoC-Ag";

const apiKey =
  "AAPK4f2bc64881714cb2b03b1b5798dd2b740wn2YfXp7EZuoC_GggsJw92b06Ou-ZhL1i0CU-haX0JwKr9Ve9ned4wNTOYlGu1x";
const basemapEnum = "ArcGIS:Oceans";
const options = {
  minZoom: 1,
  maxNativeZoom: 13,
  maxZoom: 16,
  exclusiveGroups: ["Base Maps   &#127758; "],
  groupCheckboxes: true,
};

const map = L.map("map", {
  ...options,
  zoomSnap: 0.5,  // Allow fractional zoom levels (0.5 increments: 1, 1.5, 2, 2.5, 3, etc.)
  zoomDelta: 0.5, // Zoom in/out by 0.5 increments
});
const media_url = JSON.parse(document.getElementById("MEDIA-URL").textContent);

// Change the position of the Zoom Control to bottomright.
map.zoomControl.setPosition("bottomright");

//Determine the BROWSER used - Important for ToolTip Date.parse
var browserName = fnBrowserDetect();

//////////////////////
// Base layers
//ESRI_Oceans_Vector_Layer
// const esriOceans = L.esri.Vector.vectorBasemapLayer(basemapEnum, {
//   id: "arcgisOceans",
//   name: "ArcGIS:Oceans",
//   apikey: apiKey,
// });

const esriOceansMap = L.esri.basemapLayer("Oceans", options);
const esriOceansLabel = L.esri.basemapLayer("OceansLabels", options);
const esriOceans = L.featureGroup([esriOceansMap, esriOceansLabel]);

// Google_Hybrid_Layer
const googleHybrid = L.gridLayer.googleMutant({
  type: "hybrid",
  layers: "hybrid",
  id: "hybrid",
  name: "hybrid",
});
googleHybrid.maxZoom = 16;

const gmrt = L.tileLayer.wms(
  "https://www.gmrt.org/services/mapserver/wms_merc?",
  {
    layers: "GMRT",
    id: "GMRT",
    name: "GMRT",
  }
);

const gmrtMask = L.tileLayer.wms(
  "https://www.gmrt.org/services/mapserver/wms_merc_mask?",
  {
    layers: "GMRTMask",
    id: "GMRTMask",
    name: "GMRTMask",
  }
);

//////////////////////////////////////////////////////////////////
// Construct a const map BASE LAYER OBJECT for Selection
const baseLayers = {};

//Construct Grouped Overlays to Toggle
var groupedOverlays = {
  "Base Maps   &#127758; ": {
    " GMRT (Hi-Res) ": gmrt.addTo(map),
    " Masked GMRT (Hi-Res) ": gmrtMask,
    " ESRI/ArcGIS Oceans ": esriOceans,
    " Google Hybrid Layer ": googleHybrid,
  },
};

// Display the Default or Chosen Base Map
map.fitWorld();

// Create Filter Control as Leaflet control (top-left of map)
const FilterControl = L.Control.extend({
  onAdd: function (map) {
    // Create wrapper that contains sidebar and button
    // This will be inside Leaflet's control container, so don't style it as fixed
    const wrapper = L.DomUtil.create("div", "filter-wrapper");
    wrapper.style.position = "relative";
    wrapper.style.width = "40px"; // Button width when closed
    wrapper.style.height = "50px";
    wrapper.style.transition = "width 0.3s ease";
    wrapper.style.zIndex = "1000";
    wrapper.style.backgroundColor = "transparent"; // Make wrapper transparent
    wrapper.style.border = "none"; // Remove any default borders
    wrapper.style.boxShadow = "none"; // Remove any default shadows
    wrapper.style.margin = "0"; // Remove any default margins
    wrapper.style.padding = "0"; // Remove any default padding

    // Sidebar panel (slides out from left, button moves to its right edge)
    const sidebar = L.DomUtil.create("div", "filter-sidebar", wrapper);
    sidebar.id = "filter-sidebar";
    sidebar.style.position = "absolute";
    sidebar.style.left = "-220px"; // Hidden by default (slide out from left)
    sidebar.style.top = "0";
    sidebar.style.width = "220px";
    sidebar.style.maxHeight = "250vh";
    sidebar.style.height = "auto"; // Auto-adjust to content
    sidebar.style.minHeight = "50px"; // Minimum height for button
    sidebar.style.backgroundColor = "#2d2d2d"; // Dark gray background
    sidebar.style.boxShadow = "2px 0 12px rgba(0,0,0,0.5)"; // Darker shadow
    sidebar.style.borderRadius = "0 4px 4px 0";
    sidebar.style.color = "#e0e0e0"; // Light text color
    sidebar.style.transition = "left 0.3s ease, height 0.3s ease"; // Also transition height for smooth resize
    sidebar.style.overflow = "hidden";
    sidebar.style.display = "flex";
    sidebar.style.flexDirection = "column";
    sidebar.style.zIndex = "999";
    sidebar.style.pointerEvents = "auto";
    sidebar.style.minHeight = "50px"; // At least button height

    // Filter button - initially standalone, moves to right edge of sidebar when sidebar opens
    // Don't use leaflet-bar/leaflet-control classes to avoid default Leaflet styling that creates borders
    const container = L.DomUtil.create("div", "filter-control", wrapper);
    container.id = "filter-button";
    container.title = "Filter Map View"; // Tooltip on hover
    container.style.width = "40px";
    container.style.height = "40px";
    container.style.backgroundColor = "hsla(0, 0%, 100%, 0.75)"; // Semi-transparent white like other controls
    container.style.borderRadius = "4px";
    container.style.cursor = "pointer";
    container.style.display = "flex";
    container.style.flexDirection = "column";
    container.style.alignItems = "center";
    container.style.justifyContent = "center";
    container.style.boxShadow = "0 1px 5px rgba(0,0,0,0.4)";
    container.style.position = "absolute";
    container.style.top = "5px";
    container.style.left = "20px"; // 20px from left edge of map when closed
    container.style.zIndex = "1001"; // Above sidebar
    container.style.transition = "left 0.3s ease, background-color 0.2s ease";
    container.style.border = "none"; // Ensure no border
    container.style.outline = "none"; // Ensure no outline
    container.style.margin = "0"; // Ensure no margin
    container.style.padding = "0"; // Ensure no padding

    // Filter icon (changes to X when open)
    const icon = L.DomUtil.create("i", "fas fa-filter", container);
    icon.id = "filter-icon";
    icon.style.fontSize = "18px";
    icon.style.color = "#007bff"; // Light blue color

    // Badge (shown on button)
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
    badge.style.display = "flex";
    badge.style.alignItems = "center";
    badge.style.justifyContent = "center";
    badge.textContent = "";
    badge.style.display = "none";

    // Header (will show "Filters" title)
    const header = L.DomUtil.create("div", "filter-sidebar-header", sidebar);
    header.style.padding = "0.5rem";
    header.style.paddingRight = "50px"; // Make room for button on right
    header.style.borderBottom = "1px solid #555"; // Darker border
    header.style.background = "#1e1e1e"; // Darker header background
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
    title.style.color = "#ffffff"; // White text for title
    
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
    optionMission.selected = true;
    
    const optionExpedition = L.DomUtil.create("option", "", filterTypeSelect);
    optionExpedition.value = "expedition";
    optionExpedition.textContent = "Expeditions";
    
    const optionCompilation = L.DomUtil.create("option", "", filterTypeSelect);
    optionCompilation.value = "compilation";
    optionCompilation.textContent = "Compilations";

    // Body - copy form from hidden container
    const body = L.DomUtil.create("div", "filter-sidebar-body", sidebar);
    body.id = "filter-sidebar-body";
    body.style.padding = "0.5rem 0.5rem 0.75rem 0.5rem"; // Top, Right, Bottom, Left - reduced top padding
    body.style.flex = "1";
    body.style.minHeight = "200px";
    body.style.maxHeight = "calc(80vh - 60px)"; // Account for header height

    // Function to copy and style form based on selected filter type
    const copyForm = function (filterType = "mission") {
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

      // Check if form has content
      if (form.children.length === 0) {
        console.warn(
          "Filter form is empty - may need to wait for Django rendering"
        );
        return false;
      }

      // Clear any existing form in body
      body.innerHTML = "";

      // Clone the form (deep clone)
      const clonedForm = form.cloneNode(true);
      clonedForm.id = `filter-form-${filterType}`; // Keep filter type in ID
      clonedForm.className = "filter-form";
      clonedForm.setAttribute("data-filter-type", filterType);
      clonedForm.method = "get";
      clonedForm.action = window.location.pathname; // Submit to current page

      // Remove onclick attributes from Clear buttons to prevent navigation
      // We'll handle the Clear button behavior in JavaScript instead
      const currentPath = window.location.pathname;
      const isMainMapPage = currentPath === '/' || currentPath === '/missions' || currentPath.startsWith('/missions/');
      if (isMainMapPage) {
        clonedForm.querySelectorAll("button").forEach((btn) => {
          // Check if this is a Clear button by ID, type, or onclick attribute
          const isClearBtn = btn.type === "reset" || 
                            (btn.id && (btn.id.includes("Cancel") || btn.id.includes("clear"))) ||
                            (btn.getAttribute("onclick") && btn.getAttribute("onclick").includes("window.location"));
          if (isClearBtn) {
            // Remove onclick attribute completely
            btn.removeAttribute("onclick");
            // Set onclick to null to clear any existing handler
            btn.onclick = null;
            // Also remove any data attributes that might trigger navigation
            btn.removeAttribute("data-onclick");
          }
        });
      }

      // Add hidden input to identify filter type
      const filterTypeInput = document.createElement("input");
      filterTypeInput.type = "hidden";
      filterTypeInput.name = "filter_type";
      filterTypeInput.value = filterType;
      clonedForm.appendChild(filterTypeInput);

      // Show the form (it was in a hidden container)
      clonedForm.style.display = "block";

      body.appendChild(clonedForm);
      
      // Add global click interceptor for Clear buttons on main map page (before onclick handlers execute)
      const currentPathCheck = window.location.pathname;
      const isMainMapPageCheck = currentPathCheck === '/' || currentPathCheck === '/missions' || currentPathCheck.startsWith('/missions/');
      if (isMainMapPageCheck) {
        // Use capture phase to intercept clicks before onclick handlers
        body.addEventListener('click', function(e) {
          const target = e.target;
          // Check if this is a Clear button
          const isClearBtn = target.type === "reset" || 
                            (target.id && (target.id.includes("Cancel") || target.id.includes("clear"))) ||
                            (target.getAttribute("onclick") && target.getAttribute("onclick") && target.getAttribute("onclick").includes("window.location"));
          if (isClearBtn && target.closest('#filter-sidebar-body')) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            // Clear all filter parameters and reload current page
            const currentUrl = new URL(window.location.href);
            const filterKeys = ['name', 'region_name', 'quality_categories', 'patch_test', 'repeat_survey', 'mgds_compilation', 'expedition__name', 'filter_type', 'q', 'xmin', 'xmax', 'ymin', 'ymax', 'tmin', 'tmax'];
            filterKeys.forEach(key => currentUrl.searchParams.delete(key));
            window.location.href = currentUrl.toString();
            return false;
          }
        }, true); // Capture phase - intercepts before onclick handlers
      }
      
      // Add form submission handler to actually submit the form
      clonedForm.addEventListener("submit", function(e) {
        e.preventDefault(); // Prevent default submission
        // Get form data
        const formData = new FormData(clonedForm);
        const params = new URLSearchParams(formData);
        // Preserve current URL path and add filter parameters
        const currentUrl = new URL(window.location.href);
        // Clear existing filter params to avoid conflicts
        const filterKeys = ['name', 'region_name', 'quality_categories', 'patch_test', 'repeat_survey', 'mgds_compilation', 'expedition__name', 'filter_type'];
        filterKeys.forEach(key => currentUrl.searchParams.delete(key));
        // Add new filter params from form
        for (const [key, value] of params.entries()) {
          if (value) { // Only add non-empty values
            currentUrl.searchParams.set(key, value);
          }
        }
        // Reload page with filter parameters
        window.location.href = currentUrl.toString();
      });

      const fieldCount = body.querySelectorAll(
        'input:not([type="hidden"]), select, textarea'
      ).length;
      console.log("Form copied to sidebar. Fields found:", fieldCount);

      if (fieldCount === 0) {
        console.warn(
          "No form fields found after cloning - form may not be rendered yet"
        );
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
        el.style.border = "1px solid #555"; // Darker border
        el.style.borderRadius = "4px";
        el.style.boxSizing = "border-box";
        el.style.backgroundColor = "#1e1e1e"; // Dark input background
        el.style.color = "#e0e0e0"; // Light text color
      });

      // Style checkboxes for quality categories (CheckboxSelectMultiple creates <ul><li> structure)
      body
        .querySelectorAll('.quality-checkboxes input[type="checkbox"]')
        .forEach((cb) => {
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
        lbl.style.color = "#e0e0e0"; // Light text color for labels
      });

      // Style <ul> and <li> for checkbox lists (Django CheckboxSelectMultiple)
      body.querySelectorAll(".quality-checkboxes ul").forEach((ul) => {
        ul.style.listStyle = "none";
        ul.style.paddingLeft = "0";
        ul.style.marginBottom = "0";
        ul.style.color = "#e0e0e0"; // Light text color
      });

      body.querySelectorAll(".quality-checkboxes li").forEach((li) => {
        li.style.marginBottom = "0.4rem";
        li.style.display = "flex";
        li.style.alignItems = "center";
        li.style.color = "#e0e0e0"; // Light text color
      });

      // Style form groups
      body.querySelectorAll(".form-group").forEach((fg) => {
        fg.style.marginBottom = "0.8rem";
        fg.style.marginLeft = "0"; // Remove left margin
        fg.style.marginRight = "0"; // Remove right margin
      });

      // Style labels
      body.querySelectorAll(".form-label").forEach((lbl) => {
        lbl.style.fontSize = "0.8rem";
        lbl.style.fontWeight = "500";
        lbl.style.marginBottom = "0.3rem";
        lbl.style.display = "block";
        lbl.style.color = "#e0e0e0"; // Light text color for labels
      });

      // Style buttons
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
        // Keep button colors but ensure text is visible
        if (btn.classList.contains("btn-primary")) {
          btn.style.backgroundColor = "#007bff";
          btn.style.color = "#ffffff";
        } else if (btn.classList.contains("btn-secondary")) {
          btn.style.backgroundColor = "#6c757d";
          btn.style.color = "#ffffff";
        }
        
        // Override Clear button onclick to stay on current page (only on main map/home page)
        // On expedition/compilation pages, let the default behavior navigate to those pages
        const currentPath = window.location.pathname;
        const isMainMapPage = currentPath === '/' || currentPath === '/missions' || currentPath.startsWith('/missions/');
        // Check if this is a Clear button by type, ID, or onclick attribute
        const isClearButton = btn.type === "reset" || 
                             (btn.id && (btn.id.includes("Cancel") || btn.id.includes("clear"))) ||
                             (btn.getAttribute("onclick") && btn.getAttribute("onclick") && btn.getAttribute("onclick").includes("window.location"));
        if (isMainMapPage && isClearButton) {
          // Remove any existing onclick attribute
          btn.removeAttribute("onclick");
          // Clear onclick property
          btn.onclick = null;
          
          // Create a completely new click handler that prevents default and stops propagation
          const clearHandler = function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            // Clear all filter parameters and reload current page
            const currentUrl = new URL(window.location.href);
            // Remove all filter-related query parameters
            const filterKeys = ['name', 'region_name', 'quality_categories', 'patch_test', 'repeat_survey', 'mgds_compilation', 'expedition__name', 'filter_type', 'q', 'xmin', 'xmax', 'ymin', 'ymax', 'tmin', 'tmax'];
            filterKeys.forEach(key => currentUrl.searchParams.delete(key));
            // Reload page without filter parameters (stay on home/map page)
            window.location.href = currentUrl.toString();
            return false;
          };
          
          // Remove all existing event listeners by cloning and replacing
          const newBtn = btn.cloneNode(true);
          // Remove onclick from the cloned button too
          newBtn.removeAttribute("onclick");
          newBtn.onclick = null;
          
          if (btn.parentNode) {
            btn.parentNode.replaceChild(newBtn, btn);
          }
          
          // Set new onclick handler on the new button
          newBtn.onclick = clearHandler;
          
          // Add event listener in capture phase to intercept early (before any other handlers)
          newBtn.addEventListener('click', clearHandler, true);
          
          // Also add in bubble phase as backup
          newBtn.addEventListener('click', clearHandler, false);
        }
      });

      // Override filters.css styles directly on the form via inline styles
      const formInBody = body.querySelector("form");
      if (formInBody) {
        formInBody.style.top = "0"; // Remove top offset
        formInBody.style.position = "relative"; // Change from absolute to relative
        formInBody.style.width = "100%"; // Use full width
        formInBody.style.marginTop = "0"; // Remove top margin
        formInBody.style.marginLeft = "0";
        formInBody.style.marginRight = "0";
        formInBody.style.paddingTop = "0"; // Remove top padding
        formInBody.style.paddingLeft = "0"; // Remove left padding
        formInBody.style.paddingRight = "0"; // Remove right padding
      }
      
      // Remove left margin from row elements (crispy forms creates rows)
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
      
      // Remove left padding from columns and ensure they work with flex
      body.querySelectorAll(".col-md, [class*='col-']").forEach((col) => {
        col.style.paddingLeft = "0.25rem"; // Minimal left padding
        col.style.paddingRight = "0.25rem"; // Minimal right padding
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

      // Auto-adjust sidebar height after form is copied
      setTimeout(function () {
        if (sidebar) {
          const bodyHeight = body.scrollHeight;
          const header = sidebar.querySelector(".filter-sidebar-header");
          const headerHeight = header ? header.offsetHeight : 50;
          const totalHeight = bodyHeight + headerHeight + 10; // Add small padding
          const maxHeight = window.innerHeight * 0.8;
          sidebar.style.height = Math.min(totalHeight, maxHeight) + "px";
        }
      }, 100);

      return true;
    };

    // Current filter type (default to mission)
    let currentFilterType = "mission";
    
    // Function to switch filter type and reload form
    const switchFilterType = function (newFilterType) {
      currentFilterType = newFilterType;
      // Clear existing form
      body.innerHTML = "";
      // Copy new form with styling
      if (copyForm(currentFilterType)) {
        // Re-apply all styling after form is copied
        setTimeout(function() {
          // Re-style inputs, labels, buttons, etc. (all the styling code from copyForm)
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
            
            // Override Clear button onclick to stay on current page (only on main map/home page)
            // On expedition/compilation pages, let the default behavior navigate to those pages
            const currentPath = window.location.pathname;
            const isMainMapPage = currentPath === '/' || currentPath === '/missions' || currentPath.startsWith('/missions/');
            // Check if this is a Clear button by type, ID, or onclick attribute
            const isClearButton = btn.type === "reset" || 
                                 (btn.id && (btn.id.includes("Cancel") || btn.id.includes("clear"))) ||
                                 (btn.getAttribute("onclick") && btn.getAttribute("onclick") && btn.getAttribute("onclick").includes("window.location"));
            if (isMainMapPage && isClearButton) {
              // Remove any existing onclick attribute
              btn.removeAttribute("onclick");
              // Clear onclick property
              btn.onclick = null;
              
              // Create a completely new click handler that prevents default and stops propagation
              const clearHandler = function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                // Clear all filter parameters and reload current page
                const currentUrl = new URL(window.location.href);
                // Remove all filter-related query parameters
                const filterKeys = ['name', 'region_name', 'quality_categories', 'patch_test', 'repeat_survey', 'mgds_compilation', 'expedition__name', 'filter_type', 'q', 'xmin', 'xmax', 'ymin', 'ymax', 'tmin', 'tmax'];
                filterKeys.forEach(key => currentUrl.searchParams.delete(key));
                // Reload page without filter parameters (stay on home/map page)
                window.location.href = currentUrl.toString();
                return false;
              };
              
              // Remove all existing event listeners by cloning and replacing
              const newBtn = btn.cloneNode(true);
              if (btn.parentNode) {
                btn.parentNode.replaceChild(newBtn, btn);
              }
              
              // Set new onclick handler on the new button
              newBtn.onclick = clearHandler;
              
              // Add event listener in capture phase to intercept early (before any other handlers)
              newBtn.addEventListener('click', clearHandler, true);
              
              // Also add in bubble phase as backup
              newBtn.addEventListener('click', clearHandler, false);
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

    // Start trying to copy
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        setTimeout(tryCopyForm, 200);
      });
    } else {
      // DOM already loaded, wait a bit for template rendering
      setTimeout(tryCopyForm, 200);
    }

    let sidebarOpen = false;

    // Helper function to show sidebar (slide out from left, button moves to right edge)
    function showSidebar() {
      sidebar.style.left = "0px"; // Slide sidebar out - left edge aligns with map edge (no gap)
      // Button is 20px from map edge when closed, sidebar is 220px wide starting at 0px
      // So button should be at 220px (right edge of sidebar)
      container.style.left = "220px"; // Move button to right edge of sidebar
      // Button stays on right edge - positioned relative to wrapper

      // Auto-adjust sidebar height to fit content
      const body = document.getElementById("filter-sidebar-body");
      if (body) {
        // Ensure form has correct positioning when sidebar opens
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
        const totalHeight = bodyHeight + headerHeight + 10; // Add small padding
        sidebar.style.height =
          Math.min(totalHeight, window.innerHeight * 0.8) + "px";
      }
    }

    // Helper function to hide sidebar (slide back left, button returns to left)
    function hideSidebar() {
      if (!sidebarOpen) {
        sidebar.style.left = "-220px"; // Hide sidebar
        container.style.left = "20px"; // Return button to 20px from left edge
        // Icon change is handled in click handler with animation
      }
    }

    // Click handler - toggle persistent open state
    L.DomEvent.on(container, "click", function (e) {
      L.DomEvent.stopPropagation(e);

      // Remove any existing animation classes
      icon.classList.remove("rotate-out", "rotate-in");

      sidebarOpen = !sidebarOpen;

      if (sidebarOpen) {
        // Animate filter icon out, then change to X
        icon.classList.add("rotate-out");
        setTimeout(function () {
          icon.className = "fas fa-times"; // Change to X (close icon)
          icon.style.fontSize = "18px";
          icon.style.color = "#007bff";
          icon.classList.remove("rotate-out");
          icon.classList.add("rotate-in");
          showSidebar();
        }, 150); // Halfway through animation
      } else {
        // Animate X icon out, then change to filter
        icon.classList.add("rotate-out");
        setTimeout(function () {
          icon.className = "fas fa-filter"; // Change back to filter icon
          icon.style.fontSize = "18px";
          icon.style.color = "#007bff";
          icon.classList.remove("rotate-out");
          icon.classList.add("rotate-in");
          hideSidebar();
        }, 150); // Halfway through animation
      }
    });

    // Hover functionality removed - sidebar only opens/closes on click

    // Prevent map events on sidebar
    L.DomEvent.disableClickPropagation(sidebar);
    L.DomEvent.disableScrollPropagation(sidebar);

    // Return wrapper so Leaflet positions it correctly
    return wrapper;
  },
});

// Add filter control to map at top-left
const filterControl = new FilterControl({ position: "topleft" });
filterControl.addTo(map);

// Remove Leaflet's default control styling from our filter control's container
// Leaflet wraps our control in a div with .leaflet-control class, which adds borders/background
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

  // Also ensure the wrapper itself has no background/shadow
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

  // Also target any parent containers that might have shadows
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

const missions = JSON.parse(
  document.getElementById("missions-data").textContent
);

// Add SMDB Missions to Base Map
let feature = L.geoJSON(missions, {
  style: function () { },
  hover: function () { },
})
  // Popup Thumbnail Images of Missions
  .bindPopup(
    function (layer) {
      if (layer.feature.properties.thumbnail_image) {
        image_url = layer.feature.properties.thumbnail_image;
      } else {
        image_url = "static/images/No_ZTopoSlopeNav_image.jpg";
      }
      return (
        "<a target='_blank' href='/missions/" +
        layer.feature.properties.slug +
        "'>" +
        "<img src='" +
        image_url +
        "' />" +
        "</a>"
      );
    },
    {
      maxWidth: "600px",
    }
  )
  // Popup Mission Info Tooltips
  .bindTooltip(function (layer) {
    var tooltipInfo = layer.feature.properties.slug;
    tooltipInfo = tooltipInfo.replace(/.*-/, "");
    tooltipInfo = tooltipInfo.replace(/(\d)([^\d\s%])/g, "$1 $2");
    let dateOfMission = tooltipInfo.substring(0, 8);
    if ((browserName = "firefox") || (browserName = "safari")) {
      dateOfMission = dateOfMission.replace(
        /(\d{4})(\d{2})(\d{2})/g,
        "$1-$2-$3T00:00:00"
      );
    } else {
      dateOfMission = dateOfMission.replace(
        /(\d{4})(\d{2})(\d{2})/g,
        "$2-$3-$1"
      );
    }

    dateOfMission = new Date(dateOfMission).toLocaleDateString("en-us", {
      weekday: "long",
      year: "numeric",
      month: "short",
      day: "numeric",
    });

    let missionInfo = tooltipInfo.substring(tooltipInfo.indexOf(" ") + 1);
    missionInfo = missionInfo.replace(/^\m/, "Mission ");
    tooltipInfo =
      layer.feature.properties.slug +
      "<br>Date: " +
      dateOfMission +
      "<br>Route: " +
      layer.feature.properties.route_file;
    return tooltipInfo;
  })
  .addTo(map);

// Fit map to mission bounds - calculate optimal zoom based on viewport size and mission bounds
// Priority: Show ALL mission data, but optimize zoom to minimize empty space at poles
map.whenReady(function() {
  // Invalidate size to ensure Leaflet recalculates container dimensions
  map.invalidateSize();
  
  // Small delay to ensure container has final size after invalidateSize and feature is loaded
  setTimeout(function() {
    try {
      var bounds = feature.getBounds();
      if (bounds && bounds.isValid && bounds.isValid()) {
        // Get viewport/container dimensions
        var mapContainer = document.getElementById("map");
        var viewportWidth = mapContainer.offsetWidth || window.innerWidth;
        var viewportHeight = mapContainer.offsetHeight || window.innerHeight;
        
        // Get mission bounds coordinates
        var sw = bounds.getSouthWest(); // Southwest corner
        var ne = bounds.getNorthEast(); // Northeast corner
        var missionLatSpan = ne.lat - sw.lat; // Latitude span
        var missionLngSpan = ne.lng - sw.lng; // Longitude span
        
        // Calculate aspect ratios
        var viewportAspect = viewportWidth / viewportHeight;
        var missionAspect = missionLngSpan / missionLatSpan;
        
        // Calculate padding as percentage of viewport (adaptive to screen size)
        // Use smaller padding for tighter fit and more zoom while still showing all missions
        var paddingPercent = Math.min(0.05, Math.max(0.02, 50 / viewportWidth)); // 2-5% of viewport (reduced from 5-10%)
        var paddingX = Math.round(viewportWidth * paddingPercent);
        var paddingY = Math.round(viewportHeight * paddingPercent);
        
        // If viewport is wider than mission bounds, reduce vertical padding to avoid showing empty pole areas
        // Only add vertical padding if needed to show all missions, not to match viewport aspect ratio
        if (viewportAspect > missionAspect) {
          // Viewport is wider - use minimal vertical padding to avoid showing empty north/south pole areas
          paddingY = Math.min(paddingY, Math.round(viewportHeight * 0.01)); // Max 1% vertical padding when viewport is wide
        }
        
        // Calculate optimal zoom that shows all missions but doesn't zoom out excessively
        // First, fit bounds to get the zoom level that shows all missions
        map.fitBounds(bounds, { padding: [paddingY, paddingX] });
        
        // Adjust center to better position mission data in viewport
        // If viewport is wider than mission bounds, shift center southward to show more data areas
        if (viewportAspect > missionAspect) {
          var currentCenter = map.getCenter();
          var missionCenterLat = (sw.lat + ne.lat) / 2;
          // Shift center slightly south to better position mission data (reduce empty north pole space)
          var adjustedLat = missionCenterLat - (ne.lat - missionCenterLat) * 0.1; // Shift 10% of upper half southward
          map.setView([adjustedLat, currentCenter.lng], map.getZoom(), { animate: false });
        }
        
        // Get the zoom level that fitBounds calculated
        var calculatedZoom = map.getZoom();
        
        // Allow fractional zoom for finer control when zooming in
        // No constraint on zooming out - let fitBounds determine optimal zoom to show all missions
        // Fractional zoom (0.5 increments) allows more precise zoom levels when user zooms in
      }
    } catch (err) {
      console.log("Error fitting bounds: " + err.message);
    }
  }, 150);
});

// Also try after a delay to ensure feature is fully loaded and map is ready
setTimeout(function() {
  try {
    map.invalidateSize();
    var bounds = feature.getBounds();
    if (bounds && bounds.isValid && bounds.isValid()) {
      // Get viewport dimensions
      var mapContainer = document.getElementById("map");
      var viewportWidth = mapContainer.offsetWidth || window.innerWidth;
      var viewportHeight = mapContainer.offsetHeight || window.innerHeight;
      
      // Calculate adaptive padding (reduced for tighter fit and more zoom)
      var paddingPercent = Math.min(0.05, Math.max(0.02, 50 / viewportWidth)); // 2-5% of viewport
      var paddingX = Math.round(viewportWidth * paddingPercent);
      var paddingY = Math.round(viewportHeight * paddingPercent);
      
      // Get mission bounds to check aspect ratio
      var sw = bounds.getSouthWest();
      var ne = bounds.getNorthEast();
      var missionLatSpan = ne.lat - sw.lat;
      var missionLngSpan = ne.lng - sw.lng;
      var viewportAspect = viewportWidth / viewportHeight;
      var missionAspect = missionLngSpan / missionLatSpan;
      
      // If viewport is wider than mission bounds, reduce vertical padding to avoid showing empty pole areas
      if (viewportAspect > missionAspect) {
        // Viewport is wider - use minimal vertical padding to avoid showing empty north/south pole areas
        paddingY = Math.min(paddingY, Math.round(viewportHeight * 0.01)); // Max 1% vertical padding when viewport is wide
      }
      
      map.fitBounds(bounds, { padding: [paddingY, paddingX] });
      
      // Adjust center to better position mission data in viewport
      // If viewport is wider than mission bounds, shift center southward to show more data areas
      if (viewportAspect > missionAspect) {
        var currentCenter = map.getCenter();
        var missionCenterLat = (sw.lat + ne.lat) / 2;
        // Shift center slightly south to better position mission data (reduce empty north pole space)
        var adjustedLat = missionCenterLat - (ne.lat - missionCenterLat) * 0.1; // Shift 10% of upper half southward
        map.setView([adjustedLat, currentCenter.lng], map.getZoom(), { animate: false });
      }
      
      // Fractional zoom enabled - allows 0.5 increments for finer zoom control
      // No zoom constraint - fitBounds determines optimal zoom to show all missions
    }
  } catch (err) {
    console.log("Error in fallback fitBounds: " + err.message);
  }
}, 100);

/* --------------------------------------------------  */
// Set up SIDEBAR
/* --------------------------------------------------  */
/* let sidebar = L.control.sidebar({
  position: "topleft",
  container: null,
  closeButton: true,
  autopan: false,
}); */
//map.addControl(sidebar);
//sidebar.addTo(map);

// Get Map Bounds/Coordinates
var bounds = L.control({});

bounds.onAdd = function (map) {
  var div = L.DomUtil.create("div");
  var bboxString = getMapBounds();
  div.innerHTML =
    '<div id="bounds">' +
    '<div id="div-bounds">' +
    '<input title="Use map bounds in Update" type="checkbox" onclick="getBoundsStatus()" style="vertical-align: middle" id="use_bounds">' +
    "</div>" +
    "&nbsp" +
    "&nbsp" +
    '<div id="map-bounds">' +
    bboxString +
    "</div>" +
    "</div>";
  return div;
};
bounds.addTo(map);

// Get Map Bounds Status (Checked or Unchecked)
function getBoundsStatus() {
  var boundsStatus;
  if (document.getElementById("use_bounds").checked) {
    // console.log("Bounds checkbox CHECKED!");
    boundsStatus = true;
  } else {
    // console.log("Bounds checkbox UNCHECKED!");
    boundsStatus = false;
  }
  return boundsStatus;
}

// Get Map Bounds Status (Checked or Unchecked)
function getSliderStatus() {
  var sliderStatus;
  if (document.getElementById("use_time").checked) {
    // console.log("SliderControl Time checkbox CHECKED!");
    sliderStatus = true;
  } else {
    // console.log("SliderControl Time checkbox UNCHECKED!");
    sliderStatus = false;
  }
  return sliderStatus;
}

// Determine Mouse Coordinate position
var mousePosition = L.control({ position: "topright" });
mousePosition.onAdd = function (map) {
  var div = L.DomUtil.create("div", "bounds-container row");
  var mousePos = L.DomUtil.create("div");
  map.addEventListener("mousemove", (e) => {
    mousePos.innerHTML = `&nbsp&nbsp${e.latlng.lat.toFixed(
      4
    )},  ${e.latlng.lng.toFixed(4)}&nbsp&nbsp`;
  });
  return mousePos;
};
mousePosition.addTo(map);

/////////////////////////////////////////////////////////////////////////
// BaseMap Toggle Control Layers
var controlLayers = L.control
  .groupedLayers(baseLayers, groupedOverlays, options)
  .addTo(map);
/////////////////////////////////////////////////////////////////////////

// Add Measure Control on Map
var measure = L.control
  .measure({
    primaryLengthUnit: "meters",
    secondaryLengthUnit: "feet",
    primaryAreaUnit: "sqmeters",
    secondaryAreaUnit: "sqmiles",
    activeColor: "#ABE67E",
    completedColor: "#C8F2BE",
    captureZIndex: 5000,
  })
  .addTo(map);

// Add Draw Control for Rectangle Selection
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
  position: "topright",
  draw: {
    polygon: false,
    polyline: false,
    circle: false,
    circlemarker: false,
    marker: false,
    rectangle: {
      shapeOptions: {
        color: "#3388ff",
        fillColor: "#3388ff",
        fillOpacity: 0.2,
        weight: 2,
      },
    },
  },
  edit: {
    featureGroup: drawnItems,
    remove: true,
  },
});
map.addControl(drawControl);

// Handle rectangle drawing completion
map.on(L.Draw.Event.CREATED, function (e) {
  var type = e.layerType;
  var layer = e.layer;

  if (type === "rectangle") {
    // Remove any existing rectangles
    drawnItems.clearLayers();
    
    // Add the new rectangle to the map
    drawnItems.addLayer(layer);
    
    // Get rectangle bounds
    var bounds = layer.getBounds();
    var bbox = {
      xmin: bounds.getWest(),
      ymin: bounds.getSouth(),
      xmax: bounds.getEast(),
      ymax: bounds.getNorth(),
    };
    
    // Store bounds globally for export
    window.drawnRectangleBounds = bbox;
    
    // Get current filter parameters from URL
    var urlParams = new URLSearchParams(window.location.search);
    var filterParams = {};
    var filterKeys = ['name', 'region_name', 'quality_categories', 'patch_test', 'repeat_survey', 'mgds_compilation', 'expedition__name', 'filter_type', 'q', 'tmin', 'tmax'];
    filterKeys.forEach(function(key) {
      if (urlParams.has(key)) {
        filterParams[key] = urlParams.get(key);
      }
    });
    
    // Add bbox to filter params
    filterParams.xmin = bbox.xmin;
    filterParams.xmax = bbox.xmax;
    filterParams.ymin = bbox.ymin;
    filterParams.ymax = bbox.ymax;
    
    // Show loading indicator
    showResultsPanel(true);
    updateResultsPanel("Loading missions...", []);
    
    // Fetch filtered missions
    fetchFilteredMissions(filterParams);
  }
});

// Handle rectangle deletion
map.on(L.Draw.Event.DELETED, function (e) {
  hideResultsPanel();
});

// Store drawn rectangle bounds globally for export
window.drawnRectangleBounds = null;

// Add scale on map
var scale = L.control
  .scale({
    imperial: false,
    position: "topright",
    maxWidth: 70,
  })
  .addTo(map);

// Get Map Boundaries
function getMapBounds() {
  // Reduce precision from default 14 (!) to 4 digits
  var xmin = map.getBounds().toBBoxString().split(",")[0];
  var ymin = map.getBounds().toBBoxString().split(",")[1];
  var xmax = map.getBounds().toBBoxString().split(",")[2];
  var ymax = map.getBounds().toBBoxString().split(",")[3];
  xmin = Math.round(parseFloat(xmin) * 10000) / 10000;
  ymin = Math.round(parseFloat(ymin) * 10000) / 10000;
  xmax = Math.round(parseFloat(xmax) * 10000) / 10000;
  ymax = Math.round(parseFloat(ymax) * 10000) / 10000;
  var bboxString = ymin.toString() + ", " + xmin.toString();
  bboxString += "; " + ymax.toString() + ", " + xmax.toString();

  // Add map bounds to form elements for next query
  document.getElementById("xmin").setAttribute("value", xmin);
  document.getElementById("xmax").setAttribute("value", xmax);
  document.getElementById("ymin").setAttribute("value", ymin);
  document.getElementById("ymax").setAttribute("value", ymax);
  return bboxString;
}

// Determine Current ZOOM aspect and use to set polygon stroke width
var currentZoom;
var polygon;
map.on(
  "zoomend",
  function () {
    bboxString = getMapBounds();
    document.getElementById("map-bounds").innerHTML = bboxString;

    polygon = L.polygon({});
    currentZoom = map.getZoom();
    if (currentZoom >= 1) {
      polygon.setStyle({ weight: 1 });
    } else {
      polygon.setStyle({ weight: 3 });
    }

    var currentPos = map.getCenter();
    map.panTo([currentPos.lat, currentPos.lng + 0.0001]);
  },
  50
);

// Set up Slider Control
var sliderControl = L.control.sliderControl({
  isEpoch: true,
  startTimeAttribute: "start_ems",
  endTimeAttribute: "end_ems",
  layer: feature,
  range: true,
  showAllOnStart: true,
  alwaysShowDate: true,
  startTimeIdx: 0,
  timeStrLength: 10,
});
map.addControl(sliderControl);
$("#filter-center").html(sliderControl.getContainer());
sliderControl.startSlider();

// Determine which browser you are using and indicate and issue if needed using that browser
function fnBrowserDetect() {
  let userAgent = navigator.userAgent;
  let browserName;

  if (userAgent.match(/chrome|chromium|crios/i)) {
    browserName = "chrome";
  } else if (userAgent.match(/firefox|fxios/i)) {
    browserName = "firefox";
  } else if (userAgent.match(/safari/i)) {
    browserName = "safari";
  } else if (userAgent.match(/opr\//i)) {
    browserName = "opera";
  } else if (userAgent.match(/edg/i)) {
    browserName = "edge";
  } else {
    browserName = "No browser detection";
  }
  console.log("You are using " + browserName + " browser");
  return browserName;
}
/////////////////////////////////////////////////////////////////////////////////
// Determine which BaseMap is selected and if the Google Hybrid Map, change the
// stroke color to orange in order to visually see the tracks better
// Hovering over these orange track lines will also produce a yellow focus color change
////////////////////////////////////////////////////////////////////////////////

var radios = document.querySelectorAll(
  "input[type=radio][name=leaflet-exclusive-group-layer-0].leaflet-control-layers-selector"
);
[].forEach.call(radios, function (radio) {
  radio.onchange = function () {
    var radioButton = $(
      "input[name=leaflet-exclusive-group-layer-0].leaflet-control-layers-selector:checked"
    );
    var label_value = radioButton.closest("label").find("span").html();
    // console.log(
    //   "BaseMap Label: " +
    //     label_value +
    //     "\nradioButton: " +
    //     radioButton +
    //     "\nradios: " +
    //     radios
    // );
    for (var i = 0; i < radioButton.length; i++) {
      if (radioButton[i].checked) {
        if (label_value == "  Google Hybrid Layer ") {
          $("path.leaflet-interactive").css("stroke", "");
          $("path.leaflet-interactive").css("stroke", "orange");
          $(document).ready(function () {
            $("path.leaflet-interactive").hover(
              function () {
                $(this).css("stroke", "yellow");
              },
              function () {
                $(this).css("stroke", "orange");
              }
            );
          });
        } else {
          if (label_value !== "  Google Hybrid Layer ") {
            $(document).ready(function () {
              $("path.leaflet-interactive").css("stroke", "");
              $("path.leaflet-interactive").css("stroke", "rust");
              $("path.leaflet-interactive").hover(
                function () {
                  $(this).css("stroke", "yellow");
                },
                function () {
                  $(this).css("stroke", "");
                }
              );
            });
          }
        }
      }
    }
  };
});

/////////////////////////////////////////////////////////////////////////////
// Enable L.Control.Measure to be compatible with new Leaflet 1.8.0 release
L.Control.Measure.include({
  // set icon on the capture marker
  _setCaptureMarkerIcon: function () {
    // disable autopan
    this._captureMarker.options.autoPanOnFocus = false;

    // default function
    this._captureMarker.setIcon(
      L.divIcon({
        iconSize: this._map.getSize().multiplyBy(2),
      })
    );
  },
});

// Try and determine the active overlay - Currently not working.
L.Control.Layers.include({
  _getMapLayers: function () {
    // Create array for holding active layers
    var active = [];
    obj = this._active;
    control = this;
    // var map = this._map;

    this._groupedLayers.forEach(function (obj) {
      // Check if it's an overlay and added to the map
      if (obj.overlay && this._map.hasLayer(obj.layer)) {
        console.log("OBJECT OVERLAY");
        // Push layer to active array
        active.push(obj.layer);
      }
    });
    return active;
  },
});

L.Control.Layers.include({
  _getOverlays: function () {
    // create hash to hold all layers
    var control, layers;
    layers = {};
    control = this;

    // loop thru all layers in control
    control._layers.forEach(function (obj) {
      var layerName;

      // check if layer is an overlay
      if (obj.overlay) {
        // get name of overlay
        layerName = obj.name;
        // store whether it's present on the map or not
        return (layers[layerName] = control._map.hasLayer(obj.layer));
      }
    });
    return layers;
  },
});

// Results Panel Functions
function showResultsPanel(loading) {
  var panel = document.getElementById("selection-results-panel");
  if (!panel) {
    // Create results panel if it doesn't exist
    panel = document.createElement("div");
    panel.id = "selection-results-panel";
    panel.className = "selection-results-panel";
    panel.innerHTML = `
      <div class="selection-results-header">
        <h5>Selected Missions</h5>
        <button type="button" class="btn-close" onclick="hideResultsPanel()" aria-label="Close"></button>
      </div>
      <div class="selection-results-body">
        <div id="selection-results-content"></div>
      </div>
    `;
    document.body.appendChild(panel);
  }
  panel.style.display = "block";
  if (loading) {
    document.getElementById("selection-results-content").innerHTML = '<div class="text-center p-3"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  }
}

function hideResultsPanel() {
  var panel = document.getElementById("selection-results-panel");
  if (panel) {
    panel.style.display = "none";
  }
  // Also remove drawn rectangle
  if (drawnItems) {
    drawnItems.clearLayers();
  }
  // Clear stored bounds
  window.drawnRectangleBounds = null;
}

function updateResultsPanel(message, missions) {
  var content = document.getElementById("selection-results-content");
  if (!content) return;
  
  if (missions.length === 0) {
    content.innerHTML = '<div class="alert alert-info m-3">No missions found in the selected area.</div>';
    return;
  }
  
  var html = '<div class="selection-results-info p-3 border-bottom">';
  html += '<strong>' + missions.length + ' mission' + (missions.length !== 1 ? 's' : '') + ' found</strong>';
  html += '<div class="mt-2">';
  html += '<a href="#" class="btn btn-sm btn-primary me-2" onclick="exportMissions(\'csv\')">Export CSV</a>';
  html += '<a href="#" class="btn btn-sm btn-success" onclick="exportMissions(\'excel\')">Export Excel</a>';
  html += '</div>';
  html += '</div>';
  
  // Create table
  html += '<div class="table-responsive" style="max-height: 400px; overflow-y: auto;">';
  html += '<table class="table table-sm table-striped table-hover">';
  html += '<thead class="table-light sticky-top">';
  html += '<tr>';
  html += '<th>Name</th>';
  html += '<th>Start Date</th>';
  html += '<th>Region</th>';
  html += '<th>Track Length</th>';
  html += '<th>Start Depth</th>';
  html += '<th>Vehicle</th>';
  html += '<th>Expedition</th>';
  html += '</tr>';
  html += '</thead>';
  html += '<tbody>';
  
  missions.forEach(function(mission) {
    html += '<tr>';
    html += '<td><a href="/missions/' + mission.slug + '/">' + escapeHtml(mission.name) + '</a></td>';
    html += '<td>' + (mission.start_date || '-') + '</td>';
    html += '<td>' + (mission.region_name || '-') + '</td>';
    html += '<td>' + (mission.track_length || '-') + '</td>';
    html += '<td>' + (mission.start_depth || '-') + '</td>';
    html += '<td>' + (mission.vehicle_name || '-') + '</td>';
    html += '<td>' + (mission.expedition_name || '-') + '</td>';
    html += '</tr>';
  });
  
  html += '</tbody>';
  html += '</table>';
  html += '</div>';
  
  content.innerHTML = html;
  
  // Store missions for export
  window.selectedMissions = missions;
}

function escapeHtml(text) {
  if (!text) return '';
  var map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.toString().replace(/[&<>"']/g, function(m) { return map[m]; });
}

function fetchFilteredMissions(filterParams) {
  // Build query string
  var queryString = Object.keys(filterParams)
    .map(function(key) {
      return encodeURIComponent(key) + '=' + encodeURIComponent(filterParams[key]);
    })
    .join('&');
  
  // Fetch from API endpoint
  fetch('/api/v1/missions/select?' + queryString)
    .then(function(response) {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(function(data) {
      updateResultsPanel('', data.missions || []);
    })
    .catch(function(error) {
      console.error('Error fetching missions:', error);
      updateResultsPanel('Error loading missions. Please try again.', []);
    });
}

function exportMissions(format) {
  // Get bbox from stored global variable or drawn rectangle
  var bbox = window.drawnRectangleBounds;
  
  if (!bbox) {
    // Try to get from drawn items as fallback
    if (drawnItems && drawnItems.getLayers().length > 0) {
      var layer = drawnItems.getLayers()[0];
      if (layer instanceof L.Rectangle) {
        var bounds = layer.getBounds();
        bbox = {
          xmin: bounds.getWest(),
          ymin: bounds.getSouth(),
          xmax: bounds.getEast(),
          ymax: bounds.getNorth(),
        };
      }
    }
  }
  
  if (!bbox) {
    alert('No selection area found. Please draw a rectangle first.');
    return;
  }
  
  // Build query string from current filter params
  var urlParams = new URLSearchParams(window.location.search);
  var filterParams = {};
  var filterKeys = ['name', 'region_name', 'quality_categories', 'patch_test', 'repeat_survey', 'mgds_compilation', 'expedition__name', 'filter_type', 'q', 'tmin', 'tmax'];
  filterKeys.forEach(function(key) {
    if (urlParams.has(key)) {
      filterParams[key] = urlParams.get(key);
    }
  });
  
  // Add bbox to filter params
  filterParams.xmin = bbox.xmin;
  filterParams.xmax = bbox.xmax;
  filterParams.ymin = bbox.ymin;
  filterParams.ymax = bbox.ymax;
  
  // Add format parameter
  filterParams.format = format;
  
  // Build query string
  var queryString = Object.keys(filterParams)
    .map(function(key) {
      return encodeURIComponent(key) + '=' + encodeURIComponent(filterParams[key]);
    })
    .join('&');
  
  // Open export URL
  window.location.href = '/api/v1/missions/export?' + queryString;
}
