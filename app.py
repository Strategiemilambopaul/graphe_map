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
        # COORDONNÉES RÉELLES DE KINSHASA - TOUS LES ARRÊTS
        locations = {
            'RP_VICTOIRE': {
                'nom': 'Rond-Point Victoire', 
                'lat': -4.300722, 
                'lon': 15.298056,
                'type': 'depart'
            },
            'PLACE_VICTOIRE': {
                'nom': 'Place de la Victoire', 
                'lat': -4.302500, 
                'lon': 15.300833,
                'type': 'intermediaire'
            },
            'MARCHE_CENTRAL': {
                'nom': 'Marché Central', 
                'lat': -4.303889, 
                'lon': 15.302778,
                'type': 'intermediaire'
            },
            'AVENUE_COMMERCE': {
                'nom': 'Avenue du Commerce', 
                'lat': -4.305556, 
                'lon': 15.305000,
                'type': 'intermediaire'
            },
            'STADE_MAYAMA': {
                'nom': 'Stade Mayama', 
                'lat': -4.308333, 
                'lon': 15.308611,
                'type': 'intermediaire'
            },
            'CARREFOUR_TSHENUKA': {
                'nom': 'Carrefour Tshénuka', 
                'lat': -4.311944, 
                'lon': 15.312222,
                'type': 'intermediaire'
            },
            'AVENUE_KASAVUBU': {
                'nom': 'Avenue Kasa-Vubu', 
                'lat': -4.315000, 
                'lon': 15.315833,
                'type': 'intermediaire'
            },
            'BOULEVARD_30_JUIN': {
                'nom': 'Boulevard du 30 Juin', 
                'lat': -4.317778, 
                'lon': 15.318611,
                'type': 'intermediaire'
            },
            'PLACE_STATION': {
                'nom': 'Place de la Station', 
                'lat': -4.320000, 
                'lon': 15.320833,
                'type': 'intermediaire'
            },
            'GARE_CENTRALE': {
                'nom': 'Gare Centrale', 
                'lat': -4.321389, 
                'lon': 15.322500,
                'type': 'arrivee'
            }
        }
        
        for node_id, info in locations.items():
            self.G.add_node(node_id, **info)
        
        # RÉSEAU COMPLET DES ROUTES
        routes = [
            # Routes principales
            ('RP_VICTOIRE', 'PLACE_VICTOIRE', 0.3, 2, 'Boulevard Triomphal'),
            ('PLACE_VICTOIRE', 'MARCHE_CENTRAL', 0.4, 3, 'Avenue de la Justice'),
            ('MARCHE_CENTRAL', 'AVENUE_COMMERCE', 0.5, 4, 'Rue Commerce'),
            ('AVENUE_COMMERCE', 'STADE_MAYAMA', 0.6, 5, 'Avenue Haut-Congo'),
            ('STADE_MAYAMA', 'CARREFOUR_TSHENUKA', 0.7, 6, 'Boulevard Lumumba'),
            ('CARREFOUR_TSHENUKA', 'AVENUE_KASAVUBU', 0.8, 7, 'Rue Marchal'),
            ('AVENUE_KASAVUBU', 'BOULEVARD_30_JUIN', 0.4, 3, 'Avenue Kasa-Vubu'),
            ('BOULEVARD_30_JUIN', 'PLACE_STATION', 0.5, 4, 'Boulevard du 30 Juin'),
            ('PLACE_STATION', 'GARE_CENTRALE', 0.3, 2, 'Avenue de la Gare'),
            
            # Routes alternatives
            ('RP_VICTOIRE', 'MARCHE_CENTRAL', 0.8, 6, 'Route Directe Victoire'),
            ('MARCHE_CENTRAL', 'STADE_MAYAMA', 0.9, 7, 'Avenue Industrielle'),
            ('AVENUE_COMMERCE', 'CARREFOUR_TSHENUKA', 1.1, 8, 'Route Express'),
            ('STADE_MAYAMA', 'AVENUE_KASAVUBU', 1.2, 9, 'Boulevard Principal'),
            ('CARREFOUR_TSHENUKA', 'BOULEVARD_30_JUIN', 0.9, 7, 'Avenue Flambeau'),
            ('AVENUE_KASAVUBU', 'GARE_CENTRALE', 1.4, 10, 'Route Rapide')
        ]
        
        for dep, arr, distance, temps, nom_route in routes:
            self.G.add_edge(
                dep, arr, 
                distance=distance,
                temps=temps,
                nom_route=nom_route
            )
    
    def calculer_distance_reelle(self, lat1, lon1, lat2, lon2):
        """Calcule la distance réelle entre deux points GPS (simplifié)"""
        # Conversion en radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Différences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Formule de Haversine simplifiée
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Rayon de la Terre en km
        R = 6371
        distance = R * c
        
        return round(distance, 2)
    
    def get_shortest_path(self, start, end, criteria='distance'):
        try:
            path = nx.shortest_path(self.G, start, end, weight=criteria)
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
                
                # Coordonnées réelles pour la carte
                path_coords.append([
                    [self.G.nodes[dep]['lon'], self.G.nodes[dep]['lat']],
                    [self.G.nodes[arr]['lon'], self.G.nodes[arr]['lat']]
                ])
            
            return {
                'path': [self.G.nodes[node]['nom'] for node in path],
                'path_ids': path,
                'total_distance': round(total_distance, 2),
                'total_time': total_time,
                'steps': steps,
                'path_coords': path_coords
            }
        except nx.NetworkXNoPath:
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

@app.route('/api/shortest-path/<criteria>')
def shortest_path(criteria):
    """Criteria: 'distance' ou 'temps'"""
    result = transport.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', criteria)
    return jsonify(result or {"error": "No path found"})

@app.route('/api/all-paths')
def all_paths():
    """Retourne tous les chemins possibles"""
    distance_path = transport.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', 'distance')
    time_path = transport.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', 'temps')
    
    return jsonify({
        'by_distance': distance_path,
        'by_time': time_path
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "OK", 
        "message": "Transport Kinshasa operational",
        "network_stats": {
            "nodes": transport.G.number_of_nodes(),
            "edges": transport.G.number_of_edges(),
            "routes": len(list(nx.all_simple_paths(transport.G, 'RP_VICTOIRE', 'GARE_CENTRALE')))
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)