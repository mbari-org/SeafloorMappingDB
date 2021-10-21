/* Project specific Javascript goes here. */
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
    if (document.getElementById("searchbar").value) {
      searchParams.set("q", document.getElementById("searchbar").value);
    } else {
      searchParams.delete("q");
    }
  }
  window.location.search = searchParams.toString();
}
