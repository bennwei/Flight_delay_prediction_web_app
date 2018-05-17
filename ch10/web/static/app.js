var width = 960,
    height = 500;

var y = d3.scale.linear()
    .range([height, 0]);
    // We define the domain once we get our data in d3.json, below

var chart = d3.select(".chart")
    .attr("width", width)
    .attr("height", height);

d3.json("/total_flights.json", function(data) {
  y.domain([0, d3.max(data, function(d) { return d.total_flights; })]);

  var barWidth = width / data.length;

  var bar = chart.selectAll("g")
      .data(data)
      .enter()
      .append("g")
      .attr("transform", function(d, i) { return "translate(" + i * barWidth + ",0)"; });

  bar.append("rect")
      .attr("y", function(d) { return y(d.total_flights); })
      .attr("height", function(d) { return height - y(d.total_flights); })
      .attr("width", barWidth - 1);

  bar.append("text")
      .attr("x", barWidth / 2)
      .attr("y", function(d) { return y(d.total_flights) + 3; })
      .attr("dy", ".75em")
      .text(function(d) { return d.total_flights; });
});