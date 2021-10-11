const attribution =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const map = L.map("map");
const media_url = JSON.parse(document.getElementById("MEDIA-URL").textContent);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: attribution,
}).addTo(map);
map.fitWorld();
const missions = JSON.parse(
  document.getElementById("missions-data").textContent
);

let feature = L.geoJSON(missions)
  .bindPopup(
    function (layer) {
      return (
        "<a target='_blank' href='/missions/" +
        layer.feature.properties.slug +
        "'>" +
        "<img src='" +
        layer.feature.properties.thumbnail_image +
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
map.fitBounds(feature.getBounds(), { padding: [100, 100] });
map.on("zoomend", function () {
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
  document.getElementById("map_bounds").innerHTML = bboxString;
  // Remove any time constraints following zoom event
  $("#tmin").removeAttr("value");
  $("#tmax").removeAttr("value");
});

var sliderControl = L.control.sliderControl({
  position: "topright",
  isEpoch: true,
  timeAttribute: "start_ems",
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
