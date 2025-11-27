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
        """Initialise le réseau de transport avec des coordonnées réalistes et routes complètes"""
        # COORDONNÉES RÉELLES AMÉLIORÉES - KINSHASA
        locations = {
            # POINTS DE DÉPART ET ARRIVÉE
            'RP_VICTOIRE': {
                'nom': 'Rond-Point Victoire', 
                'lat': -4.337778, 
                'lon': 15.305000,
                'type': 'depart',
                'description': 'Point de départ principal - Centre ville'
            },
            'GARE_CENTRALE': {
                'nom': 'Gare Centrale', 
                'lat': -4.300556, 
                'lon': 15.318889,
                'type': 'arrivee',
                'description': 'Destination finale - Pôle de transport'
            },
            
            # ARRÊTS INTERMÉDIAIRES PRINCIPAUX
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
            
            # NOUVEAUX ARRÊTS POUR COMPLÉTER LE RÉSEAU
            'UNIVERSITE': {
                'nom': 'Université de Kinshasa', 
                'lat': -4.335000, 
                'lon': 15.307000,
                'type': 'intermediaire',
                'description': 'Zone universitaire et estudiantine'
            },
            'HOPITAL_GENERAL': {
                'nom': 'Hôpital Général', 
                'lat': -4.332000, 
                'lon': 15.308000,
                'type': 'intermediaire',
                'description': 'Centre médical principal'
            },
            'MARCHE_BANDAL': {
                'nom': 'Marché Bandal', 
                'lat': -4.328000, 
                'lon': 15.309000,
                'type': 'intermediaire',
                'description': 'Marché secondaire - Quartier Bandal'
            },
            'PLACE_MATONGE': {
                'nom': 'Place Matonge', 
                'lat': -4.325000, 
                'lon': 15.310000,
                'type': 'intermediaire',
                'description': 'Place animée - Quartier culturel'
            },
            'STADE_TAATA': {
                'nom': 'Stade Taata', 
                'lat': -4.322000, 
                'lon': 15.311500,
                'type': 'intermediaire',
                'description': 'Stade de quartier'
            },
            'ECOLE_PRIMAIRE': {
                'nom': 'École Primaire', 
                'lat': -4.319000, 
                'lon': 15.312000,
                'type': 'intermediaire',
                'description': 'Établissement scolaire'
            },
            'POSTE_POLICE': {
                'nom': 'Poste de Police', 
                'lat': -4.317000, 
                'lon': 15.313000,
                'type': 'intermediaire',
                'description': 'Commissariat de police'
            },
            'CENTRE_AFFAIRES': {
                'nom': 'Centre d\'Affaires', 
                'lat': -4.314000, 
                'lon': 15.313500,
                'type': 'intermediaire',
                'description': 'Zone d\'entreprises et bureaux'
            },
            'PARC_PUBLIC': {
                'nom': 'Parc Public', 
                'lat': -4.311000, 
                'lon': 15.315000,
                'type': 'intermediaire',
                'description': 'Espace vert et de détente'
            },
            'GARE_ROUTIERE': {
                'nom': 'Gare Routière', 
                'lat': -4.308000, 
                'lon': 15.317500,
                'type': 'intermediaire',
                'description': 'Station de bus et taxis'
            },
            'MOSQUEE_CENTRALE': {
                'nom': 'Mosquée Centrale', 
                'lat': -4.306000, 
                'lon': 15.318000,
                'type': 'intermediaire',
                'description': 'Lieu de culte important'
            },
            'EGLISE_SAINTE': {
                'nom': 'Église Sainte-Anne', 
                'lat': -4.304000, 
                'lon': 15.318500,
                'type': 'intermediaire',
                'description': 'Église historique'
            }
        }
        
        # Ajout des nœuds avec métadonnées complètes
        for node_id, info in locations.items():
            self.G.add_node(node_id, **info)
        
        # DÉFINITION DE TOUTES LES CONNEXIONS POSSIBLES
        connections = [
            # ROUTES PRINCIPALES (vitesse moyenne 25 km/h)
            ('RP_VICTOIRE', 'PLACE_VICTOIRE', 'Boulevard Triomphal', 'principale'),
            ('PLACE_VICTOIRE', 'UNIVERSITE', 'Avenue des Universitaires', 'principale'),
            ('UNIVERSITE', 'HOPITAL_GENERAL', 'Rue des Hôpitaux', 'principale'),
            ('HOPITAL_GENERAL', 'MARCHE_BANDAL', 'Avenue du Progrès', 'principale'),
            ('MARCHE_BANDAL', 'PLACE_MATONGE', 'Boulevard Culturel', 'principale'),
            ('PLACE_MATONGE', 'STADE_TAATA', 'Avenue Sportive', 'principale'),
            ('STADE_TAATA', 'ECOLE_PRIMAIRE', 'Rue des Écoles', 'principale'),
            ('ECOLE_PRIMAIRE', 'POSTE_POLICE', 'Avenue de la Sécurité', 'principale'),
            ('POSTE_POLICE', 'MARCHE_CENTRAL', 'Boulevard Central', 'principale'),
            ('MARCHE_CENTRAL', 'CENTRE_AFFAIRES', 'Avenue des Affaires', 'principale'),
            ('CENTRE_AFFAIRES', 'AVENUE_COMMERCE', 'Rue du Commerce', 'principale'),
            ('AVENUE_COMMERCE', 'PARC_PUBLIC', 'Avenue Verte', 'principale'),
            ('PARC_PUBLIC', 'STADE_MAYAMA', 'Boulevard des Sports', 'principale'),
            ('STADE_MAYAMA', 'GARE_ROUTIERE', 'Route des Transports', 'principale'),
            ('GARE_ROUTIERE', 'CARREFOUR_TSHENUKA', 'Avenue du Carrefour', 'principale'),
            ('CARREFOUR_TSHENUKA', 'MOSQUEE_CENTRALE', 'Boulevard de la Foi', 'principale'),
            ('MOSQUEE_CENTRALE', 'AVENUE_KASAVUBU', 'Avenue Kasa-Vubu', 'principale'),
            ('AVENUE_KASAVUBU', 'EGLISE_SAINTE', 'Rue Sainte-Anne', 'principale'),
            ('EGLISE_SAINTE', 'BOULEVARD_30_JUIN', 'Boulevard du 30 Juin', 'principale'),
            ('BOULEVARD_30_JUIN', 'PLACE_STATION', 'Avenue de la Gare', 'principale'),
            ('PLACE_STATION', 'GARE_CENTRALE', 'Route Finale', 'principale'),
            
            # ROUTES ALTERNATIVES (vitesse moyenne 20 km/h)
            ('RP_VICTOIRE', 'UNIVERSITE', 'Route Campus', 'alternative'),
            ('RP_VICTOIRE', 'MARCHE_CENTRAL', 'Route Directe Victoire', 'alternative'),
            ('UNIVERSITE', 'MARCHE_BANDAL', 'Chemin Universitaire', 'alternative'),
            ('HOPITAL_GENERAL', 'PLACE_MATONGE', 'Route Médicale', 'alternative'),
            ('MARCHE_BANDAL', 'ECOLE_PRIMAIRE', 'Passage Bandal', 'alternative'),
            ('PLACE_MATONGE', 'POSTE_POLICE', 'Voie Culturelle', 'alternative'),
            ('STADE_TAATA', 'MARCHE_CENTRAL', 'Avenue du Stade', 'alternative'),
            ('ECOLE_PRIMAIRE', 'CENTRE_AFFAIRES', 'Route Scolaire', 'alternative'),
            ('POSTE_POLICE', 'AVENUE_COMMERCE', 'Voie de Sécurité', 'alternative'),
            ('MARCHE_CENTRAL', 'PARC_PUBLIC', 'Chemin du Marché', 'alternative'),
            ('CENTRE_AFFAIRES', 'STADE_MAYAMA', 'Route des Affaires', 'alternative'),
            ('AVENUE_COMMERCE', 'GARE_ROUTIERE', 'Voie Commerciale', 'alternative'),
            ('PARC_PUBLIC', 'CARREFOUR_TSHENUKA', 'Passage du Parc', 'alternative'),
            ('STADE_MAYAMA', 'MOSQUEE_CENTRALE', 'Route Sportive', 'alternative'),
            ('GARE_ROUTIERE', 'AVENUE_KASAVUBU', 'Chemin de la Gare', 'alternative'),
            ('CARREFOUR_TSHENUKA', 'EGLISE_SAINTE', 'Voie du Carrefour', 'alternative'),
            ('MOSQUEE_CENTRALE', 'BOULEVARD_30_JUIN', 'Route de la Mosquée', 'alternative'),
            ('AVENUE_KASAVUBU', 'PLACE_STATION', 'Passage Kasa-Vubu', 'alternative'),
            ('EGLISE_SAINTE', 'GARE_CENTRALE', 'Chemin Sainte-Anne', 'alternative'),
            
            # ROUTES EXPRESS (vitesse moyenne 30 km/h)
            ('RP_VICTOIRE', 'HOPITAL_GENERAL', 'Autoroute Est', 'express'),
            ('UNIVERSITE', 'PLACE_MATONGE', 'Voie Rapide Universitaire', 'express'),
            ('HOPITAL_GENERAL', 'STADE_TAATA', 'Express Médical', 'express'),
            ('MARCHE_BANDAL', 'POSTE_POLICE', 'Route Express Bandal', 'express'),
            ('PLACE_MATONGE', 'CENTRE_AFFAIRES', 'Boulevard Express', 'express'),
            ('STADE_TAATA', 'AVENUE_COMMERCE', 'Voie Sportive Express', 'express'),
            ('ECOLE_PRIMAIRE', 'STADE_MAYAMA', 'Route Scolaire Express', 'express'),
            ('POSTE_POLICE', 'PARC_PUBLIC', 'Voie Sécurisée Express', 'express'),
            ('MARCHE_CENTRAL', 'GARE_ROUTIERE', 'Avenue Marchande Express', 'express'),
            ('CENTRE_AFFAIRES', 'CARREFOUR_TSHENUKA', 'Route d\'Affaires Express', 'express'),
            ('AVENUE_COMMERCE', 'MOSQUEE_CENTRALE', 'Boulevard Commercial Express', 'express'),
            ('PARC_PUBLIC', 'AVENUE_KASAVUBU', 'Voie Verte Express', 'express'),
            ('STADE_MAYAMA', 'EGLISE_SAINTE', 'Route des Stades Express', 'express'),
            ('GARE_ROUTIERE', 'BOULEVARD_30_JUIN', 'Avenue des Transports Express', 'express'),
            ('CARREFOUR_TSHENUKA', 'PLACE_STATION', 'Voie Principale Express', 'express'),
            ('MOSQUEE_CENTRALE', 'GARE_CENTRALE', 'Route Directe Express', 'express'),
            
            # CONNEXIONS CROISÉES POUR PLUS DE FLEXIBILITÉ
            ('UNIVERSITE', 'POSTE_POLICE', 'Liaison Universitaire', 'alternative'),
            ('HOPITAL_GENERAL', 'CENTRE_AFFAIRES', 'Liaison Médicale', 'alternative'),
            ('MARCHE_BANDAL', 'STADE_MAYAMA', 'Liaison Bandal', 'alternative'),
            ('PLACE_MATONGE', 'GARE_ROUTIERE', 'Liaison Culturelle', 'alternative'),
            ('STADE_TAATA', 'CARREFOUR_TSHENUKA', 'Liaison Sportive', 'alternative'),
            ('ECOLE_PRIMAIRE', 'MOSQUEE_CENTRALE', 'Liaison Éducative', 'alternative'),
            ('POSTE_POLICE', 'EGLISE_SAINTE', 'Liaison de Sécurité', 'alternative')
        ]
        
        # Calcul automatique des distances et temps
        for dep, arr, nom_route, type_route in connections:
            distance = self.calculer_distance_reelle(
                self.G.nodes[dep]['lat'], self.G.nodes[dep]['lon'],
                self.G.nodes[arr]['lat'], self.G.nodes[arr]['lon']
            )
            
            temps = self.calculer_temps_trajet(distance, type_route)
            
            self.G.add_edge(
                dep, arr, 
                distance=round(distance, 3),
                temps=round(temps, 1),
                nom_route=nom_route,
                type_route=type_route,
                vitesse_moyenne=self.get_vitesse_moyenne(type_route)
            )
    
    def get_vitesse_moyenne(self, type_route: str) -> int:
        """Retourne la vitesse moyenne selon le type de route"""
        vitesses = {
            'principale': 25,     # Routes principales fluides (km/h)
            'alternative': 20,    # Routes secondaires (km/h)
            'express': 30         # Routes rapides (km/h)
        }
        return vitesses.get(type_route, 20)
    
    def calculer_distance_reelle(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance réelle entre deux points GPS avec formule Haversine"""
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    def calculer_temps_trajet(self, distance: float, type_route: str) -> float:
        """Calcule le temps de trajet en minutes selon le type de route"""
        vitesse = self.get_vitesse_moyenne(type_route)
        temps_heures = distance / vitesse
        temps_minutes = temps_heures * 60
        
        # Facteur de trafic réaliste pour Kinshasa
        facteurs_trafic = {
            'principale': 1.3,    # Plus de trafic sur les routes principales
            'alternative': 1.15,  # Moins de trafic sur les alternatives
            'express': 1.1        # Peu de trafic sur les routes express
        }
        
        facteur_trafic = facteurs_trafic.get(type_route, 1.2)
        return temps_minutes * facteur_trafic
    
    def get_shortest_path(self, start: str, end: str, criteria: str = 'distance') -> Optional[Dict]:
        """Trouve le chemin optimal selon le critère spécifié"""
        try:
            if criteria not in ['distance', 'temps']:
                criteria = 'distance'
            
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
        if vitesse_moyenne > 25:
            return "Excellente"
        elif vitesse_moyenne > 20:
            return "Bonne"
        elif vitesse_moyenne > 15:
            return "Moyenne"
        else:
            return "Faible"
    
    def get_all_paths(self) -> Dict:
        """Retourne les deux chemins optimaux (distance et temps) avec comparaison"""
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
            'recommandation': "Temps" if gain_temps > 1 else "Distance"
        }

    def get_all_simple_paths(self, max_paths: int = 50) -> List[Dict]:
        """
        Retourne tous les chemins simples (sans boucle) entre RP_VICTOIRE et GARE_CENTRALE,
        avec une limite pour éviter les performances.
        """
        start = 'RP_VICTOIRE'
        end = 'GARE_CENTRALE'
        all_paths_data = []

        try:
            # Utiliser networkx.all_simple_paths avec une limite
            paths_found = 0
            for path_nodes in nx.all_simple_paths(self.G, source=start, target=end, cutoff=15):
                if paths_found >= max_paths:
                    break
                    
                total_distance = 0.0
                total_time = 0.0
                path_steps = []

                # Calculer les totaux pour chaque chemin
                for i in range(len(path_nodes) - 1):
                    dep = path_nodes[i]
                    arr = path_nodes[i+1]
                    edge_data = self.G[dep][arr]
                    
                    total_distance += edge_data['distance']
                    total_time += edge_data['temps']
                    
                    path_steps.append({
                        'from': self.G.nodes[dep]['nom'],
                        'to': self.G.nodes[arr]['nom'],
                        'route': edge_data['nom_route'],
                        'type': edge_data['type_route'],
                        'time': round(edge_data['temps'], 1),
                        'distance': round(edge_data['distance'], 3)
                    })

                # Stocker le chemin et ses métriques
                all_paths_data.append({
                    'path': [self.G.nodes[node]['nom'] for node in path_nodes],
                    'path_ids': path_nodes,
                    'total_distance_km': round(total_distance, 3),
                    'total_time_min': round(total_time, 1),
                    'vitesse_moyenne': round(total_distance / (total_time / 60), 1) if total_time > 0 else 0,
                    'nombre_etapes': len(path_steps),
                    'steps': path_steps
                })
                
                paths_found += 1

            # Trier les chemins par durée totale (le plus rapide en premier)
            all_paths_data.sort(key=lambda x: x['total_time_min'])
            
            return all_paths_data
        
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

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
            'connectivite': {},
            'noeuds_par_type': {}
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
        
        # Statistiques par type de nœud
        noeuds_par_type = {}
        for node in self.G.nodes():
            node_type = self.G.nodes[node]['type']
            if node_type not in noeuds_par_type:
                noeuds_par_type[node_type] = 0
            noeuds_par_type[node_type] += 1
        stats['noeuds_par_type'] = noeuds_par_type
        
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
            'entrantes': [
                {
                    'from': self.G.nodes[u]['nom'],
                    'from_id': u,
                    'route': self.G[u][node_id]['nom_route'],
                    'distance': self.G[u][node_id]['distance'],
                    'time': self.G[u][node_id]['temps']
                } for u in self.G.predecessors(node_id)
            ],
            'sortantes': [
                {
                    'to': self.G.nodes[v]['nom'],
                    'to_id': v,
                    'route': self.G[node_id][v]['nom_route'],
                    'distance': self.G[node_id][v]['distance'],
                    'time': self.G[node_id][v]['temps']
                } for v in self.G.successors(node_id)
            ]
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
    
    def get_all_nodes_by_type(self, node_type: str = None) -> List[Dict]:
        """Retourne tous les nœuds, optionnellement filtrés par type"""
        nodes = []
        for node_id in self.G.nodes():
            node_data = self.G.nodes[node_id]
            if node_type is None or node_data['type'] == node_type:
                nodes.append({
                    'id': node_id,
                    'name': node_data['nom'],
                    'lat': node_data['lat'],
                    'lon': node_data['lon'],
                    'type': node_data['type'],
                    'description': node_data.get('description', '')
                })
        return nodes

# Initialisation du système
transport = TransportSystem()

# --- ROUTES FLASK ---

@app.route('/')
def index():
    """Page principale de l'application"""
    return render_template('index_unifie.html')

@app.route('/api/network')
def get_network():
    """API: Retourne tout le réseau avec statistiques complètes"""
    nodes = transport.get_all_nodes_by_type()
    
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
            'version': '4.0',
            'city': 'Kinshasa',
            'description': 'Réseau de transport complet Rond-Point Victoire → Gare Centrale',
            'total_nodes': len(nodes),
            'total_edges': len(edges)
        }
    })

