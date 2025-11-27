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
        # Coordonnées réelles approximatives de Kinshasa
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
            'STADE_MAYAMA': {
                'nom': 'Stade Mayama', 
                'lat': -4.3083, 
                'lon': 15.3089,
                'type': 'intermediaire'
            },
            'PLACE_VICTORIA': {
                'nom': 'Place Victoria', 
                'lat': -4.3050, 
                'lon': 15.2950,
                'type': 'intermediaire'
            },
            'CARREFOUR_TSHENUKA': {
                'nom': 'Carrefour Tshénuka', 
                'lat': -4.3122, 
                'lon': 15.3125,
                'type': 'intermediaire'
            },
            'AVENUE_KASAVUBU': {
                'nom': 'Avenue Kasa-Vubu', 
                'lat': -4.3150, 
                'lon': 15.3180,
                'type': 'intermediaire'
            },
            'BOULEVARD_30_JUIN': {
                'nom': 'Boulevard du 30 Juin', 
                'lat': -4.3180, 
                'lon': 15.3150,
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
        
        # Routes avec distances calculées
        routes = [
            ('RP_VICTOIRE', 'MARCHE_CENTRAL', 'Avenue de la Justice'),
            ('RP_VICTOIRE', 'PLACE_VICTORIA', 'Boulevard Triomphal'),
            ('MARCHE_CENTRAL', 'STADE_MAYAMA', 'Rue Commerce'),
            ('MARCHE_CENTRAL', 'CARREFOUR_TSHENUKA', 'Avenue Haut-Congo'),
            ('PLACE_VICTORIA', 'CARREFOUR_TSHENUKA', 'Rue Industrielle'),
            ('PLACE_VICTORIA', 'BOULEVARD_30_JUIN', 'Avenue Reine'),
            ('STADE_MAYAMA', 'AVENUE_KASAVUBU', 'Boulevard Lumumba'),
            ('CARREFOUR_TSHENUKA', 'AVENUE_KASAVUBU', 'Rue Marchal'),
            ('CARREFOUR_TSHENUKA', 'BOULEVARD_30_JUIN', 'Avenue Flambeau'),
            ('AVENUE_KASAVUBU', 'GARE_CENTRALE', 'Avenue Kasa-Vubu'),
            ('BOULEVARD_30_JUIN', 'GARE_CENTRALE', 'Boulevard du 30 Juin'),
            ('STADE_MAYAMA', 'GARE_CENTRALE', 'Route Directe')
        ]
        
        for dep, arr, nom_route in routes:
            distance = self.calculer_distance(
                self.G.nodes[dep]['lat'], self.G.nodes[dep]['lon'],
                self.G.nodes[arr]['lat'], self.G.nodes[arr]['lon']
            )
            temps = self.calculer_temps(distance)
            
            self.G.add_edge(
                dep, arr, 
                distance=round(distance, 2),
                temps=temps,
                nom_route=nom_route
            )
    
    def calculer_distance(self, lat1, lon1, lat2, lon2):
        """Calcule la distance en km entre deux points GPS"""
        R = 6371  # Rayon de la Terre en km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def calculer_temps(self, distance):
        """Estime le temps de trajet en minutes (vitesse moyenne 20km/h en ville)"""
        return int((distance / 20) * 60)
    
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

@app.route('/api/shortest-path/<start>/<end>')
def get_shortest_path(start, end):
    result = transport.get_shortest_path(start, end)
    return jsonify(result)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port)