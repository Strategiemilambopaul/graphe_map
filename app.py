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
                'description': 'Point de départ principal - Centre ville'
            },
            'PLACE_VICTOIRE': {
                'nom': 'Place de la Victoire', 
                'lat': -4.338056, 
                'lon': 15.305000,
                'type': 'intermediaire',
                'description': 'Place centrale - Zone administrative'
            },
            'MARCHE_CENTRAL': {
                'nom': 'Marché Central', 
                'lat': -4.316000, 
                'lon': 15.311000,
                'type': 'intermediaire',
                'description': 'Zone commerciale animée'
            },
            'AVENUE_COMMERCE': {
                'nom': 'Avenue du Commerce', 
                'lat': -4.313000, 
                'lon': 15.312000,
                'type': 'intermediaire',
                'description': 'Axe commercial principal'
            },
            'STADE_MAYAMA': {
                'nom': 'Stade Mayama', 
                'lat': -4.310000, 
                'lon': 15.314000,
                'type': 'intermediaire',
                'description': 'Complexe sportif et culturel'
            },
            'CARREFOUR_TSHENUKA': {
                'nom': 'Carrefour Tshénuka', 
                'lat': -4.307000, 
                'lon': 15.316000,
                'type': 'intermediaire',
                'description': 'Carrefour important - Zone résidentielle'
            },
            'AVENUE_KASAVUBU': {
                'nom': 'Avenue Kasa-Vubu', 
                'lat': -4.305000, 
                'lon': 15.317000,
                'type': 'intermediaire',
                'description': 'Artère principale - Quartier des affaires'
            },
            'BOULEVARD_30_JUIN': {
                'nom': 'Boulevard du 30 Juin', 
                'lat': -4.303000, 
                'lon': 15.318000,
                'type': 'intermediaire',
                'description': 'Boulevard majeur - Axe historique'
            },
            'PLACE_STATION': {
                'nom': 'Place de la Station', 
                'lat': -4.301500, 
                'lon': 15.318500,
                'type': 'intermediaire',
                'description': 'Proche de la gare - Zone de transit'
            },
            'GARE_CENTRALE': {
                'nom': 'Gare Centrale', 
                'lat': -4.300556, 
                'lon': 15.318889,
                'type': 'arrivee',
                'description': 'Destination finale - Pôle de transport'
            }
        }
        
        # Ajout des nœuds avec métadonnées complètes
        for node_id, info in locations.items():
            self.G.add_node(node_id, **info)
        
        # DÉFINITION DES CONNEXIONS AVEC COORDONNÉES RÉELLES
        connections = [
            # Routes principales (vitesse moyenne 25 km/h)
            ('RP_VICTOIRE', 'PLACE_VICTOIRE', 'Boulevard Triomphal', 'principale'),
            ('PLACE_VICTOIRE', 'MARCHE_CENTRAL', 'Avenue de la Justice', 'principale'),
            ('MARCHE_CENTRAL', 'AVENUE_COMMERCE', 'Rue Commerce', 'principale'),
            ('AVENUE_COMMERCE', 'STADE_MAYAMA', 'Avenue Haut-Congo', 'principale'),
            ('STADE_MAYAMA', 'CARREFOUR_TSHENUKA', 'Boulevard Lumumba', 'principale'),
            ('CARREFOUR_TSHENUKA', 'AVENUE_KASAVUBU', 'Rue Marchal', 'principale'),
            ('AVENUE_KASAVUBU', 'BOULEVARD_30_JUIN', 'Avenue Kasa-Vubu', 'principale'),
            ('BOULEVARD_30_JUIN', 'PLACE_STATION', 'Boulevard du 30 Juin', 'principale'),
            ('PLACE_STATION', 'GARE_CENTRALE', 'Avenue de la Gare', 'principale'),
            
            # Routes alternatives (vitesse moyenne 20 km/h)
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
                vitesse_moyenne=25 if type_route == 'principale' else 20
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
        # Vitesses moyennes en km/h (réalistes pour Kinshasa)
        vitesses = {
            'principale': 25,    # Routes principales fluides
            'alternative': 20,   # Routes secondaires
            'express': 30        # Routes rapides
        }
        
        vitesse = vitesses.get(type_route, 20)
        temps_heures = distance / vitesse
        temps_minutes = temps_heures * 60
        
        # Ajout d'un facteur de trafic réaliste pour Kinshasa
        facteur_trafic = 1.3 if type_route == 'principale' else 1.15
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
                    'vitesse_moyenne': edge_data['vitesse_moyenne'],
                    'coordinates': {
                        'start': [self.G.nodes[dep]['lon'], self.G.nodes[dep]['lat']],
                        'end': [self.G.nodes[arr]['lon'], self.G.nodes[arr]['lat']]
                    }
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
                'nombre_etapes': len(steps),
                'efficacite': self.calculer_efficacite(total_distance, total_time)
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def calculer_efficacite(self, distance: float, temps: float) -> str:
        """Calcule l'efficacité du trajet"""
        vitesse_moyenne = distance / (temps / 60)
        if vitesse_moyenne > 20:
            return "Excellente"
        elif vitesse_moyenne > 15:
            return "Bonne"
        elif vitesse_moyenne > 10:
            return "Moyenne"
        else:
            return "Faible"
    
    def get_all_paths(self) -> Dict:
        """Retourne tous les chemins optimaux avec comparaison"""
        by_distance = self.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', 'distance')
        by_time = self.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', 'temps')
        
        return {
            'by_distance': by_distance,
            'by_time': by_time,
            'comparaison': self.comparer_chemins(by_distance, by_time)
        }
    
    def comparer_chemins(self, chemin_distance: Dict, chemin_temps: Dict) -> Dict:
        """Compare les deux chemins optimaux"""
        if not chemin_distance or not chemin_temps:
            return {}
        
        gain_temps = chemin_distance['total_time'] - chemin_temps['total_time']
        gain_distance = chemin_temps['total_distance'] - chemin_distance['total_distance']
        
        return {
            'gain_temps_minutes': round(gain_temps, 1),
            'gain_temps_pourcentage': round((gain_temps / chemin_distance['total_time']) * 100, 1),
            'gain_distance_km': round(gain_distance, 2),
            'recommandation': "Temps" if gain_temps > 5 else "Distance"
        }
    
    def get_network_stats(self) -> Dict:
        """Retourne les statistiques détaillées du réseau"""
        stats = {
            'nombre_noeuds': self.G.number_of_nodes(),
            'nombre_aretes': self.G.number_of_edges(),
            'densite': round(nx.density(self.G), 3),
            'distance_totale_reseau': round(sum(self.G[u][v]['distance'] for u, v in self.G.edges()), 2),
            'temps_total_reseau': round(sum(self.G[u][v]['temps'] for u, v in self.G.edges()), 1),
            'vitesse_moyenne_reseau': 0,
            'types_routes': {},
            'connectivite': {}
        }
        
        # Statistiques par type de route
        types_routes = {}
        for u, v, data in self.G.edges(data=True):
            type_route = data['type_route']
            if type_route not in types_routes:
                types_routes[type_route] = {'count': 0, 'distance': 0, 'temps': 0}
            types_routes[type_route]['count'] += 1
            types_routes[type_route]['distance'] += data['distance']
            types_routes[type_route]['temps'] += data['temps']
        
        stats['types_routes'] = types_routes
        
        # Connectivité des nœuds
        for node in self.G.nodes():
            stats['connectivite'][node] = {
                'degree_entrant': self.G.in_degree(node),
                'degree_sortant': self.G.out_degree(node),
                'degree_total': self.G.degree(node)
            }
        
        # Vitesse moyenne
        if stats['temps_total_reseau'] > 0:
            stats['vitesse_moyenne_reseau'] = round(
                stats['distance_totale_reseau'] / (stats['temps_total_reseau'] / 60), 1
            )
        
        return stats
    
    def get_node_details(self, node_id: str) -> Optional[Dict]:
        """Retourne les détails d'un nœud spécifique"""
        if node_id not in self.G.nodes():
            return None
        
        node_data = self.G.nodes[node_id]
        connections = {
            'entrantes': list(self.G.predecessors(node_id)),
            'sortantes': list(self.G.successors(node_id))
        }
        
        return {
            'id': node_id,
            **node_data,
            'connections': connections,
            'centralite': self.calculer_centralite(node_id)
        }
    
    def calculer_centralite(self, node_id: str) -> Dict:
        """Calcule les métriques de centralité pour un nœud"""
        return {
            'degree_centrality': round(nx.degree_centrality(self.G).get(node_id, 0), 3),
            'betweenness_centrality': round(nx.betweenness_centrality(self.G).get(node_id, 0), 3),
            'closeness_centrality': round(nx.closeness_centrality(self.G).get(node_id, 0), 3)
        }

# Initialisation du système
transport = TransportSystem()

@app.route('/')
def index():
    """Page principale de l'application"""
    return render_template('index_unifie.html')

@app.route('/api/network')
def get_network():
    """API: Retourne tout le réseau avec statistiques complètes"""
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
        'stats': transport.get_network_stats(),
        'metadata': {
            'version': '3.0',
            'last_updated': '2024-01-01',
            'city': 'Kinshasa',
            'description': 'Réseau de transport Rond-Point Victoire → Gare Centrale'
        }
    })

