/* Project specific Javascript goes here. */
// include map.js

function updateMap() {
  // See https://stackoverflow.com/a/41542008/1281657
  if ("URLSearchParams" in window) {
    var searchParams = new URLSearchParams(window.location.search);
    try {
      if (document.getElementById("use_bounds").checked) {
        searchParams.set("xmin", document.getElementById("xmin").value);
        searchParams.set("xmax", document.getElementById("xmax").value);
        searchParams.set("ymin", document.getElementById("ymin").value);
        searchParams.set("ymax", document.getElementById("ymax").value);
      } else {
        searchParams.delete("xmin");
        searchParams.delete("xmax");
        searchParams.delete("ymin");
        searchParams.delete("ymax");
      }
      if (document.getElementById("use_time").checked) {
        searchParams.set("tmin", document.getElementById("tmin").value);
        searchParams.set("tmax", document.getElementById("tmax").value);
      } else {
        searchParams.delete("tmin");
        searchParams.delete("tmax");
      }
    } catch (err) {
      // Catch degenerate case when checkboxes aren't on the page and continue
      console.log(err.message);
    }
    // Try and incorporate with updateMap() - Easy Button
    if ((toggle = "remove-geoman")) {
      console.log("This works.");
    }
    if ((toggle.stateName = "add-geoman")) {
      console.log("Geoman is currently closed.");
      toggle.stateName = "remove-geoman";
    } else if ((toggle.stateName = "remove-geoman")) {
      console.log("Geoman is currently open.");
      toggle.stateName = "add-geoman";
    }

    if (document.getElementById("searchbar") != null) {
      //if (document.getElementById("searchbar").value) {
      searchParams.set("q", document.getElementById("searchbar").value);
    } else {
      searchParams.delete("q");
    }
  }
  //var url = searchParams.toString();
  window.location.search = searchParams.toString();
}

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
        // Push layer to active array
        active.push(obj.layer);
      }
    });
    return active;
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
