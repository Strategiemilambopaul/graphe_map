from flask import Flask, render_template, jsonify
import networkx as nx
import math
import os
from typing import Dict, List, Optional, Tuple

app = Flask(__name__)

class TransportSystem:
    def __init__(self):
        self.G = nx.DiGraph()
        self.setup_network()
    
    def setup_network(self):
        """Initialise le réseau de transport avec des coordonnées réalistes"""
        # COORDONNÉES RÉELLES AMÉLIORÉES - KINSHASA
        locations = {
            'RP_VICTOIRE': {
                'nom': 'Rond-Point Victoire', 
                'lat': -4.337778, 
                'lon': 15.305000,
                'type': 'depart',
                'description': 'Point de départ principal'
            },
            'PLACE_VICTOIRE': {
                'nom': 'Place de la Victoire', 
                'lat': -4.338056, 
                'lon': 15.305000,
                'type': 'intermediaire',
                'description': 'Place centrale'
            },
            'MARCHE_CENTRAL': {
                'nom': 'Marché Central', 
                'lat': -4.316000, 
                'lon': 15.311000,
                'type': 'intermediaire',
                'description': 'Zone commerciale'
            },
            'AVENUE_COMMERCE': {
                'nom': 'Avenue du Commerce', 
                'lat': -4.313000, 
                'lon': 15.312000,
                'type': 'intermediaire',
                'description': 'Axe commercial'
            },
            'STADE_MAYAMA': {
                'nom': 'Stade Mayama', 
                'lat': -4.310000, 
                'lon': 15.314000,
                'type': 'intermediaire',
                'description': 'Complexe sportif'
            },
            'CARREFOUR_TSHENUKA': {
                'nom': 'Carrefour Tshénuka', 
                'lat': -4.307000, 
                'lon': 15.316000,
                'type': 'intermediaire',
                'description': 'Carrefour important'
            },
            'AVENUE_KASAVUBU': {
                'nom': 'Avenue Kasa-Vubu', 
                'lat': -4.305000, 
                'lon': 15.317000,
                'type': 'intermediaire',
                'description': 'Artère principale'
            },
            'BOULEVARD_30_JUIN': {
                'nom': 'Boulevard du 30 Juin', 
                'lat': -4.303000, 
                'lon': 15.318000,
                'type': 'intermediaire',
                'description': 'Boulevard majeur'
            },
            'PLACE_STATION': {
                'nom': 'Place de la Station', 
                'lat': -4.301500, 
                'lon': 15.318500,
                'type': 'intermediaire',
                'description': 'Proche de la gare'
            },
            'GARE_CENTRALE': {
                'nom': 'Gare Centrale', 
                'lat': -4.300556, 
                'lon': 15.318889,
                'type': 'arrivee',
                'description': 'Destination finale'
            }
        }
        
        # Ajout des nœuds avec métadonnées complètes
        for node_id, info in locations.items():
            self.G.add_node(node_id, **info)
        
        # DÉFINITION DES CONNEXIONS (sans distances pour calcul automatique)
        connections = [
            # Routes principales
            ('RP_VICTOIRE', 'PLACE_VICTOIRE', 'Boulevard Triomphal', 'principale'),
            ('PLACE_VICTOIRE', 'MARCHE_CENTRAL', 'Avenue de la Justice', 'principale'),
            ('MARCHE_CENTRAL', 'AVENUE_COMMERCE', 'Rue Commerce', 'principale'),
            ('AVENUE_COMMERCE', 'STADE_MAYAMA', 'Avenue Haut-Congo', 'principale'),
            ('STADE_MAYAMA', 'CARREFOUR_TSHENUKA', 'Boulevard Lumumba', 'principale'),
            ('CARREFOUR_TSHENUKA', 'AVENUE_KASAVUBU', 'Rue Marchal', 'principale'),
            ('AVENUE_KASAVUBU', 'BOULEVARD_30_JUIN', 'Avenue Kasa-Vubu', 'principale'),
            ('BOULEVARD_30_JUIN', 'PLACE_STATION', 'Boulevard du 30 Juin', 'principale'),
            ('PLACE_STATION', 'GARE_CENTRALE', 'Avenue de la Gare', 'principale'),
            
            # Routes alternatives
            ('RP_VICTOIRE', 'MARCHE_CENTRAL', 'Route Directe Victoire', 'alternative'),
            ('MARCHE_CENTRAL', 'STADE_MAYAMA', 'Avenue Industrielle', 'alternative'),
            ('AVENUE_COMMERCE', 'CARREFOUR_TSHENUKA', 'Route Express', 'alternative'),
            ('STADE_MAYAMA', 'AVENUE_KASAVUBU', 'Boulevard Principal', 'alternative'),
            ('CARREFOUR_TSHENUKA', 'BOULEVARD_30_JUIN', 'Avenue Flambeau', 'alternative'),
            ('AVENUE_KASAVUBU', 'GARE_CENTRALE', 'Route Rapide', 'alternative')
        ]
        
        # Calcul automatique des distances et temps
        for dep, arr, nom_route, type_route in connections:
            distance = self.calculer_distance_reelle(
                self.G.nodes[dep]['lat'], self.G.nodes[dep]['lon'],
                self.G.nodes[arr]['lat'], self.G.nodes[arr]['lon']
            )
            
            # Calcul du temps basé sur le type de route et distance
            temps = self.calculer_temps_trajet(distance, type_route)
            
            self.G.add_edge(
                dep, arr, 
                distance=round(distance, 3),
                temps=round(temps, 1),
                nom_route=nom_route,
                type_route=type_route,
                vitesse_moyenne=20 if type_route == 'principale' else 15  # km/h
            )
    
    def calculer_distance_reelle(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance réelle entre deux points GPS avec formule Haversine"""
        # Rayon de la Terre en km
        R = 6371.0
        
        # Conversion en radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Différences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Formule de Haversine
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    def calculer_temps_trajet(self, distance: float, type_route: str) -> float:
        """Calcule le temps de trajet en minutes selon le type de route"""
        # Vitesses moyennes en km/h
        vitesses = {
            'principale': 25,    # Routes principales fluides
            'alternative': 20,   # Routes secondaires
            'express': 30        # Routes rapides
        }
        
        vitesse = vitesses.get(type_route, 20)
        temps_heures = distance / vitesse
        temps_minutes = temps_heures * 60
        
        # Ajout d'un facteur de trafic réaliste
        facteur_trafic = 1.2 if type_route == 'principale' else 1.1
        return temps_minutes * facteur_trafic
    
    def get_shortest_path(self, start: str, end: str, criteria: str = 'distance') -> Optional[Dict]:
        """Trouve le chemin optimal selon le critère spécifié"""
        try:
            if criteria not in ['distance', 'temps']:
                criteria = 'distance'
            
            path = nx.shortest_path(self.G, start, end, weight=criteria)
            
            # Calcul des totaux
            total_distance = sum(self.G[path[i]][path[i+1]]['distance'] for i in range(len(path)-1))
            total_time = sum(self.G[path[i]][path[i+1]]['temps'] for i in range(len(path)-1))
            
            # Préparation des étapes
            steps = []
            path_coords = []
            
            for i in range(len(path)-1):
                dep = path[i]
                arr = path[i+1]
                edge_data = self.G[dep][arr]
                
                steps.append({
                    'etape': i + 1,
                    'from': self.G.nodes[dep]['nom'],
                    'from_id': dep,
                    'to': self.G.nodes[arr]['nom'],
                    'to_id': arr,
                    'distance': round(edge_data['distance'], 2),
                    'time': round(edge_data['temps'], 1),
                    'route': edge_data['nom_route'],
                    'type_route': edge_data['type_route'],
                    'vitesse_moyenne': edge_data['vitesse_moyenne']
                })
                
                # Coordonnées pour la carte
                path_coords.append([
                    [self.G.nodes[dep]['lon'], self.G.nodes[dep]['lat']],
                    [self.G.nodes[arr]['lon'], self.G.nodes[arr]['lat']]
                ])
            
            return {
                'critere': criteria,
                'path': [self.G.nodes[node]['nom'] for node in path],
                'path_ids': path,
                'total_distance': round(total_distance, 2),
                'total_time': round(total_time, 1),
                'vitesse_moyenne': round(total_distance / (total_time / 60), 1),
                'steps': steps,
                'path_coords': path_coords,
                'nombre_etapes': len(steps)
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def get_network_stats(self) -> Dict:
        """Retourne les statistiques du réseau"""
        return {
            'nombre_noeuds': self.G.number_of_nodes(),
            'nombre_aretes': self.G.number_of_edges(),
            'densite': round(nx.density(self.G), 3),
            'chemins_possibles': len(list(nx.all_simple_paths(self.G, 'RP_VICTOIRE', 'GARE_CENTRALE'))),
            'distance_totale_reseau': round(sum(self.G[u][v]['distance'] for u, v in self.G.edges()), 2)
        }
    
    def get_all_paths(self) -> Dict:
        """Retourne tous les chemins optimaux"""
        return {
            'by_distance': self.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', 'distance'),
            'by_time': self.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', 'temps')
        }

# Initialisation du système
transport = TransportSystem()

@app.route('/')
def index():
    """Page principale de l'application"""
    return render_template('index_unifie.html')

@app.route('/api/network')
def get_network():
    """API: Retourne tout le réseau"""
    nodes = []
    for node_id in transport.G.nodes():
        node_data = transport.G.nodes[node_id]
        nodes.append({
            'id': node_id,
            'name': node_data['nom'],
            'lat': node_data['lat'],
            'lon': node_data['lon'],
            'type': node_data['type'],
            'description': node_data.get('description', '')
        })
    
    edges = []
    for u, v in transport.G.edges():
        edge_data = transport.G[u][v]
        edges.append({
            'from': u,
            'to': v,
            'distance': edge_data['distance'],
            'time': edge_data['temps'],
            'route': edge_data['nom_route'],
            'type_route': edge_data['type_route'],
            'vitesse_moyenne': edge_data['vitesse_moyenne']
        })
    
    return jsonify({
        'nodes': nodes, 
        'edges': edges,
        'stats': transport.get_network_stats()
    })

@app.route('/api/shortest-path/<criteria>')
def shortest_path(criteria):
    """API: Chemin optimal selon le critère"""
    result = transport.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', criteria)
    return jsonify(result or {"error": "Aucun chemin trouvé"})

@app.route('/api/all-paths')
def all_paths():
    """API: Tous les chemins optimaux"""
    return jsonify(transport.get_all_paths())

@app.route('/api/stats')
def stats():
    """API: Statistiques du réseau"""
    return jsonify(transport.get_network_stats())

@app.route('/health')
def health():
    """API: Santé de l'application"""
    return jsonify({
        "status": "OK", 
        "message": "Transport Kinshasa opérationnel",
        "version": "2.0",
        "network_stats": transport.get_network_stats()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint non trouvé"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erreur interne du serveur"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)