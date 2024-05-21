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
  maxNativeZoom: 13,
  maxZoom: 16,
  exclusiveGroups: ["Base Maps   &#127758; "],
  groupCheckboxes: true,
};

const map = L.map("map", {
  options,
});
const media_url = JSON.parse(document.getElementById("MEDIA-URL").textContent);

// Change the position of the Zoom Control to bottomright.
map.zoomControl.setPosition("bottomright");
map.options.minZoom = 2.495;
map.attributionControl.setPosition("bottomleft")

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
const missions = JSON.parse(
  document.getElementById("missions-data").textContent
);

// Add SMDB Missions to Base Map
let feature = L.geoJSON(missions, {
  style: function () {},
  hover: function () {},
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
      "<br>Info: " +
      missionInfo;
    return tooltipInfo;
  })
  .addTo(map);
try {
  map.fitBounds(feature.getBounds(), { padding: [100, 100] });
} catch (err) {
  console.log(err.message);
}

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

////////  ADD GEOMAN for LEAFLET  /////////
var toggle = L.easyButton({
  position: "topright",
  id: "geoMan",
  states: [
    {
      stateName: "add-geoman",
      icon: "fas fa-draw-polygon fa-xl",
      title: "Show Geometry Toolbar",
      onClick: function (control) {
        map.pm.addControls({
          position: "topright",
          drawControls: true,
          editControls: true,
          editMode: false,
          optionsControls: true,
          customControls: true,
          oneBlock: true,
          enableGlobalRotateMode: true,
        });
        control.state("remove-geoman");
        // Check Geoman Geometry Tool Status
        if (control.state("remove-geoman")) {
          console.log("Geoman menu open!");
          // toggle.onClick = updateMap();
        }
      },
    },
    {
      stateName: "remove-geoman",
      icon: "fa-undo",
      title: "Hide Geometry Toolbar",
      onClick: function (control) {
        map.pm.removeControls();
        control.state("add-geoman");
        // Check Geoman Geometry Tool Status
        if (control.state("add-geoman")) {
          console.log("Geoman menu closed!");
        }
        // toggle.onClick = updateMap();
      },
    },
  ],
});
toggle.addTo(map);
