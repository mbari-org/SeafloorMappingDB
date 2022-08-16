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
