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
        layer.feature.properties.name +
        "<br>" +
        "<img src='" +
        media_url +
        layer.feature.properties.thumbnail_image +
        "' />"
      );
    },
    {
      maxWidth: "600px",
    }
  )
  .addTo(map);
map.fitBounds(feature.getBounds(), { padding: [100, 100] });