@app.route('/api/shortest-path/<criteria>')
def shortest_path(criteria):
    """API: Chemin optimal selon le critère"""
    if criteria not in ['distance', 'temps']:
        return jsonify({"error": "Critère invalide. Utilisez 'distance' ou 'temps'"}), 400
    
    result = transport.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', criteria)
    if not result:
        return jsonify({"error": "Aucun chemin trouvé entre les points spécifiés"}), 404
    
    return jsonify(result)

@app.route('/api/all-paths')
def all_paths():
    """API: Tous les chemins optimaux avec comparaison"""
    return jsonify(transport.get_all_paths())

@app.route('/api/stats')
def stats():
    """API: Statistiques détaillées du réseau"""
    return jsonify(transport.get_network_stats())

@app.route('/api/node/<node_id>')
def node_details(node_id):
    """API: Détails d'un nœud spécifique"""
    details = transport.get_node_details(node_id)
    if not details:
        return jsonify({"error": f"Nœud '{node_id}' non trouvé"}), 404
    return jsonify(details)

@app.route('/api/health')
def health():
    """API: Santé de l'application avec diagnostics"""
    try:
        stats = transport.get_network_stats()
        return jsonify({
            "status": "OK", 
            "message": "Transport Kinshasa opérationnel",
            "version": "3.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "network_stats": stats,
            "diagnostics": {
                "graph_connected": nx.is_weakly_connected(transport.G),
                "has_path": nx.has_path(transport.G, 'RP_VICTOIRE', 'GARE_CENTRALE'),
                "nodes_count": stats['nombre_noeuds'],
                "edges_count": stats['nombre_aretes']
            }
        })
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": f"Erreur système: {str(e)}"
        }), 500

@app.route('/api/search/<query>')
def search_nodes(query):
    """API: Recherche de nœuds par nom"""
    query = query.lower()
    results = []
    
    for node_id in transport.G.nodes():
        node_data = transport.G.nodes[node_id]
        node_name = node_data['nom'].lower()
        node_desc = node_data.get('description', '').lower()
        
        if query in node_name or query in node_desc:
            results.append({
                'id': node_id,
                'name': node_data['nom'],
                'type': node_data['type'],
                'description': node_data.get('description', ''),
                'lat': node_data['lat'],
                'lon': node_data['lon']
            })
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint non trouvé",
        "available_endpoints": [
            "/api/network",
            "/api/shortest-path/{distance|temps}",
            "/api/all-paths", 
            "/api/stats",
            "/api/node/{node_id}",
            "/api/health",
            "/api/search/{query}"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Erreur interne du serveur",
        "message": "Veuillez réessayer plus tard"
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Requête invalide",
        "message": "Vérifiez les paramètres de votre requête"
    }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)