@app.route('/api/shortest-path/<criteria>')
def shortest_path(criteria):
    """API: Chemin optimal selon le critère ('distance' ou 'temps')"""
    if criteria not in ['distance', 'temps']:
        return jsonify({"error": "Critère invalide. Utilisez 'distance' ou 'temps'"}), 400
    
    result = transport.get_shortest_path('RP_VICTOIRE', 'GARE_CENTRALE', criteria)
    if not result:
        return jsonify({"error": "Aucun chemin trouvé entre les points spécifiés"}), 404
    
    return jsonify(result)

@app.route('/api/all-paths')
def all_paths():
    """API: Les deux chemins optimaux (distance et temps) avec comparaison"""
    return jsonify(transport.get_all_paths())

@app.route('/api/all-simple-paths')
def all_simple_paths():
    """API: Retourne la liste de tous les chemins simples possibles"""
    all_paths = transport.get_all_simple_paths()
    
    if not all_paths:
        return jsonify({"error": "Aucun chemin simple trouvé entre les points spécifiés"}), 404
    
    return jsonify({
        'start_node': transport.G.nodes['RP_VICTOIRE']['nom'],
        'end_node': transport.G.nodes['GARE_CENTRALE']['nom'],
        'total_paths': len(all_paths),
        'paths': all_paths
    })

