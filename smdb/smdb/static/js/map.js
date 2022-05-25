// /lib/leaflet.css
// /lib/leaflet-measure.css
// /lib/leaflet.js
// /lib/esri-leaflet.js
// /lib/esri-leaflet-vector.js
// /lib/Leaflet.GoogleMutant.js
// /lib/leaflet-google.js
// /lib/leaflet-measure.js

mapboxgl.accessToken =
  "pk.eyJ1Ijoic2FsYW15IiwiYSI6ImNrZjRlMGVpczBjNHgzMHZ3bWpmZWtsazcifQ.oR-gObeinElgR2KXLOYeWQ";
const map = L.map("map");
const media_url = JSON.parse(document.getElementById("MEDIA-URL").textContent);
const options = {
  minZoom: 1,
  maxNativeZoom: 13,
  maxZoom: 16,
  exclusiveGroups: ["Base Maps   &#127758; "],
  groupCheckboxes: true,
};

//Determine the BROWSER used - Important for ToolTip Date.parse
var browserName = fnBrowserDetect();

// Base layers
//ESRI_Oceans_Vector_Layer
const esriOceans = L.esri.Vector.vectorBasemapLayer(
  "ArcGIS:Oceans",
  {
    apikey:
      "AAPK4f2bc64881714cb2b03b1b5798dd2b740wn2YfXp7EZuoC_GggsJw92b06Ou-ZhL1i0CU-haX0JwKr9Ve9ned4wNTOYlGu1x",
  },
  options
);
/* 
L.esri.basemapLayer("Oceans", options).addTo(map);
L.esri.basemapLayer("OceansLabels", options).addTo(map); */

// Google_Hybrid_Layer
const googleHybrid = L.gridLayer.googleMutant({ type: "hybrid" });
googleHybrid.maxZoom = 16;

// Open_Maps_StreetView_Vector_Layer - was L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
const openMapStreetViewLayer = L.esri.Vector.vectorBasemapLayer(
  "OSM:Standard",
  {
    apikey:
      "AAPK4f2bc64881714cb2b03b1b5798dd2b740wn2YfXp7EZuoC_GggsJw92b06Ou-ZhL1i0CU-haX0JwKr9Ve9ned4wNTOYlGu1x",
  },
  options
);

// ArcGIS_Dark_Vector_Layer
const arcGISDark = L.esri.Vector.vectorBasemapLayer(
  "ArcGIS:DarkGray",
  {
    apikey:
      "AAPK4f2bc64881714cb2b03b1b5798dd2b740wn2YfXp7EZuoC_GggsJw92b06Ou-ZhL1i0CU-haX0JwKr9Ve9ned4wNTOYlGu1x",
  },
  options
);

// ArcGIS_Gray_Vector_Layer
const arcGISGray = L.esri.Vector.vectorBasemapLayer(
  "ArcGIS:LightGray",
  {
    apikey:
      "AAPK4f2bc64881714cb2b03b1b5798dd2b740wn2YfXp7EZuoC_GggsJw92b06Ou-ZhL1i0CU-haX0JwKr9Ve9ned4wNTOYlGu1x",
  },
  options
);

// Empty - From DashUI - Perhaps this is something others would like to have an option for
const emptyLayer = L.tileLayer("", { opacity: 0 });

//////////////////////////////////////////////////////////////////
// Construct a const map BASE LAYER OBJECT for Selection
const mapBaseLayers = {};

//Construct Grouped Overlays to Toggle
var groupedOverlays = {
  "Base Maps   &#127758; ": {
    " ESRI/ArcGIS Oceans ": esriOceans.addTo(map),
    //' ESRI/ArcGIS Imagery ': esriImagery,
    " Google Hybrid Layer ": googleHybrid,
    //' Google Satellite Layer ': googleSatellite,
    " OpenStreetMap Layer ": openMapStreetViewLayer,
    " ArcGIS Gray Layer ": arcGISGray,
    " ArcGIS Dark Layer ": arcGISDark,
    " No Map ": emptyLayer,
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
    '<input title="Use map bounds in Update" type="checkbox" style="vertical-align: middle" id="use_bounds">' +
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

////////////
// BaseMap Toggle Control Layers
var controlLayers = L.control.groupedLayers(
  mapBaseLayers,
  groupedOverlays,
  options
);
map.addControl(controlLayers);

//Determine the mapBaseLayer being currently used in browser
var mapBaseLayerName = fnMapLayerDetect();
//console.log("Map Base Layer: " + mapBaseLayerName);
//////////////////////

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

// add Leaflet-Geoman controls with some options to the map
map.pm
  .addControls({
    position: "topleft",
    drawCircle: false,
    drawMarker: false,
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

// Try and get information on ActiveLayer with each map pan
//map.on("moveend", function (event) {
/*   var layer = this.layer;
  console.log('Layer name -> ', event.name);
  fnMapLayerDetect(); */
//console.log(map.getCenter().toString());
//});

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

// Try and determine the active overlay - Currently not working.
// function getOverlays() {
// create hash to hold all layers
/*  var control;
  const layers = {}; */
//var obj = this._layers;
/*   control = this;
  var layerName;
  var map = this._map;
  console.log("Testing " + map.itemInfo.itemData.operationalLayers);
 */
// loop thru all layers in control
// control._layers?.forEach((obj) => {
// check if layer is an overlay
// if (obj.overlay) {
// get name of overlay
/*         layerName = obj.name;
          console.log("LayerName: " + layerName); */
// store whether it's present on the map or not
/*         return layers[layerName] = control._map.hasLayer(obj.layer);
      }
    });
  console.log("Active Layer: " + layers);
  return layers;
}  */

// Set up a Map Layer Detection Function
function fnMapLayerDetect() {
  //add the layer to the overlayMaps with a dynamic layer name (e.g. overlayMaps[layerName] = layer1;)
  groupedOverlays[" ESRI/ArcGIS Oceans "] = esriOceans;
  groupedOverlays[" Google Hybrid Layer "] = googleHybrid;
  groupedOverlays[" OpenStreetMap Layer "] = openMapStreetViewLayer;
  groupedOverlays[" ArcGIS Lt. Gray Layer "] = arcGISGray;
  groupedOverlays[" ArcGIS Dark Layer "] = arcGISDark;
  groupedOverlays[" No Map "] = emptyLayer;
}
