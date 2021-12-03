// /lib/leaflet.css
// /lib/leaflet.js
// /lib/esri-leaflet.js

const map = L.map("map");
const media_url = JSON.parse(document.getElementById("MEDIA-URL").textContent);
const options  = { minZoom: 1, maxZoom: 16, }

L.esri.basemapLayer('Oceans', options).addTo(map);
L.esri.basemapLayer('OceansLabels', options).addTo(map);
//L.esri.basemapLayer('Streets', options).addTo(map);

map.fitWorld();
const missions = JSON.parse(
  document.getElementById("missions-data").textContent
);

let feature = L.geoJSON(missions)
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
  .bindTooltip(function (layer) {
    return layer.feature.properties.slug;
  })
  .addTo(map);
try {
  map.fitBounds(feature.getBounds(), { padding: [100, 100] });
} catch (err) {
  console.log(err.message);
}

var bounds = L.control({ position: "bottomleft" });
bounds.onAdd = function (map) {
  var div = L.DomUtil.create("div", "bounds-container row");
  var bboxString = getMapBounds();
  div.innerHTML =
    '<div id="map-bounds">' +
    bboxString +
    "</div>" +
    "<div>&nbsp;" +
    '<input title="Use map bounds in Update" type="checkbox" id="use_bounds">' +
    "</div>";
  return div;
};
bounds.addTo(map);

function getMapBounds() {
  // Reduce precision from defaut 14 (!) to 4 digits
  var xmin = map.getBounds().toBBoxString().split(",")[0];
  var ymin = map.getBounds().toBBoxString().split(",")[1];
  var xmax = map.getBounds().toBBoxString().split(",")[2];
  var ymax = map.getBounds().toBBoxString().split(",")[3];
  xmin = Math.round(parseFloat(xmin) * 10000) / 10000;
  ymin = Math.round(parseFloat(ymin) * 10000) / 10000;
  xmax = Math.round(parseFloat(xmax) * 10000) / 10000;
  ymax = Math.round(parseFloat(ymax) * 10000) / 10000;
  var bboxString = xmin.toString() + "," + ymin.toString();
  bboxString += "," + xmax.toString() + "," + ymax.toString();
  // Add map bounds to form elements for next query
  document.getElementById("xmin").setAttribute("value", xmin);
  document.getElementById("xmax").setAttribute("value", xmax);
  document.getElementById("ymin").setAttribute("value", ymin);
  document.getElementById("ymax").setAttribute("value", ymax);
  return bboxString;
}

map.on("zoomend", function () {
  bboxString = getMapBounds();
  document.getElementById("map-bounds").innerHTML = bboxString;
});

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
