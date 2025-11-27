from flask import Flask, render_template, jsonify
import networkx as nx
import math
import os

app = Flask(__name__)

class TransportSystem:
    def __init__(self):
        self.G = nx.DiGraph()
        self.setup_network()
    
    def setup_network(self):
        # Coordonnées réelles de Kinshasa
        locations = {
            'RP_VICTOIRE': {
                'nom': 'Rond-Point Victoire', 
                'lat': -4.3006, 
                'lon': 15.2981,
                'type': 'depart'
            },
            'MARCHE_CENTRAL': {
                'nom': 'Marché Central', 
                'lat': -4.3036, 
                'lon': 15.3028,
                'type': 'intermediaire'
            },
            'GARE_CENTRALE': {
                'nom': 'Gare Centrale', 
                'lat': -4.3214, 
                'lon': 15.3225,
                'type': 'arrivee'
            }
        }
        
        for node_id, info in locations.items():
            self.G.add_node(node_id, **info)
        
        # Routes avec distances fixes (pas besoin de NumPy)
        routes = [
            ('RP_VICTOIRE', 'MARCHE_CENTRAL', 1.2, 5, 'Avenue de la Justice'),
            ('MARCHE_CENTRAL', 'GARE_CENTRALE', 1.3, 6, 'Route Directe')
        ]
        
        for dep, arr, distance, temps, nom_route in routes:
            self.G.add_edge(
                dep, arr, 
                distance=distance,
                temps=temps,
                nom_route=nom_route
            )
    
    def get_shortest_path(self, start, end):
        try:
            path = nx.shortest_path(self.G, start, end, weight='distance')
            total_distance = sum(self.G[path[i]][path[i+1]]['distance'] for i in range(len(path)-1))
            total_time = sum(self.G[path[i]][path[i+1]]['temps'] for i in range(len(path)-1))
            
            steps = []
            path_coords = []
            
            for i in range(len(path)-1):
                dep = path[i]
                arr = path[i+1]
                edge_data = self.G[dep][arr]
                
                steps.append({
                    'from': self.G.nodes[dep]['nom'],
                    'to': self.G.nodes[arr]['nom'],
                    'distance': edge_data['distance'],
                    'time': edge_data['temps'],
                    'route': edge_data['nom_route']
                })
                
                # Coordonnées pour la carte
                path_coords.append([
                    [self.G.nodes[dep]['lon'], self.G.nodes[dep]['lat']],
                    [self.G.nodes[arr]['lon'], self.G.nodes[arr]['lat']]
                ])
            
            return {
                'path': [self.G.nodes[node]['nom'] for node in path],
                'total_distance': total_distance,
                'total_time': total_time,
                'steps': steps,
                'path_coords': path_coords
            }
        except:
            return None

transport = TransportSystem()

@app.route('/')
def index():
    return render_template('index_unifie.html')

@app.route('/api/network')
def get_network():
    nodes = []
    for node_id in transport.G.nodes():
        node_data = transport.G.nodes[node_id]
        nodes.append({
            'id': node_id,
            'name': node_data['nom'],
            'lat': node_data['lat'],
            'lon': node_data['lon'],
            'type': node_data['type']
        })
    
    edges = []
    for u, v in transport.G.edges():
        edge_data = transport.G[u][v]
        edges.append({
            'from': u,
            'to': v,
            'distance': edge_data['distance'],
            'time': edge_data['temps'],
            'route': edge_data['nom_route']
        })
    
    return jsonify({'nodes': nodes, 'edges': edges})

@app.route('/api/shortest-path')
def shortest_path():
    result = transport.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE')
    return jsonify(result or {"error": "No path found"})

@app.route('/health')
def health():
    return jsonify({"status": "OK", "message": "Transport Kinshasa operational"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)