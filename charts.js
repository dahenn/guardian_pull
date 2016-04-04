/******************CHART********************/
var margin = {top: 20, right: 20, bottom: 30, left: 40},
    chartwidth = 1200 - margin.left - margin.right,
    chartheight = 600 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, chartwidth], .15);

var y = d3.scale.linear()
    .rangeRound([chartheight, 0]);

var color = d3.scale.ordinal()
    .range(["rgba(255,255,255,0.7)", "rgba(255,255,255,0.2)", "rgba(255,255,255,0.4)"]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(d3.format(".2s"));

var chartsvg = d3.select("div.chart1").append("svg")
    .attr("width", chartwidth + margin.left + margin.right)
    .attr("height", chartheight + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.csv("chart1.csv", function(error, data) {
  if (error) throw error;

  color.domain(d3.keys(data[0]).filter(function(key) { return key !== "race"; }));

  data.forEach(function(d) {
    var y0 = 0;
    d.deaths = color.domain().map(function(name) { return {name: name, y0: y0, y1: y0 += +d[name]}; });
    d.total = d.deaths[d.deaths.length - 1].y1;
  });

  data.sort(function(a, b) { return b.total - a.total; });

  x.domain(data.map(function(d) { return d.race; }));
  y.domain([0, 10]);

  chartsvg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + chartheight + ")")
      .call(xAxis);

  chartsvg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Deaths per Million");

  var state = chartsvg.selectAll(".population")
      .data(data)
    .enter().append("g")
      .attr("class", "g")
      .attr("transform", function(d) { return "translate(" + x(d.race) + ",0)"; });

  state.selectAll("rect")
      .data(function(d) { return d.deaths; })
    .enter().append("rect")
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.y1); })
      .attr("height", function(d) { return y(d.y0) - y(d.y1); })
      .style("fill", function(d) { return color(d.name); });

  state.selectAll('text')
      .data(function(d) {return d.deaths; })
    .enter().append('text')
      .attr('x', x.rangeBand()/2)
      .attr("y", function(d, i) { return y(d.y1) + (y(d.y0) - y(d.y1))/2; })
      .style('text-anchor', 'middle')
      .text(function(d) { return (d.y1 - d.y0).toFixed(2); });

  var legend = chartsvg.selectAll(".legend")
      .data(color.domain().slice().reverse())
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
      .attr("x", chartwidth - 18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color);

  legend.append("text")
      .attr("x", chartwidth - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .attr('class', function(d) { return d; })
      .style("text-anchor", "end")
      .text(function(d) { return d; });

});


/******************MAPPING******************/
var width = 1400,
    height = 700;

var projection = d3.geo.albersUsa()
    .translate([width / 2, height / 2])
    .scale(1500);

var zoom = d3.behavior.zoom()
    .scaleExtent([1, 12])
    .on("zoom", zoomed);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("div.map").append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr('class', 'map')
  .append("g");

var g = svg.append("g");

svg.append("rect")
    .attr("class", "overlay")
    .attr("width", width)
    .attr("height", height);

svg
    .call(zoom)
    .call(zoom.event);

d3.json("states.json", function(error, UnitedStates) {
  if (error) throw error;

  var states = UnitedStates.features

  for (var i = 0; i < states.length; i++) {
  g.append("path")
      .datum(states[i])
      .attr('class', function(d) {return 'state ' + d.properties.name; })
      .attr("d", path);
  }

  d3.json("event_points.json", function(error, events) {
    if (error) return console.error(error);

  for (var i = 0; i < events.length; i++) {
    g.append('circle')
      .datum(events[i])
      .attr('id', function(d) {return d['race']; })
      .attr('class', function(d) {return 'event ' + d['date_index'] + " " + d['armed']; })
      .attr('r', 1.5)
      .attr("transform", function(d) {return "translate(" + projection([d["long"],d["lat"]]) + ")";})
    .append('title')
      .text(function(d) {return d['race'] + " " + d['sex'] + ", Armed: " + d['armed']; });
  }

  });

});

