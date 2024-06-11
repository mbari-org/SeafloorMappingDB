/* https://stackoverflow.com/a/33181806/1281657 and http://jsfiddle.net/nathansnider/mos9Lr5v/ */
L.Control.SliderControl = L.Control.extend({
  options: {
    position: "topright",
    layers: null,
    startTimeAttribute: "start_time",
    endTimeAttribute: "end_time",
    isEpoch: false, // whether the time attribute is seconds elapsed from epoch
    startTimeIdx: 0, // where to start looking for a timestring
    timeStrLength: 19, // the size of  yyyy-mm-dd hh:mm:ss - if millis are present this will be larger
    maxValue: -1,
    minValue: 0,
    showAllOnStart: false,
    markers: null,
    range: false,
    follow: false,
    alwaysShowDate: false,
    rezoom: null,
  },

  initialize: function (options) {
    L.Util.setOptions(this, options);
    this._layer = this.options.layer;
  },

  extractTimestamp: function (time, options) {
    if (options.isEpoch) {
      //time = new Date(parseInt(time)).toUTCShortFormat();  // not a function ?
      time = new Date(parseInt(time)).toISOString();
    }
    return time.substr(
      options.startTimeIdx,
      options.startTimeIdx + options.timeStrLength
    );
  },

  setSliderMarks: function (layers, minIndx, maxIndx) {
    var min_ems, max_ems;
    // Add marker tics to range slider
    if (layers[minIndx].feature.properties !== undefined) {
      min_ems =
        layers[minIndx].feature.properties[this.options.startTimeAttribute];
    } else {
      console.error("TypeError Reading properties.");
    }
    if (layers[maxIndx].feature !== undefined) {
      max_ems =
        layers[maxIndx].feature.properties[this.options.endTimeAttribute];
    } else {
      console.error("TypeError Reading properties.");
    }
    this._layer.eachLayer(function (layer) {
      if (layer !== undefined) {
        s_frac =
          (layer.feature.properties.start_ems - min_ems) / (max_ems - min_ems);
        e_frac =
          (layer.feature.properties.end_ems - min_ems) / (max_ems - min_ems);
        // TODO: Add marks to the slider
      }
    });
  },

  setPosition: function (position) {
    var map = this._map;

    if (map) {
      map.removeControl(this);
    }

    this.options.position = position;

    if (map) {
      map.addControl(this);
    }
    this.startSlider();
    return this;
  },

  onAdd: function (map) {
    this.options.map = map;

    // Create a control sliderContainer with a jquery ui slider
    var sliderContainer = L.DomUtil.create("div", "slider", this._container);
    $(sliderContainer).append(
      '<div class="row">' +
        '  <div class="col-12">' +
        '    <div id="leaflet-slider" style="inline-block; margin: 0 5px 0 5px;"></div>' +
        "  </div>" +
        "</div>" +
        '<div class="row" id="slider-row">' +
        '  <div class="col-2" id="slider-min-row">' +
        '    <div id="slider-min" style="color: darkblue;"></div>' +
        "  </div>" +
        '  <div class="col-8" id="slider-current-row">' +
        '    <div id="slider-current" style="text-align: center;">' +
        '      <span class="start-time"></span> to <span class="end-time"></span>' +
        '      <input title="Use time bounds in Update" type="checkbox" id="use_time" onclick="getSliderStatus()">' +
        "    </div>" +
        "  </div>" +
        '  <div class="col-2" id="slider-max-row">' +
        '    <div id="slider-max" style="text-align: right; color: darkblue;"></div>' +
        "  </div>" +
        "</div>"
    );
    //Prevent map panning/zooming while using the slider
    $(sliderContainer).mousedown(function () {
      map.dragging.disable();
    });

    $(document).mouseup(function () {
      map.dragging.enable();
      //Hide the slider timestamp if not range and option alwaysShowDate is set on false
      if (options.range || !options.alwaysShowDate) {
        $("#slider-timestamp").html("");
      }
    });

    var options = this.options;
    this.options.markers = [];

    //If a layer has been provided: calculate the min and max values for the slider
    if (this._layer) {
      var index_temp = 0;
      this._layer.eachLayer(function (layer) {
        options.markers[index_temp] = layer;
        ++index_temp;
      });
      options.maxValue = index_temp - 1;
      this.options = options;
      // Add tics to slider
      this.setSliderMarks(options.markers, options.minValue, options.maxValue);
    } else {
      console.log(
        "Error: You have to specify a layer via new SliderControl({layer: your_layer});"
      );
    }
    $("#slider-min", sliderContainer).html(
      this.extractTimestamp(
        this.options.markers[this.options.minValue].feature.properties[
          this.options.startTimeAttribute
        ],
        this.options
      )
    );
    $("#slider-max", sliderContainer).html(
      this.extractTimestamp(
        this.options.markers[this.options.maxValue].feature.properties[
          this.options.startTimeAttribute
        ],
        this.options
      )
    );
    this.$currentStartDiv = $("#slider-current .start-time", sliderContainer);
    this.$currentEndDiv = $("#slider-current .end-time", sliderContainer);
    this._updateCurrentDiv(0, this.options.maxValue);

    return sliderContainer;
  },
  _updateCurrentDiv: function (startIdx, endIdx) {
    var min_date = this.extractTimestamp(
      this.options.markers[startIdx].feature.properties[
        this.options.startTimeAttribute
      ],
      this.options
    );
    var max_date = this.extractTimestamp(
      this.options.markers[endIdx].feature.properties[
        this.options.endTimeAttribute
      ],
      this.options
    );
    this.$currentStartDiv.html(min_date);
    this.$currentEndDiv.html(max_date);
    // Add to hidden form elements
    $("#tmin").attr("value", min_date);
    $("#tmax").attr("value", max_date);
    $("#num-missions").html(endIdx - startIdx + 1);
    // Also add map bounds for when zoom event doesn't update them
    var xmin = map.getBounds().toBBoxString().split(",")[0];
    var ymin = map.getBounds().toBBoxString().split(",")[1];
    var xmax = map.getBounds().toBBoxString().split(",")[2];
    var ymax = map.getBounds().toBBoxString().split(",")[3];
    // Reduce precision from defaut 14 (!) to 4 digits
    xmin = Math.round(parseFloat(xmin) * 10000) / 10000;
    ymin = Math.round(parseFloat(ymin) * 10000) / 10000;
    xmax = Math.round(parseFloat(xmax) * 10000) / 10000;
    ymax = Math.round(parseFloat(ymax) * 10000) / 10000;
    document.getElementById("xmin").setAttribute("value", xmin);
    document.getElementById("xmax").setAttribute("value", xmax);
    document.getElementById("ymin").setAttribute("value", ymin);
    document.getElementById("ymax").setAttribute("value", ymax);
  },
  onRemove: function (map) {
    //Delete all markers which where added via the slider and remove the slider div
    for (i = this.options.minValue; i < this.options.maxValue; i++) {
      map.removeLayer(this.options.markers[i]);
    }
    $("#leaflet-slider").remove();
  },

  startSlider: function () {
    self = this;
    _options = this.options;
    _extractTimestamp = this.extractTimestamp;
    var index_start = _options.minValue;
    if (_options.showAllOnStart) {
      index_start = _options.maxValue;
      if (_options.range)
        _options.values = [_options.minValue, _options.maxValue];
      else _options.value = _options.maxValue;
    }
    $("#leaflet-slider").slider({
      range: _options.range,
      value: _options.value,
      values: _options.values,
      min: _options.minValue,
      max: _options.maxValue,
      step: 1,
      slide: function (e, ui) {
        var map = _options.map;
        var fg = L.featureGroup();
        var timeAttribute;
        if ($(ui.handle).index() == 1) {
          timeAttribute = _options.startTimeAttribute;
        } else if ($(ui.handle).index() == 2) {
          timeAttribute = _options.endTimeAttribute;
        }
        if (!!_options.markers[ui.value]) {
          // If there is no time property, this line has to be removed (or exchanged with a different property)
          if (_options.markers[ui.value].feature !== undefined) {
            if (_options.markers[ui.value].feature.properties[timeAttribute]) {
              if (_options.markers[ui.value])
                $("#slider-timestamp").html(
                  _extractTimestamp(
                    _options.markers[ui.value].feature.properties[
                      timeAttribute
                    ],
                    _options
                  )
                );
            } else {
              console.error(
                "Time property " + timeAttribute + " not found in data"
              );
            }
          } else {
            // set by leaflet Vector Layers
            if (_options.markers[ui.value].options[timeAttribute]) {
              if (_options.markers[ui.value])
                $("#slider-timestamp").html(
                  _extractTimestamp(
                    _options.markers[ui.value].options[timeAttribute],
                    _options
                  )
                );
            } else {
              console.error(
                "Time property " + timeAttribute + " not found in data"
              );
            }
          }

          var i;
          // clear markers
          for (i = _options.minValue; i <= _options.maxValue; i++) {
            if (_options.markers[i]) map.removeLayer(_options.markers[i]);
          }
          if (_options.range) {
            // jquery ui using range
            for (i = ui.values[0]; i <= ui.values[1]; i++) {
              if (_options.markers[i]) {
                map.addLayer(_options.markers[i]);
                fg.addLayer(_options.markers[i]);
              }
            }
            self._updateCurrentDiv(ui.values[0], ui.values[1]);
          } else if (_options.follow) {
            for (i = ui.value - _options.follow + 1; i <= ui.value; i++) {
              if (_options.markers[i]) {
                map.addLayer(_options.markers[i]);
                fg.addLayer(_options.markers[i]);
              }
            }
          } else {
            for (i = _options.minValue; i <= ui.value; i++) {
              if (_options.markers[i]) {
                map.addLayer(_options.markers[i]);
                fg.addLayer(_options.markers[i]);
              }
            }
          }
        }
        if (_options.rezoom) {
          map.fitBounds(fg.getBounds(), {
            maxZoom: _options.rezoom,
          });
        }
      },
    });
    if (!_options.range && _options.alwaysShowDate) {
      $("#slider-timestamp").html(
        _extractTimeStamp(
          _options.markers[index_start].feature.properties[
            _options.startTimeAttribute
          ],
          _options
        )
      );
    }
    for (i = _options.minValue; i <= index_start; i++) {
      _options.map.addLayer(_options.markers[i]);
    }
  },
});

L.control.sliderControl = function (options) {
  return new L.Control.SliderControl(options);
};
