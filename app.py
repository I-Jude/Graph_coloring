from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import itertools
import io
import base64

matplotlib.use('Agg')

app = Flask(__name__)

@app.context_processor
def utility_processor():
    return dict(chr=chr)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_matrix', methods=['POST'])
def get_matrix():
    num_vertices = int(request.form['num_vertices'])
    return render_template('matrix.html', num_vertices=num_vertices)

@app.route('/draw_graph_route', methods=['POST'])
def draw_graph_route():
    num_vertices = int(request.form['num_vertices'])
    try:
        matrix = [[int(request.form[f'cell_{i}_{j}']) for j in range(num_vertices)] for i in range(num_vertices)]
    except ValueError:
        return "Invalid input. Please enter integers only."

    G = nx.Graph()
    G.add_nodes_from(range(num_vertices))
    G.add_edges_from((i, j) for i in range(num_vertices) for j in range(num_vertices) if matrix[i][j] == 1)
    
    labels = {i: chr(65 + i) for i in range(num_vertices)}
    
    pos = nx.circular_layout(G)  # Fixed circular layout
    
    plt.figure(figsize=(6, 6))
    nx.draw(G, pos, labels=labels, with_labels=True, node_color='skyblue', node_size=700, edge_color='gray', font_color='black')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode('utf8')

    return render_template('graph.html', graph_url=graph_url, num_vertices=num_vertices, matrix=matrix)

def welsh_powell_vertex_coloring(G):
    coloring = {}
    nodes_sorted = sorted(G.nodes(), key=lambda node: G.degree(node), reverse=True)
    for node in nodes_sorted:
        used_colors = set(coloring.get(neigh, None) for neigh in G.neighbors(node))
        color = next(color for color in range(len(G)) if color not in used_colors)
        coloring[node] = color
    return coloring

@app.route('/find_chromatic_index', methods=['POST'])
def find_chromatic_index():
    try:
        num_vertices = int(request.form['num_vertices'])
        matrix = [[int(request.form[f'cell_{i}_{j}']) for j in range(num_vertices)] for i in range(num_vertices)]

        G = nx.Graph()
        G.add_nodes_from(range(num_vertices))
        G.add_edges_from((i, j) for i in range(num_vertices) for j in range(num_vertices) if matrix[i][j] == 1)

        vertex_coloring = welsh_powell_vertex_coloring(G)
        chromatic_index = max(vertex_coloring.values()) + 1

        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'orange', 'purple', 'pink', 'brown']

        pos = nx.circular_layout(G)  # Fixed circular layout

        def draw_graph(G, vertex_coloring, color_mapping, num_vertices):
            labels = {i: chr(65 + i) for i in range(num_vertices)}
            plt.figure(figsize=(6, 6))
            node_colors = [color_mapping[vertex_coloring[node]] for node in G.nodes()]
            nx.draw(G, pos, labels=labels, with_labels=True, node_color=node_colors, node_size=700, edge_color='gray', font_color='black')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()  # Close the plot to free up memory
            return base64.b64encode(buf.getvalue()).decode('utf8')

        color_combinations = list(itertools.permutations(colors[:chromatic_index]))

        graphs = []
        for color_mapping in color_combinations:
            color_mapping_dict = {i: color for i, color in enumerate(color_mapping)}
            graph_url = draw_graph(G, vertex_coloring, color_mapping_dict, num_vertices)
            graphs.append(graph_url)

        return render_template('chromatic_index.html', chromatic_index=chromatic_index, graphs=graphs)

    except Exception as e:
        print(f"Error: {e}")
        return str(e)


@app.route('/manual_color', methods=['GET'])
def manual_color():
    num_vertices = int(request.args['num_vertices'])
    matrix = [[int(request.args[f'cell_{i}_{j}']) for j in range(num_vertices)] for i in range(num_vertices)]
    return render_template('manual_color.html', num_vertices=num_vertices, matrix=matrix)


from math import ceil

@app.route('/manual_color_process', methods=['POST'])
def manual_color_process():
    try:
        num_vertices = int(request.form['num_vertices'])
        num_colors = int(request.form['num_colors'])
        matrix = [[int(request.form[f'cell_{i}_{j}']) for j in range(num_vertices)] for i in range(num_vertices)]

        G = nx.Graph()
        G.add_nodes_from(range(num_vertices))
        G.add_edges_from((i, j) for i in range(num_vertices) for j in range(num_vertices) if matrix[i][j] == 1)

        vertex_coloring = welsh_powell_vertex_coloring(G)
        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'orange', 'purple', 'pink', 'brown']

        pos = nx.circular_layout(G)  # Fixed circular layout

        def draw_graph(G, vertex_coloring, color_mapping, num_vertices):
            labels = {i: chr(65 + i) for i in range(num_vertices)}
            plt.figure(figsize=(6, 6))
            node_colors = [color_mapping[vertex_coloring[node]] for node in G.nodes()]
            nx.draw(G, pos, labels=labels, with_labels=True, node_color=node_colors, node_size=700, edge_color='gray', font_color='black')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()  # Close the plot to free up memory
            return base64.b64encode(buf.getvalue()).decode('utf8')

        # Limit the number of permutations displayed
        max_permutations = 10  # Adjust as needed
        color_combinations = list(itertools.permutations(colors[:num_colors], num_vertices))[:max_permutations]

        graphs = []
        for color_mapping in color_combinations:
            color_mapping_dict = {i: color for i, color in enumerate(color_mapping)}
            graph_url = draw_graph(G, vertex_coloring, color_mapping_dict, num_vertices)
            graphs.append(graph_url)

        # Pagination logic
        page = int(request.args.get('page', 1))
        per_page = 5  # Number of graphs per page
        total_pages = ceil(len(graphs) / per_page)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        # Slice graphs to display for the current page
        current_page_graphs = graphs[start_idx:end_idx]

        return render_template('manual_color_result.html', graphs=current_page_graphs, num_vertices=num_vertices, num_colors=num_colors, page=page, total_pages=total_pages)

    except Exception as e:
        print(f"Error: {e}")
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)