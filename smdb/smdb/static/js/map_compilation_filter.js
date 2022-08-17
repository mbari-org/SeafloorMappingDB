const map = L.map("map_compilation_filter");
const options = { minZoom: 1, maxZoom: 20 };

L.esri.basemapLayer("Oceans", options).addTo(map);
L.esri.basemapLayer("OceansLabels", options).addTo(map);

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