function zoomed() {
  g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

d3.select(self.frameElement).style("height", height + "px");

/******************* PIE 1 *******************/

var pie1width = 275,
    pie1height = 275,
    pie1radius = Math.min(pie1width, pie1height) / 2;

var pie1color = d3.scale.ordinal()
    .range(["#4e44d0", "#ab0101", "#e18a24"]);

var pie1arc = d3.svg.arc()
    .outerRadius(pie1radius - 0)
    .innerRadius(0);

var pie1labelArc = d3.svg.arc()
    .outerRadius(pie1radius - 40)
    .innerRadius(pie1radius - 40);

var pie1 = d3.layout.pie()
    .sort(null)
    .value(function(d) { return d.pct; });

var pie1svg = d3.select("#pie1").append("svg")
    .attr("width", pie1width)
    .attr("height", pie1height)
    .attr('style','margin-top:25px;')
  .append("g")
    .attr("transform", "translate(" + pie1width / 2 + "," + pie1height / 2 + ")");

d3.csv("data/pie1.csv", type, function(error, data) {
  if (error) throw error;

  var g = pie1svg.selectAll(".arc")
      .data(pie1(data))
    .enter().append("g")
      .attr("class", "arc");

  g.append("path")
      .attr("d", pie1arc)
      .style("fill", function(d) { return pie1color(d.data.pct); });

  g.append("text")
      .attr("transform", function(d) { return "translate(" + pie2labelArc.centroid(d) +")"; })
      .attr("dy", ".35em")
      .attr('text-anchor','middle')
      .attr('class', function(d) { return (d.data.pct*100).toFixed(0); })
      .text(function(d) { return (d.data.pct*100).toFixed(1) + "%"; });

  d3.select("span.killed")
      .data(data)
    .text(function(d) { return d.All; });

  d3.selectAll("span.totals")
      .data(data)
    .text(function(d) { return d.Total; });

});

function type(d) {
  d.race_cat = +d.race_cat;
  return d;
}

/******************* PIE 2 *******************/

var pie2width = 225,
    pie2height = 225,
    pie2radius = Math.min(pie2width, pie2height) / 2;

var pie2color = d3.scale.ordinal()
    .range(["#4e44d0", "#ab0101", "#e18a24"]);

var pie2arc = d3.svg.arc()
    .outerRadius(pie2radius - 10)
    .innerRadius(0);

var pie2labelArc = d3.svg.arc()
    .outerRadius(pie2radius - 40)
    .innerRadius(pie2radius - 40);

var pie2 = d3.layout.pie()
    .sort(null)
    .value(function(d) { return d.pct; });

var pie2svg = d3.select("#pie2").append("svg")
    .attr("width", pie2width)
    .attr("height", pie2height)
    .attr("style", "margin:" + ((275 - pie2width)/2) + "px; margin-top:" + (25 + (275 - pie2width)/2) + "px;")
  .append("g")
    .attr("transform", "translate(" + pie2width / 2 + "," + pie2height / 2 + ")");

d3.csv("data/pie2.csv", type, function(error, data) {
  if (error) throw error;

  var g = pie2svg.selectAll(".arc")
      .data(pie2(data))
    .enter().append("g")
      .attr("class", "arc");

  g.append("path")
      .attr("d", pie2arc)
      .style("fill", function(d) { return pie2color(d.data.pct); });

  g.append("text")
      .attr("transform", function(d) { return "translate(" + pie2labelArc.centroid(d) +")"; })
      .attr("dy", ".35em")
      .attr('text-anchor','middle')
      .attr('class', function(d) { return (d.data.pct*100).toFixed(0); })
      .text(function(d) { return (d.data.pct*100).toFixed(1) + "%"; });

  d3.select("span.unarmed-total")
      .data(data)
    .text(function(d) { return d.All; });

  d3.selectAll("span.unarmed")
      .data(data)
    .text(function(d) { return d.Total; });
});

function type(d) {
  d.race = +d.race;
  return d;
}

/******************* PIE 3 *******************/

var pie3width = 225,
    pie3height = 225,
    pie3radius = Math.min(pie3width, pie3height) / 2;

var pie3color = d3.scale.ordinal()
    .range(["#4e44d0", "#ab0101", "#e18a24"]);

var pie3arc = d3.svg.arc()
    .outerRadius(pie3radius - 10)
    .innerRadius(0);

var pie3labelArc = d3.svg.arc()
    .outerRadius(pie3radius - 40)
    .innerRadius(pie3radius - 40);

var pie3 = d3.layout.pie()
    .sort(null)
    .value(function(d) { return d.pct; });

var pie3svg = d3.select("#pie3").append("svg")
    .attr("width", pie3width)
    .attr("height", pie3height)
    .attr("style", "margin:" + ((275 - pie3width)/2) + "px; margin-top:" + (25 + (275 - pie3width)/2) + "px;")
  .append("g")
    .attr("transform", "translate(" + pie3width / 2 + "," + pie3height / 2 + ")");

d3.csv("data/pie3.csv", type, function(error, data) {
  if (error) throw error;

  var g = pie3svg.selectAll(".arc")
      .data(pie3(data))
    .enter().append("g")
      .attr("class", "arc");

  g.append("path")
      .attr("d", pie3arc)
      .style("fill", function(d) { return pie3color(d.data.pct); });

  g.append("text")
      .attr("transform", function(d) { return "translate(" + pie3labelArc.centroid(d) +")"; })
      .attr("dy", ".35em")
      .attr('text-anchor','middle')
      .attr('class', function(d) { return (d.data.pct*100).toFixed(0); })
      .text(function(d) { return (d.data.pct*100).toFixed(1) + "%"; });

  d3.select("span.armed-total")
      .data(data)
    .text(function(d) { return d.All; });

  d3.selectAll("span.armed")
      .data(data)
    .text(function(d) { return d.Total; });
});

function type(d) {
  d.race = +d.race;
  return d;
}

/******************* PIE 4 *******************/

var pie4width = 275,
    pie4height = 275,
    pie4radius = Math.min(pie4width, pie4height) / 2;

var pie4color = d3.scale.ordinal()
    .range(["#4e44d0", "#ab0101", "#e18a24"]);

var pie4arc = d3.svg.arc()
    .outerRadius(pie4radius - 10)
    .innerRadius(0);

var pie4labelArc = d3.svg.arc()
    .outerRadius(pie4radius - 40)
    .innerRadius(pie4radius - 40);

var pie4 = d3.layout.pie()
    .sort(null)
    .value(function(d) { return d.pct; });

var pie4svg = d3.select("#pie4").append("svg")
    .attr("width", pie4width)
    .attr("height", pie4height)
    .attr("style", "margin:" + ((275 - pie4width)/2) + "px; margin-top:" + (25 + (275 - pie4width)/2) + "px;")
  .append("g")
    .attr("transform", "translate(" + pie4width / 2 + "," + pie4height / 2 + ")");

d3.csv("data/pie4.csv", type, function(error, data) {
  if (error) throw error;

  var g = pie4svg.selectAll(".arc")
      .data(pie4(data))
    .enter().append("g")
      .attr("class", "arc");

  g.append("path")
      .attr("d", pie4arc)
      .style("fill", function(d) { return pie4color(d.data.pct); });

  g.append("text")
      .attr("transform", function(d) { return "translate(" + pie4labelArc.centroid(d) +")"; })
      .attr("dy", ".35em")
      .attr('text-anchor','middle')
      .attr('class', function(d) { return (d.data.pct*100).toFixed(0); })
      .text(function(d) { return (d.data.pct*100).toFixed(1) + "%"; });

  d3.selectAll("span.demo")
      .data(data)
    .text(function(d) { return (d.pop_mil*1).toFixed(0) + "M"; });
});

function type(d) {
  d.race = +d.race;
  return d;
}
