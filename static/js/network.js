var container = document.getElementById("mynetwork");
var data = {{ graph_data|tojson|safe }};
var options = {};

var network = new vis.Network(container, data, options);