@app.route('/api/stats')
def stats():
    """API: Statistiques détaillées du réseau"""
    return jsonify(transport.get_network_stats())

@app.route('/api/nodes')
def all_nodes():
    """API: Retourne tous les nœuds du réseau"""
    return jsonify({
        'nodes': transport.get_all_nodes_by_type(),
        'total': len(transport.G.nodes())
    })

@app.route('/api/nodes/<node_type>')
def nodes_by_type(node_type):
    """API: Retourne les nœuds filtrés par type"""
    valid_types = ['depart', 'arrivee', 'intermediaire']
    if node_type not in valid_types:
        return jsonify({"error": f"Type invalide. Types valides: {valid_types}"}), 400
    
    nodes = transport.get_all_nodes_by_type(node_type)
    return jsonify({
        'nodes': nodes,
        'type': node_type,
        'total': len(nodes)
    })

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
            "version": "4.0",
            "network_stats": stats,
            "diagnostics": {
                "graph_connected": nx.is_weakly_connected(transport.G),
                "has_path": nx.has_path(transport.G, 'RP_VICTOIRE', 'GARE_CENTRALE'),
                "nodes_count": stats['nombre_noeuds'],
                "edges_count": stats['nombre_aretes'],
                "total_possible_paths": len(list(nx.all_simple_paths(transport.G, 'RP_VICTOIRE', 'GARE_CENTRALE', cutoff=10)))
            }
        })
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": f"Erreur système: {str(e)}"
        }), 500

# --- GESTION DES ERREURS ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint non trouvé",
        "available_endpoints": [
            "/api/network", 
            "/api/shortest-path/{distance|temps}", 
            "/api/all-paths", 
            "/api/all-simple-paths", 
            "/api/stats", 
            "/api/nodes",
            "/api/nodes/{depart|arrivee|intermediaire}",
            "/api/node/{node_id}",
            "/api/health"
        ]
    }), 404

# --- LANCEMENT DE L'APPLICATION ---

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Démarrage de l'application Flask sur le port {port}. DEBUG={debug}")
    print(f"Réseau créé avec {