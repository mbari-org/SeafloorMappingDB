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
    sidebar.style.left = "-250px"; // Hidden by default (slide out from left)
    sidebar.style.top = "0";
    sidebar.style.width = "250px";
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
    body.style.paddingBottom = "0.75rem"; // Ensure bottom padding for buttons
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
      
      // Debug: Log form structure to see if buttons are present
      console.log("Form HTML:", clonedForm.innerHTML);
      console.log("Buttons in form:", clonedForm.querySelectorAll("button").length);
      console.log("All rows:", clonedForm.querySelectorAll(".row").length);
      
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
            
            // Store sidebar open state before reloading
            sessionStorage.setItem('sidebarOpen', 'true');
            
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
        el.style.maxWidth = "230px";
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

      // Create custom dropdown for quality categories with checkboxes
      const qualitySelect = body.querySelector('select[name="quality_categories"]');
      const locationSelect = body.querySelector('select[name="region_name"]');
      
      if (qualitySelect && qualitySelect.options.length > 0) {
        // Hide the original select
        qualitySelect.style.display = "none";
        
        // Create custom dropdown container
        const dropdownContainer = document.createElement('div');
        dropdownContainer.className = 'quality-dropdown-container';
        dropdownContainer.style.position = 'relative';
        dropdownContainer.style.width = '230px';
        dropdownContainer.style.minWidth = '230px';
        dropdownContainer.style.maxWidth = '230px';
        dropdownContainer.style.marginBottom = '0.4rem';
        dropdownContainer.style.flexShrink = '0';
        dropdownContainer.style.flexGrow = '0';
        
        // Create dropdown button (looks like Location field)
        const dropdownButton = document.createElement('button');
        dropdownButton.type = 'button';
        dropdownButton.className = 'quality-dropdown-button';
        dropdownButton.textContent = '- Quality assessment -';
        dropdownButton.style.width = '230px';
        dropdownButton.style.minWidth = '230px';
        dropdownButton.style.maxWidth = '230px';
        dropdownButton.style.padding = '0.3rem';
        dropdownButton.style.fontSize = '0.8rem';
        dropdownButton.style.fontWeight = '300';
        dropdownButton.style.border = '1px solid #555';
        dropdownButton.style.borderRadius = '4px';
        dropdownButton.style.backgroundColor = '#1e1e1e';
        dropdownButton.style.color = '#e0e0e0';
        dropdownButton.style.textAlign = 'left';
        dropdownButton.style.cursor = 'pointer';
        dropdownButton.style.boxSizing = 'border-box';
        dropdownButton.style.position = 'relative';
        dropdownButton.style.paddingRight = '2rem';
        dropdownButton.style.overflow = 'hidden';
        dropdownButton.style.textOverflow = 'ellipsis';
        dropdownButton.style.whiteSpace = 'nowrap';
        
        // Match the native select dropdown arrow from Location field
        // Native HTML select elements use browser's default dropdown arrow
        // We'll create a visual match - browsers typically use a downward triangle/chevron
        const locationSelect = body.querySelector('select[name="region_name"]');
        
        // Create V-shaped chevron caret to match Location field dropdown
        const caret = document.createElement('span');
        // Use V-shaped chevron (⌄) to match native select dropdown appearance
        caret.innerHTML = '⌄'; // Downward V-shaped chevron
        caret.style.position = 'absolute';
        caret.style.right = '0.3rem'; // Move a few pixels to the right (smaller right value = more to the right)
        caret.style.top = '38%'; // Slightly above center to account for visual centering
        caret.style.transform = 'translateY(-50%) scaleX(1.3)'; // Center vertically and widen the V
        caret.style.transformOrigin = 'center center'; // Ensure scaling happens from center
        caret.style.fontSize = '1.2rem'; // Size to match image
        caret.style.color = '#ffffff'; // White color
        caret.style.pointerEvents = 'none';
        caret.style.lineHeight = '0'; // Remove line-height to prevent extra space
        caret.style.display = 'flex';
        caret.style.alignItems = 'center';
        caret.style.justifyContent = 'center';
        caret.style.fontWeight = 'bold'; // Make it bolder/thicker
        caret.style.fontFamily = 'Arial, sans-serif';
        caret.style.letterSpacing = '0'; // No extra spacing
        dropdownButton.appendChild(caret);
        
        // Create dropdown menu
        const dropdownMenu = document.createElement('div');
        dropdownMenu.className = 'quality-dropdown-menu';
        dropdownMenu.style.display = 'none';
        dropdownMenu.style.position = 'absolute';
        dropdownMenu.style.top = '100%';
        dropdownMenu.style.left = '0';
        dropdownMenu.style.width = '230px';
        dropdownMenu.style.minWidth = '230px';
        dropdownMenu.style.maxWidth = '230px';
        dropdownMenu.style.maxHeight = '200px';
        dropdownMenu.style.overflowY = 'auto';
        dropdownMenu.style.backgroundColor = '#2d2d2d';
        dropdownMenu.style.border = '1px solid #555';
        dropdownMenu.style.borderRadius = '4px';
        dropdownMenu.style.marginTop = '2px';
        dropdownMenu.style.zIndex = '1000';
        dropdownMenu.style.boxShadow = '0 4px 6px rgba(0,0,0,0.3)';
        // Hide scrollbar
        dropdownMenu.style.scrollbarWidth = 'thin';
        dropdownMenu.style.scrollbarColor = 'transparent transparent';
        dropdownMenu.setAttribute('class', 'quality-dropdown-menu custom-scrollbar');
        
        // Track last clicked checkbox for Shift+Click range selection
        let lastClickedCheckbox = null;
        
        // Create checkbox options
        Array.from(qualitySelect.options).forEach((option, index) => {
          if (option.value) { // Skip empty placeholder option
            const checkboxItem = document.createElement('label');
            checkboxItem.style.display = 'flex';
            checkboxItem.style.alignItems = 'center';
            checkboxItem.style.padding = '0.5rem';
            checkboxItem.style.cursor = 'pointer';
            checkboxItem.style.color = '#ffffff'; // White text for better visibility
            checkboxItem.style.fontSize = '0.8rem';
            checkboxItem.style.borderBottom = '1px solid #444';
            checkboxItem.style.marginBottom = '0';
            
            checkboxItem.addEventListener('mouseenter', function() {
              this.style.backgroundColor = '#3d3d3d';
            });
            checkboxItem.addEventListener('mouseleave', function() {
              this.style.backgroundColor = 'transparent';
            });
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = option.value;
            checkbox.name = 'quality_categories';
            checkbox.style.width = '14px';
            checkbox.style.height = '14px';
            checkbox.style.marginRight = '0.5rem';
            checkbox.style.cursor = 'pointer';
            checkbox.style.flexShrink = '0';
            
            // Store index for Shift+Click range selection
            checkbox.dataset.index = index;
            
            // Sync with original select
            checkbox.checked = option.selected;
            
            // Handle checkbox change with Shift+Click support
            checkbox.addEventListener('click', function(e) {
              if (e.shiftKey && lastClickedCheckbox && lastClickedCheckbox !== checkbox) {
                // Shift+Click: select range between last clicked and current
                e.preventDefault();
                const checkboxes = Array.from(dropdownMenu.querySelectorAll('input[type="checkbox"]'));
                const startIndex = parseInt(lastClickedCheckbox.dataset.index);
                const endIndex = parseInt(checkbox.dataset.index);
                const start = Math.min(startIndex, endIndex);
                const end = Math.max(startIndex, endIndex);
                
                // Use the state of the last clicked checkbox as the target state
                const targetState = lastClickedCheckbox.checked;
                
                // Set all checkboxes in range to the target state
                for (let i = start; i <= end; i++) {
                  const cb = checkboxes[i];
                  if (cb) {
                    cb.checked = targetState;
                    const originalOption = qualitySelect.querySelector(`option[value="${cb.value}"]`);
                    if (originalOption) {
                      originalOption.selected = targetState;
                    }
                  }
                }
                
                // Trigger change event on original select
                qualitySelect.dispatchEvent(new Event('change', { bubbles: true }));
                updateButtonText();
              } else {
                // Normal click: checkbox state is toggled automatically by browser
                // Just sync with original select
                const originalOption = qualitySelect.querySelector(`option[value="${this.value}"]`);
                if (originalOption) {
                  originalOption.selected = this.checked;
                  // Trigger change event on original select
                  qualitySelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
                updateButtonText();
              }
              
              // Update last clicked checkbox
              lastClickedCheckbox = checkbox;
            });
            
            const labelText = document.createElement('span');
            labelText.textContent = option.text;
            labelText.style.color = '#ffffff'; // White text for visibility
            labelText.style.flex = '1';
            
            checkboxItem.appendChild(checkbox);
            checkboxItem.appendChild(labelText);
            dropdownMenu.appendChild(checkboxItem);
          }
        });
        
        // Function to update button text
        function updateButtonText() {
          const selectedOptions = Array.from(qualitySelect.selectedOptions).filter(opt => opt.value);
          let displayText = '- Quality assessment -';
          
          if (selectedOptions.length === 0) {
            displayText = '- Quality assessment -';
          } else if (selectedOptions.length === 1) {
            displayText = selectedOptions[0].text;
          } else {
            // Show all selected options as comma-separated list
            displayText = selectedOptions.map(opt => opt.text).join(', ');
          }
          
          // Update text content while preserving the caret element
          // Remove all text nodes but keep the caret span
          const nodesToRemove = [];
          Array.from(dropdownButton.childNodes).forEach(node => {
            if (node.nodeType === Node.TEXT_NODE) {
              nodesToRemove.push(node);
            } else if (node.nodeType === Node.ELEMENT_NODE && node !== caret) {
              nodesToRemove.push(node);
            }
          });
          nodesToRemove.forEach(node => node.remove());
          
          // Insert new text before the caret
          dropdownButton.insertBefore(document.createTextNode(displayText), caret);
          
          // Ensure button maintains fixed width to prevent layout shifts
          dropdownButton.style.width = '230px';
          dropdownButton.style.minWidth = '230px';
          dropdownButton.style.maxWidth = '230px';
        }
        
        // Toggle dropdown
        dropdownButton.addEventListener('click', function(e) {
          e.stopPropagation();
          const isOpen = dropdownMenu.style.display === 'block';
          dropdownMenu.style.display = isOpen ? 'none' : 'block';
          
          // Close other dropdowns
          body.querySelectorAll('.quality-dropdown-menu').forEach(menu => {
            if (menu !== dropdownMenu) {
              menu.style.display = 'none';
            }
          });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
          if (!dropdownContainer.contains(e.target)) {
            dropdownMenu.style.display = 'none';
          }
        });
        
        // Insert custom dropdown before the hidden select
        const parentElement = qualitySelect.parentElement;
        dropdownContainer.appendChild(dropdownButton);
        dropdownContainer.appendChild(dropdownMenu);
        parentElement.insertBefore(dropdownContainer, qualitySelect);
        
        // Initialize button text
        updateButtonText();
      }

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

      // Style buttons - find ALL buttons, not just .btn class
      const allButtons = body.querySelectorAll("button");
      console.log("Found buttons:", allButtons.length);
      allButtons.forEach((btn) => {
        // Ensure button is visible
        btn.style.display = "block";
        btn.style.visibility = "visible";
        btn.style.opacity = "1";
        btn.style.fontSize = "0.75rem";
        btn.style.padding = "0.4rem 0.6rem"; // Reduced horizontal padding
        // Check if buttons are in a row - if so, make them share the row width
        const parentRow = btn.closest(".row");
        const parentColumn = btn.closest("[class*='col-']");
        if (parentRow && parentRow.querySelectorAll("button").length > 1) {
          // Multiple buttons in same row - make them narrower to fit side by side
          // Ensure the column container doesn't force full width
          if (parentColumn) {
            parentColumn.style.flex = "1 1 auto";
            parentColumn.style.minWidth = "0";
            parentColumn.style.maxWidth = "none";
            parentColumn.style.width = "auto";
            parentColumn.style.flexBasis = "auto";
            parentColumn.style.display = "block";
            parentColumn.style.visibility = "visible";
          }
          btn.style.width = "100%";
          btn.style.minWidth = "60px";
          btn.style.maxWidth = "none";
          btn.style.marginRight = "0.3rem";
          btn.style.marginTop = "0.2rem";
        } else {
          // Single button - full width
          btn.style.width = "100%";
          btn.style.maxWidth = "230px";
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
        // Ensure button row is visible and aligned
        if (parentRow) {
          parentRow.style.display = "flex";
          parentRow.style.visibility = "visible";
          parentRow.style.opacity = "1";
          parentRow.style.alignItems = "flex-start"; // Align items to start (top)
          // If this row contains buttons, ensure they're aligned
          if (parentRow.querySelectorAll("button").length > 0) {
            parentRow.style.alignItems = "center"; // Center align buttons vertically
            // Center buttons horizontally on the row
            if (btn.classList.contains("button-row")) {
              parentRow.style.justifyContent = "center"; // Center buttons horizontally
            }
          }
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
            
            // Store sidebar open state before reloading
            sessionStorage.setItem('sidebarOpen', 'true');
            
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
        row.style.visibility = "visible";
        row.style.opacity = "1";
        // Override Bootstrap's default row display
        row.style.setProperty("display", "flex", "important");
        // Ensure row is not hidden
        row.style.setProperty("visibility", "visible", "important");
        row.style.setProperty("opacity", "1", "important");
      });
      
      // Remove left padding from columns and ensure they work with flex
      body.querySelectorAll(".col-md, [class*='col-']").forEach((col) => {
        col.style.paddingLeft = "0.25rem"; // Minimal left padding
        col.style.paddingRight = "0.25rem"; // Minimal right padding
        // Make all columns flexible to use full sidebar width
        col.style.flex = "1 1 auto";
        col.style.minWidth = "0";
        col.style.maxWidth = "none";
        col.style.width = "auto";
        col.style.flexBasis = "auto";
        // Override Bootstrap's default column width
        col.style.setProperty("width", "auto", "important");
        col.style.setProperty("flex-basis", "auto", "important");
      });
      
      // Make expedition__name field column expand to full width (230px) like Name field
      // This will naturally push buttons to wrap to next line
      const expeditionNameInput = body.querySelector('input[name="expedition__name"], select[name="expedition__name"]');
      if (expeditionNameInput) {
        const expeditionColumn = expeditionNameInput.closest("[class*='col-']");
        if (expeditionColumn) {
          // Override the general column styling to force full width (230px) when wrapping
          // This makes it behave like the Name field above it
          expeditionColumn.style.setProperty("flex-basis", "230px", "important");
          expeditionColumn.style.setProperty("min-width", "230px", "important");
          expeditionColumn.style.setProperty("width", "230px", "important");
          // This will cause the row to wrap, pushing buttons to next line
        }
      }
      
      // Force buttons to wrap to new line by making their columns full width
      body.querySelectorAll(".button-row").forEach((btn) => {
        const btnColumn = btn.closest("[class*='col-']");
        if (btnColumn) {
          btnColumn.style.width = "100%";
          btnColumn.style.flexBasis = "100%";
          btnColumn.style.maxWidth = "100%";
          btnColumn.style.marginTop = "0.5rem";
        }
      });

      // Auto-adjust sidebar height after form is copied
      setTimeout(function () {
        if (sidebar) {
          // Force a reflow to ensure all content is measured
          body.style.display = "block";
          const bodyHeight = body.scrollHeight;
          const header = sidebar.querySelector(".filter-sidebar-header");
          const headerHeight = header ? header.offsetHeight : 50;
          // Include padding in calculation to ensure buttons are fully visible
          const bodyPadding = parseFloat(window.getComputedStyle(body).paddingTop) + 
                             parseFloat(window.getComputedStyle(body).paddingBottom);
          const totalHeight = bodyHeight + headerHeight + bodyPadding;
          const maxHeight = window.innerHeight * 0.8;
          sidebar.style.height = Math.min(totalHeight, maxHeight) + "px";
        }
      }, 150);

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
              btn.style.maxWidth = "230px";
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
      // Button is 20px from map edge when closed, sidebar is 250px wide starting at 0px
      // So button should be at 250px (right edge of sidebar)
      container.style.left = "250px"; // Move button to right edge of sidebar
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

        // Force a reflow to ensure all content is measured
        body.style.display = "block";
        const bodyHeight = body.scrollHeight;
        const headerHeight =
          sidebar.querySelector(".filter-sidebar-header")?.offsetHeight || 50;
        // Include padding in calculation to ensure buttons are fully visible
        const bodyPadding = parseFloat(window.getComputedStyle(body).paddingTop) + 
                           parseFloat(window.getComputedStyle(body).paddingBottom);
        const totalHeight = bodyHeight + headerHeight + bodyPadding;
        sidebar.style.height =
          Math.min(totalHeight, window.innerHeight * 0.8) + "px";
      }
    }

    // Helper function to hide sidebar (slide back left, button returns to left)
    function hideSidebar() {
      if (!sidebarOpen) {
        sidebar.style.left = "-250px"; // Hide sidebar
        container.style.left = "20px"; // Return button to 20px from left edge
        // Icon change is handled in click handler with animation
      }
    }

    // Ensure icon is set correctly initially (filter icon when closed)
    if (!sidebarOpen) {
      icon.className = "fas fa-filter";
      icon.style.fontSize = "18px";
      icon.style.color = "#007bff";
    }
    
    // Check if sidebar should be open from sessionStorage (after Clear button reload)
    const shouldOpenSidebar = sessionStorage.getItem('sidebarOpen') === 'true';
    if (shouldOpenSidebar) {
      sidebarOpen = true;
      icon.className = "fas fa-times"; // Set to X (close icon)
      icon.style.fontSize = "18px";
      icon.style.color = "#007bff";
      showSidebar();
      // Clear the sessionStorage flag
      sessionStorage.removeItem('sidebarOpen');
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

// Add tooltip to draw button
setTimeout(function() {
  var drawButton = document.querySelector('.leaflet-draw-draw-rectangle');
  if (drawButton) {
    drawButton.setAttribute('title', 'Draw Rectangle - Click and drag to create a rectangular selection area');
  }
}, 200);

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

// Handle rectangle deletion - don't close panel, just remove rectangle
map.on(L.Draw.Event.DELETED, function (e) {
  // Panel stays open - user must manually close it with X button
  // Just remove the rectangle from the map
  if (drawnItems) {
    drawnItems.clearLayers();
  }
  // Clear stored bounds but keep panel open
  window.drawnRectangleBounds = null;
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
        <button type="button" class="btn-close" onclick="hideResultsPanel()" aria-label="Close">×</button>
      </div>
      <div class="selection-results-body">
        <div id="selection-results-content"></div>
      </div>
      <div class="resize-handle resize-handle-n"></div>
      <div class="resize-handle resize-handle-e"></div>
      <div class="resize-handle resize-handle-s"></div>
      <div class="resize-handle resize-handle-w"></div>
      <div class="resize-handle resize-handle-ne"></div>
      <div class="resize-handle resize-handle-nw"></div>
      <div class="resize-handle resize-handle-se"></div>
      <div class="resize-handle resize-handle-sw"></div>
    `;
    document.body.appendChild(panel);
    
    // Prevent clicks on panel from propagating to map (prevents accidental closing)
    panel.addEventListener('click', function(e) {
      e.stopPropagation();
    });
    
    // Prevent mousedown events from propagating to map
    panel.addEventListener('mousedown', function(e) {
      e.stopPropagation();
    });
    
    // Prevent wheel events from propagating to map (allows panel to scroll)
    panel.addEventListener('wheel', function(e) {
      e.stopPropagation();
      
      // Find the scrollable container (selection-results-body)
      var body = panel.querySelector('.selection-results-body');
      if (body) {
        var scrollTop = body.scrollTop;
        var scrollHeight = body.scrollHeight;
        var clientHeight = body.clientHeight;
        
        // Check if we can scroll
        if (scrollHeight > clientHeight) {
          // Prevent default map zoom/pan behavior
          e.preventDefault();
          
          // Scroll the body
          var delta = e.deltaY;
          body.scrollTop += delta;
          
          // Prevent further propagation
          e.stopImmediatePropagation();
        }
      }
    }, { passive: false });
    
    // Detect when mouse is over scrollbar area and disable resize handles
    var body = panel.querySelector('.selection-results-body');
    if (body) {
      body.addEventListener('mousemove', function(e) {
        var rect = body.getBoundingClientRect();
        var scrollbarWidth = 17; // Typical scrollbar width
        var scrollbarHeight = 17; // Typical scrollbar height
        
        // Check if mouse is in scrollbar area (right edge for vertical, bottom for horizontal)
        var isOverVerticalScrollbar = (e.clientX >= rect.right - scrollbarWidth && e.clientX <= rect.right);
        var isOverHorizontalScrollbar = (e.clientY >= rect.bottom - scrollbarHeight && e.clientY <= rect.bottom);
        // Check if mouse is in the scrollbar intersection (bottom-right corner where scrollbars meet)
        var isOverScrollbarIntersection = isOverVerticalScrollbar && isOverHorizontalScrollbar;
        
        // Get resize handles
        var handleE = panel.querySelector('.resize-handle-e');
        var handleS = panel.querySelector('.resize-handle-s');
        var handleSE = panel.querySelector('.resize-handle-se');
        
        // Disable right edge handle when over vertical scrollbar (but not intersection)
        if (handleE) {
          if (isOverVerticalScrollbar && !isOverScrollbarIntersection) {
            handleE.classList.add('scrollbar-active');
          } else {
            handleE.classList.remove('scrollbar-active');
          }
        }
        
        // Disable bottom handle when over horizontal scrollbar (but not intersection)
        if (handleS) {
          if (isOverHorizontalScrollbar && !isOverScrollbarIntersection) {
            handleS.classList.add('scrollbar-active');
          } else {
            handleS.classList.remove('scrollbar-active');
          }
        }
        
        // Bottom-right corner handle is always active (never disabled)
        // The reserved space prevents scrollbars from overlapping it
        if (handleSE) {
          handleSE.classList.remove('scrollbar-active');
        }
      });
      
      body.addEventListener('mouseleave', function() {
        // Remove scrollbar-active when mouse leaves body
        var handleE = panel.querySelector('.resize-handle-e');
        var handleS = panel.querySelector('.resize-handle-s');
        var handleSE = panel.querySelector('.resize-handle-se');
        if (handleE) handleE.classList.remove('scrollbar-active');
        if (handleS) handleS.classList.remove('scrollbar-active');
        if (handleSE) handleSE.classList.remove('scrollbar-active');
      });
    }
    
    // Initialize drag functionality
    initializePanelDrag(panel);
    
    // Initialize resize functionality
    initializePanelResize(panel);
  }
  panel.style.display = "flex";
  
  // Force a synchronous layout calculation to ensure panel is rendered
  panel.offsetHeight;
  
  // Convert CSS percentage transform to pixel transform immediately
  // This must happen synchronously before any user interaction
  var currentTransform = panel.style.transform || '';
  if (!currentTransform || currentTransform.indexOf('%') !== -1) {
    var rect = panel.getBoundingClientRect();
    var currentCenterX = rect.left + rect.width / 2;
    var currentCenterY = rect.top + rect.height / 2;
    var viewportCenterX = window.innerWidth / 2;
    var viewportCenterY = window.innerHeight / 2;
    var pixelOffsetX = currentCenterX - viewportCenterX;
    var pixelOffsetY = currentCenterY - viewportCenterY;
    
    panel.style.transform = 'translate(' + pixelOffsetX + 'px, ' + pixelOffsetY + 'px)';
    
    // Force reflow
    panel.offsetHeight;
    
    // Mark as converted so dragStart doesn't convert again
    panel._transformConverted = true;
  } else {
    panel._transformConverted = true;
  }
  
  if (loading) {
    document.getElementById("selection-results-content").innerHTML = '<div class="text-center p-3"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  }
}

// Initialize drag functionality for panel
function initializePanelDrag(panel) {
  var header = panel.querySelector('.selection-results-header');
  var isDragging = false;
  var startX = 0;
  var startY = 0;
  var startLeft = 0;
  var startTop = 0;

  header.addEventListener('mousedown', dragStart);
  document.addEventListener('mousemove', drag);
  document.addEventListener('mouseup', dragEnd);

  function dragStart(e) {
    // Don't start drag if clicking the close button
    if (e.target.classList.contains('btn-close') || e.target.closest('.btn-close')) {
      return;
    }
    
    if (e.target === header || header.contains(e.target)) {
      e.preventDefault();
      e.stopPropagation();
      
      // Get current mouse position
      startX = e.clientX;
      startY = e.clientY;
      
      // Get current panel position - use getBoundingClientRect for actual rendered position
      // This gives us the true visual position regardless of transform type
      var rect = panel.getBoundingClientRect();
      startLeft = rect.left;
      startTop = rect.top;
      
      isDragging = true;
      header.style.cursor = 'move';
    }
  }

  function drag(e) {
    if (isDragging) {
      e.preventDefault();
      
      // On first drag movement, ensure transform is in pixels
      if (!panel._dragTransformConverted) {
        var currentTransform = panel.style.transform || '';
        
        if (!currentTransform || currentTransform.indexOf('%') !== -1) {
          // Convert to pixels using current position BEFORE any movement
          // Use the startLeft/startTop we captured in dragStart
          var panelWidth = panel.offsetWidth;
          var panelHeight = panel.offsetHeight;
          var panelCenterX = startLeft + panelWidth / 2;
          var panelCenterY = startTop + panelHeight / 2;
          var viewportCenterX = window.innerWidth / 2;
          var viewportCenterY = window.innerHeight / 2;
          var pixelOffsetX = panelCenterX - viewportCenterX;
          var pixelOffsetY = panelCenterY - viewportCenterY;
          
          panel.style.transform = 'translate(' + pixelOffsetX + 'px, ' + pixelOffsetY + 'px)';
          
          // Force reflow
          panel.offsetHeight;
          
          // Get position AFTER transform change
          var rectAfter = panel.getBoundingClientRect();
          
          // Update start positions if panel moved
          if (Math.abs(rectAfter.left - startLeft) > 0.1 || Math.abs(rectAfter.top - startTop) > 0.1) {
            startLeft = rectAfter.left;
            startTop = rectAfter.top;
          }
        }
        panel._dragTransformConverted = true;
      }
      
      // Calculate how far mouse has moved
      var deltaX = e.clientX - startX;
      var deltaY = e.clientY - startY;
      
      // Calculate new panel position (top-left corner)
      var newLeft = startLeft + deltaX;
      var newTop = startTop + deltaY;
      
      // IMPORTANT: Panel has left: 50% and top: 50%, which means its top-left corner is at viewport center
      // When we apply transform: translate(Xpx, Ypx), the top-left corner ends up at:
      // (viewportCenterX + X, viewportCenterY + Y)
      // So to get the top-left at newLeft, newTop:
      // newLeft = viewportCenterX + transformX
      // newTop = viewportCenterY + transformY
      // Therefore:
      var viewportCenterX = window.innerWidth / 2;
      var viewportCenterY = window.innerHeight / 2;
      
      // Calculate transform needed to position top-left at newLeft, newTop
      var transformX = newLeft - viewportCenterX;
      var transformY = newTop - viewportCenterY;
      
      panel.style.transform = 'translate(' + transformX + 'px, ' + transformY + 'px)';
    }
  }
  
  function dragEnd(e) {
    if (isDragging) {
      isDragging = false;
      header.style.cursor = 'default';
      panel._dragTransformConverted = false;
    }
  }
}

// Initialize resize functionality for panel
function initializePanelResize(panel) {
  if (!panel) return;
  
  var resizeHandles = panel.querySelectorAll('.resize-handle');
  if (!resizeHandles || resizeHandles.length === 0) {
    return; // No resize handles found, skip initialization
  }
  
  var isResizing = false;
  var currentHandle = null;
  var startX, startY, startWidth, startHeight, startLeft, startTop, startTransformX, startTransformY;

  resizeHandles.forEach(function(handle) {
    handle.addEventListener('mousedown', function(e) {
      e.preventDefault();
      e.stopPropagation();
      isResizing = true;
      currentHandle = handle;
      startX = e.clientX;
      startY = e.clientY;
      startWidth = parseInt(document.defaultView.getComputedStyle(panel).width, 10);
      startHeight = parseInt(document.defaultView.getComputedStyle(panel).height, 10);
      
      // Get current position accounting for transform
      var rect = panel.getBoundingClientRect();
      startLeft = rect.left;
      startTop = rect.top;
      
      // Parse current transform
      var transform = panel.style.transform || '';
      var match = transform.match(/translate\(([^,]+),\s*([^)]+)\)/);
      startTransformX = match ? parseFloat(match[1]) : 0;
      startTransformY = match ? parseFloat(match[2]) : 0;
      
      document.addEventListener('mousemove', doResize);
      document.addEventListener('mouseup', stopResize);
    });
  });

  function doResize(e) {
    if (!isResizing) return;
    
    var deltaX = e.clientX - startX;
    var deltaY = e.clientY - startY;
    
    var width = startWidth;
    var height = startHeight;
    var transformX = startTransformX;
    var transformY = startTransformY;
    
    if (currentHandle.classList.contains('resize-handle-e')) {
      width = startWidth + deltaX;
    } else if (currentHandle.classList.contains('resize-handle-w')) {
      width = startWidth - deltaX;
      transformX = startTransformX + deltaX;
    } else if (currentHandle.classList.contains('resize-handle-s')) {
      height = startHeight + deltaY;
    } else if (currentHandle.classList.contains('resize-handle-n')) {
      height = startHeight - deltaY;
      transformY = startTransformY + deltaY;
    } else if (currentHandle.classList.contains('resize-handle-se')) {
      width = startWidth + deltaX;
      height = startHeight + deltaY;
    } else if (currentHandle.classList.contains('resize-handle-sw')) {
      width = startWidth - deltaX;
      height = startHeight + deltaY;
      transformX = startTransformX + deltaX;
    } else if (currentHandle.classList.contains('resize-handle-ne')) {
      width = startWidth + deltaX;
      height = startHeight - deltaY;
      transformY = startTransformY + deltaY;
    } else if (currentHandle.classList.contains('resize-handle-nw')) {
      width = startWidth - deltaX;
      height = startHeight - deltaY;
      transformX = startTransformX + deltaX;
      transformY = startTransformY + deltaY;
    }
    
    // Apply min/max constraints
    var minWidth = 400;
    var minHeight = 300;
    var maxWidth = window.innerWidth - 20;
    var maxHeight = window.innerHeight - 20;
    
    width = Math.max(minWidth, Math.min(maxWidth, width));
    height = Math.max(minHeight, Math.min(maxHeight, height));
    
    // Set width and height with box-sizing
    panel.style.width = width + 'px';
    panel.style.height = height + 'px';
    panel.style.boxSizing = 'border-box';
    panel.style.transform = 'translate(' + transformX + 'px, ' + transformY + 'px)';
    
    // Force reflow to ensure content adjusts
    panel.offsetHeight;
  }

  function stopResize() {
    isResizing = false;
    currentHandle = null;
    document.removeEventListener('mousemove', doResize);
    document.removeEventListener('mouseup', stopResize);
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
  html += '<div class="table-responsive">';
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
  
  // Mark as exported
  window.resultsPanelExported = true;
  
  // Open export URL
  window.location.href = '/api/v1/missions/export?' + queryString;
}
