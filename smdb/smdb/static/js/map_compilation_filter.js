const map = L.map("map_compilation_filter");
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

// Check if missions data is empty before creating GeoJSON layer
var hasMissions = missions && missions.features && missions.features.length > 0;

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

// Fit map to mission bounds with checks for empty missions (same logic as home page)
map.whenReady(function() {
  map.invalidateSize();
  
  setTimeout(function() {
    try {
      // Check if there are any missions before trying to fit bounds
      if (!hasMissions) {
        // No missions found - set to default zoom level 3 and center
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      
      // Also check the feature layers as a secondary check
      var featureLayers = feature.getLayers();
      if (!featureLayers || featureLayers.length === 0) {
        // No missions found - set to default zoom level 3 and center
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      
      // Try to get bounds - this may throw an error if layer is empty
      var bounds;
      try {
        bounds = feature.getBounds();
      } catch (boundsError) {
        // getBounds() failed (likely empty layer) - set to default zoom level 3 and center
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      
      if (!bounds || !bounds.isValid || !bounds.isValid()) {
        // Invalid bounds (likely empty layer) - set to default zoom level 3 and center
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      
      // Get mission bounds coordinates
      var sw = bounds.getSouthWest();
      var ne = bounds.getNorthEast();
      var missionLatSpan = ne.lat - sw.lat;
      var missionLngSpan = ne.lng - sw.lng;
      
      // Check if bounds span is too large (indicating invalid/empty bounds or global span)
      if (missionLngSpan >= 360 || missionLatSpan >= 180 || isNaN(missionLatSpan) || isNaN(missionLngSpan)) {
        // Invalid or global-spanning bounds - set to default zoom level 3 and center
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      
      // Valid bounds - fit to bounds with padding
      map.fitBounds(bounds, { padding: [100, 100] });
    } catch (err) {
      console.log(err.message);
      // On any error, set to default zoom level 3 and center
      map.setView([39.8423, -26.8945], 3, { animate: false });
    }
  }, 100);
});

// Only create markers if there are missions
if (hasMissions && missions.features) {
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
}
