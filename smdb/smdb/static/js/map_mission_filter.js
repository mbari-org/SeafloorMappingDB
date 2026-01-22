const map = L.map("map_mission_filter");
const options = { minZoom: 1, maxZoom: 20 };

const gmrt = L.tileLayer.wms(
  "https://www.gmrt.org/services/mapserver/wms_merc?",
  {
    layers: "GMRT",
  }
);
gmrt.addTo(map);

const missions = JSON.parse(
  document.getElementById("missions-data").textContent
);

// Check if missions data is empty before creating GeoJSON layer
var hasMissions = missions && missions.features && missions.features.length > 0;

// Set initial view to default - will be adjusted in whenReady callback if valid missions exist
map.setView([39.8423, -26.8945], 3, { animate: false });

let feature = L.geoJSON(missions)
  .bindPopup(function (layer) {
    return (
      "<a target='_blank' href='/missions/" +
      layer.feature.properties.slug +
      "'>" +
      layer.feature.properties.slug +
      "</a>: " +
      layer.feature.properties.expedition.name +
      "<br>Route: " +
      layer.feature.properties.route_file
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
        console.log("No missions found - using default view");
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      
      // Double-check missions data structure
      if (!missions || !missions.features || missions.features.length === 0) {
        console.log("Missions data structure invalid - using default view");
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
      // Also check for extremely large spans that would cause excessive zoom-out
      if (missionLngSpan >= 360 || missionLatSpan >= 180 || isNaN(missionLatSpan) || isNaN(missionLngSpan) || 
          missionLngSpan > 350 || missionLatSpan > 170) {
        // Invalid or global-spanning bounds - set to default zoom level 3 and center
        map.setView([39.8423, -26.8945], 3, { animate: false });
        return;
      }
      
      // Additional check: ensure bounds are reasonable before fitting
      // If the span is still very large (e.g., > 180 degrees longitude), use default view
      if (Math.abs(missionLngSpan) > 180 || Math.abs(missionLatSpan) > 90) {
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
