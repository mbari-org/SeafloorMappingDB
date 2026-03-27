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

/**
 * Shared: turn each CheckboxSelectMultiple fieldset (div_id_* with .form-check)
 * into a collapsible dark accordion. Used by home page (map.js) and Missions
 * page (map_mission_filter.js). Optional recalcCallback (e.g. recalcSidebarHeight)
 * is called after toggle to adjust sidebar height.
 * @param {HTMLElement} formEl - Form or container with [id^="div_id_"] divs
 * @param {function} [recalcCallback] - Called after open/close (setTimeout 50ms)
 */
function setupCheckboxDropdowns(formEl, recalcCallback) {
  if (!formEl) return;
  formEl.querySelectorAll('[id^="div_id_"]').forEach(function (outerDiv) {
    var checks = outerDiv.querySelectorAll(".form-check");
    if (checks.length === 0) return;

    var toggleEl = outerDiv.querySelector("legend") ||
                   outerDiv.querySelector("label.form-label");
    if (!toggleEl) return;

    var panel = checks[0].parentElement;
    if (!panel) return;

    if (toggleEl.dataset.dropdownInit) return;
    toggleEl.dataset.dropdownInit = "1";

    var TOGGLE_BG = "#1e1e1e";
    var TOGGLE_BORDER = "#555";

    toggleEl.style.cssText =
      "display:flex;justify-content:space-between;align-items:center;" +
      "width:100%;max-width:230px;padding:0.3rem;box-sizing:border-box;" +
      "background:" + TOGGLE_BG + ";border:1px solid " + TOGGLE_BORDER + ";" +
      "border-radius:4px;cursor:pointer;color:#e0e0e0;font-size:0.8rem;" +
      "margin-bottom:0;user-select:none;";

    var caret = document.createElement("span");
    caret.innerHTML = "&#8964;";
    caret.style.cssText =
      "font-size:0.9rem;font-weight:bold;line-height:1;" +
      "transition:transform 0.2s;flex-shrink:0;color:#e0e0e0;";
    toggleEl.appendChild(caret);

    toggleEl.addEventListener("mouseenter", function () {
      toggleEl.style.boxShadow =
        "inset 0 1px 1px rgba(0,0,0,0.075), 0 0 8px cornflowerblue";
    });
    toggleEl.addEventListener("mouseleave", function () {
      toggleEl.style.boxShadow = "none";
    });

    var fieldset = outerDiv.querySelector("fieldset");
    if (fieldset) {
      fieldset.style.cssText = "border:none;padding:0;margin:0;min-width:0;";
    }

    panel.style.cssText =
      "padding:0.15rem 0 0.15rem 10px;margin:0;" +
      "background:#2a2a2a;border:1px solid #555;border-top:none;" +
      "border-radius:0 0 4px 4px;";
    panel.querySelectorAll(".form-check").forEach(function (chk) {
      chk.style.marginBottom = "0";
      chk.style.paddingTop = "0.15rem";
      chk.style.paddingBottom = "0.15rem";
      chk.style.minHeight = "unset";
    });
    panel.querySelectorAll(".form-check-label").forEach(function (lbl) {
      lbl.style.color = "#e0e0e0";
      lbl.style.fontSize = "0.8rem";
      lbl.style.cursor = "pointer";
      lbl.style.margin = "0";
    });

    var hasChecked = !!panel.querySelector("input[type='checkbox']:checked");
    panel.style.display = hasChecked ? "block" : "none";
    if (hasChecked) caret.style.transform = "rotate(180deg)";

    toggleEl.addEventListener("click", function (e) {
      e.preventDefault();
      var open = panel.style.display !== "none";
      panel.style.display = open ? "none" : "block";
      caret.style.transform = open ? "" : "rotate(180deg)";
      // Recalc after layout so body.scrollHeight reflects collapsed/expanded content.
      if (typeof recalcCallback === "function") {
        var runRecalc = function () { recalcCallback(); };
        requestAnimationFrame(function () {
          requestAnimationFrame(runRecalc);
        });
        setTimeout(runRecalc, 120);
      }
    });
  });
}
