/* Project specific Javascript goes here. */
function updateMap() {
  console.log("UpdateMap() called.");
  // See https://stackoverflow.com/a/41542008/1281657
  if ("URLSearchParams" in window) {
    var searchParams = new URLSearchParams(window.location.search);
    console.log("searchParams " + searchParams);
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
    if (document.getElementById("toggle").onclick) {
      toggle.Control.onClick();
    }
    if (document.getElementById("searchbar") != null) {
      //if (document.getElementById("searchbar").value) {
      searchParams.set("q", document.getElementById("searchbar").value);
    } else {
      searchParams.delete("q");
    }
  }
  window.location.search = searchParams.toString();
}

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

////////  ADD GEOMAN for LEAFLET  /////////
var toggle = L.easyButton({
  position: "topright",
  // id: "toggle",
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
