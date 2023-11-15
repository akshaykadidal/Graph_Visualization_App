import pickle
from flask import Flask, render_template, request, redirect, url_for, session, make_response
import networkx as nx
from pyvis.network import Network

app = Flask(__name__)

# Initialize the session
app.secret_key = "your_secret_key"

# Load the NetworkX graph from a pickle file
with open("Process_inventory_v1.pickle", "rb") as f:
    graph = pickle.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        selected_node = request.form["selected_node"]
        session["selected_node"] = selected_node
        #session["selected_node"] = 'NM1'
        return redirect(url_for("processes"))

    #nodes = list(graph.nodes())
    #nodes_to_isolate =  [node for node in graph.nodes if 'ntype' not in graph.nodes[node]]
    #graph.remove_nodes_from(nodes_to_isolate)
    nodes = [node for node in graph.nodes if graph.nodes[node]['ntype']=='PI_Elements']
    return render_template("index.html", nodes=nodes)

@app.route("/processes", methods=["GET", "POST"])
def processes():
    if request.method == "POST":
        selected_process = request.form["selected_process"]
        session["selected_process"] = selected_process
        return redirect(url_for("visualization"))

    selected_node = session.get("selected_node", None)
    if selected_node is not None:
        #nodes = [node for node in graph.nodes if graph.nodes[node]['ntype']!='Process']
        neighbors_all = list(graph.predecessors(selected_node))
        neighbors = [nod for nod in neighbors_all if graph.nodes[nod]['ntype']=="Process"]
        neighbors_with_description = [{node: graph.nodes[node]['description_english']} for node  in neighbors]
        neighbors_with_description = {key:value for d in neighbors_with_description for key, value in d.items()}
        #neighbors.extend(selected_node)
        return render_template("processes.html", neighbors= neighbors, neighbors_with_description=neighbors_with_description, selected_node=selected_node)
        #return render_template("processes.html", neighbors=neighbors)

    #return redirect(url_for("index"))
    return redirect(url_for("index"))

@app.route("/visualization", methods=["GET"])
def visualization():
    #selected_node = session.get("selected_node", None)
    selected_process = session.get("selected_process", None)
    #selected_process = request.args.get("selected_process", None)
    #selected_process.extend(selected_node)

    if selected_process is not None:
        l = list(graph.neighbors(int(selected_process)))
        # l = list(graph.neighbors(1231))
        # l.append(1231)
        l.append(int(selected_process))
        subgraph = graph.subgraph(l)
        nt = Network(notebook=True, cdn_resources='in_line',directed =True, filter_menu=True)
        nt.show_buttons()
        nt.from_nx(subgraph)
        # nt.set_options('CAL Asset', layout='circular')
        html = nt.generate_html().encode('utf-8')
        #html = html.decode("utf-8")
        response = make_response(html)
        #response = make_response(render_template('visualization.html', content=html))
        # response.content_type = 'text/html'

        #with open("PIEN.html", mode='w', encoding='utf-8') as fp:
        #    fp.write(html)
        # return render_template('visualization.html', graph_html=response)
        #html =  open("PIEN.html", "r")     
        # return render_template('visualization.html', graph_html=response)
        return(response)
        #return render_template("visualization.html", network=network.get_edge_data())


    return redirect(url_for("processes"))

@app.route("/restart", methods=["GET"])
def restart():
    session.pop("selected_node", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
