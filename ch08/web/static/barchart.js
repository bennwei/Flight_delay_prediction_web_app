class BarChart {

    constructor(url, labelName, valueName, chartClassName) {
        this.url = url;
        this.labelName = (typeof labelName !== 'undefined') ? labelName : 'label';
        this.valueName = (typeof valueName !== 'undefined') ? valueName : 'value';
        this.chartClassName = (typeof chartClassName !== 'undefined') ? chartClassName : 'chart';
    }

    render() {
        var margin = {top: 20, right: 30, bottom: 30, left: 40},
            width = 900 - margin.left - margin.right,
            height = 300 - margin.top - margin.bottom;

        var x = d3.scale.ordinal()
            .rangeRoundBands([0, width], .1);
        var y = d3.scale.linear()
            .range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickFormat(function(d) {
                return truncate(d, 14);
            });
        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var chart = d3.select('.' + this.chartClassName)
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var labelName = this.labelName;
        var valueName = this.valueName;
        d3.json(this.url, function(error, data) {
            var data = data.data;

            x.domain(data.map(function(d) { return d[labelName]; }));
            y.domain([0, d3.max(data, function(d) { return d[valueName]; })]);

            chart.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            chart.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            chart.selectAll(".bar")
                .data(data)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function(d) { return x(d[labelName]); })
                .attr("y", function(d) { return y(d[valueName]); })
                .attr("height", function(d) { return height - y(d[valueName]); })
                .attr("width", x.rangeBand());
        });

        function truncate(d, l) {
             if(d.length > l)
                 return d.substring(0,l)+'...';
             else
                 return d;
        }
    }
}
