import folium
import pandas as pd
import requests
from folium.plugins import MarkerCluster

def get_hydro_data():
    """Récupère les données des centrales hydrauliques depuis l'API EDF."""
    url = "https://opendata.edf.fr/api/explore/v2.1/catalog/datasets/centrales-de-production-hydraulique-de-edf-sa/records"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        total_count = response.json().get('total_count', 0)
        
        response = requests.get(url, params={"limit": total_count})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API hydraulique: {e}")
        return None

def get_nuclear_data():
    """Récupère les données des centrales nucléaires depuis l'API EDF."""
    url = "https://opendata.edf.fr/api/explore/v2.1/catalog/datasets/centrales-de-production-nucleaire-edf/records"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        total_count = response.json().get('total_count', 0)
        
        response = requests.get(url, params={"limit": total_count})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API nucléaire: {e}")
        return None

def get_flamme_data():
    """Récupère les données des centrales thermiques à flamme depuis l'API EDF."""
    url = "https://opendata.edf.fr/api/explore/v2.1/catalog/datasets/centrales-de-production-thermique-a-flamme-d-edf-sa-fioul-gaz-charbon/records"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        total_count = response.json().get('total_count', 0)
        
        response = requests.get(url, params={"limit": total_count})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API thermique: {e}")
        return None

def create_hydro_dataframe(data):
    if not data or 'results' not in data:
        return None
    
    centrales = []
    for centrale in data['results']:
        point_gps = centrale.get('point_gps_wsg_84', {})
        lat = point_gps.get('lat') if isinstance(point_gps, dict) else None
        lon = point_gps.get('lon') if isinstance(point_gps, dict) else None
        
        centrale_info = {
            'Centrale': centrale.get('centrale'),
            'Type': 'Hydraulique',
            'Filière': centrale.get('filiere'),
            'Catégorie': centrale.get('categorie_centrale'),
            'Puissance (MW)': centrale.get('puissance_installee'),
            'Département': centrale.get('departement'),
            'Commune': centrale.get('commune'),
            'Année mise en service': centrale.get('annee_de_mise_en_service'),
            'Latitude': lat,
            'Longitude': lon
        }
        centrales.append(centrale_info)
    
    return pd.DataFrame(centrales)

def create_nuclear_dataframe(data):
    if not data or 'results' not in data:
        return None
    
    centrales = []
    for centrale in data['results']:
        point_gps = centrale.get('point_gps_wsg84', {})
        lat = point_gps.get('lat') if isinstance(point_gps, dict) else None
        lon = point_gps.get('lon') if isinstance(point_gps, dict) else None
        
        sous_filiere = centrale.get('sous_filiere')
        print(f"Catégorie nucléaire trouvée : {sous_filiere}")
        
        centrale_info = {
            'Centrale': centrale.get('centrale'),
            'Type': 'Nucléaire',
            'Filière': centrale.get('filiere'),
            'Catégorie': sous_filiere,
            'Puissance (MW)': centrale.get('puissance_installee'),
            'Combustible': centrale.get('combustible'),
            'Date mise en service': centrale.get('date_de_mise_en_service_industrielle'),
            'Région': centrale.get('region'),
            'Latitude': lat,
            'Longitude': lon
        }
        centrales.append(centrale_info)
    
    df = pd.DataFrame(centrales)
    print("\nCatégories uniques de réacteurs nucléaires:")
    print(df['Catégorie'].unique())
    return df

def create_flamme_dataframe(data):
    if not data or 'results' not in data:
        return None
    
    centrales = []
    for centrale in data['results']:
        point_gps = centrale.get('point_gps_wsg84', {})
        lat = point_gps.get('lat') if isinstance(point_gps, dict) else None
        lon = point_gps.get('lon') if isinstance(point_gps, dict) else None
        
        centrale_info = {
            'Centrale': centrale.get('centrale'),
            'Tranche': centrale.get('tranche'),
            'Filière': centrale.get('filiere'),
            'Sous-filière': centrale.get('sous_filiere'),
            'Combustible': centrale.get('combustible'),
            'Puissance (MW)': centrale.get('puissance_installee'),
            'Date mise en service': centrale.get('date_de_mise_en_service_industrielle'),
            'Région': centrale.get('region'),
            'Département': centrale.get('departement'),
            'Commune': centrale.get('commune'),
            'Latitude': lat,
            'Longitude': lon
        }
        centrales.append(centrale_info)
    
    return pd.DataFrame(centrales)

def create_combined_map(df_hydro, df_nuclear, df_flamme):
    """Crée une carte interactive combinant les centrales hydrauliques, nucléaires et thermiques."""
    # Créer la carte centrée sur la France
    m = folium.Map(location=[46.6034, 1.8883], zoom_start=6)
    
    # Définir les couleurs pour les centrales hydrauliques
    hydro_colors = {
        'Lac': 'blue',
        'Fil de l\'eau': 'green',
        'Eclusée': 'orange',
        'Pompage pur': 'red',
        'Pompage mixte': 'purple'
    }
    
    # Obtenir la liste unique des sous-filières nucléaires
    sous_filieres = sorted(df_nuclear['Catégorie'].unique())
    
    # Créer un dictionnaire de couleurs pour les sous-filières nucléaires
    nuclear_colors = {}
    nuclear_available_colors = ['red', 'darkred', 'purple', 'darkpurple']
    for i, sous_filiere in enumerate(sous_filieres):
        nuclear_colors[sous_filiere] = nuclear_available_colors[i % len(nuclear_available_colors)]
    
    # Afficher les associations sous-filière-couleur
    print("\nCouleurs attribuées aux sous-filières nucléaires:")
    for sous_filiere, color in nuclear_colors.items():
        print(f"- {sous_filiere}: {color}")
    
    # Obtenir la liste unique des combustibles pour les centrales thermiques
    combustibles = sorted(df_flamme['Combustible'].unique())
    
    # Créer un dictionnaire de couleurs pour les combustibles
    available_colors = ['green', 'orange', 'pink', 'lightred', 'beige', 'lightgreen']
    flamme_colors = {combustible: available_colors[i % len(available_colors)] 
                    for i, combustible in enumerate(combustibles)}
    
    # Créer les groupes principaux
    hydro_group = folium.FeatureGroup(name="Centrales Hydrauliques")
    nuclear_group = folium.FeatureGroup(name="Centrales Nucléaires")
    flamme_group = folium.FeatureGroup(name="Centrales Thermiques")
    
    # Créer les sous-groupes pour l'hydraulique
    hydro_clusters = {}
    for category in df_hydro['Catégorie'].unique():
        hydro_clusters[category] = MarkerCluster(name=f"Hydraulique - {category}")
    
    # Créer les sous-groupes pour le nucléaire
    nuclear_clusters = {}
    for reactor_type in df_nuclear['Catégorie'].unique():
        nuclear_clusters[reactor_type] = MarkerCluster(name=f"Nucléaire - {reactor_type}")
    
    # Créer les sous-groupes pour le thermique
    flamme_clusters = {}
    for combustible in combustibles:
        nom_groupe = "Thermique - Mixte" if '/' in combustible else f"Thermique - {combustible}"
        flamme_clusters[combustible] = MarkerCluster(name=nom_groupe)
    
    # Ajouter les marqueurs hydrauliques
    for idx, row in df_hydro.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            category = row['Catégorie']
            color = hydro_colors.get(category, 'blue')
            name = row['Centrale']
            
            popup_content = f"""
                <b>{name}</b><br>
                Type: {row['Type']}<br>
                Filière: {row['Filière']}<br>
                Puissance: {row['Puissance (MW)']} MW<br>
                Catégorie: {category}<br>
                Département: {row['Département']}<br>
                Commune: {row['Commune']}<br>
                Année de mise en service: {row['Année mise en service']}
            """
            
            marker = folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=name,
                icon=folium.Icon(color=color, icon='tint')
            )
            
            if category in hydro_clusters:
                marker.add_to(hydro_clusters[category])
    
    # Ajouter les marqueurs nucléaires
    for idx, row in df_nuclear.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            reactor_type = row['Catégorie']
            color = nuclear_colors.get(reactor_type, 'red')
            name = row['Centrale']
            
            popup_content = f"""
                <b>{name}</b><br>
                Type: {row['Type']}<br>
                Filière: {row['Filière']}<br>
                Puissance: {row['Puissance (MW)']} MW<br>
                Type de réacteur: {reactor_type}<br>
                Combustible: {row['Combustible']}<br>
                Région: {row['Région']}<br>
                Date de mise en service: {row['Date mise en service']}
            """
            
            marker = folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=name,
                icon=folium.Icon(color=color, icon='bolt', prefix='fa')
            )
            
            if reactor_type in nuclear_clusters:
                marker.add_to(nuclear_clusters[reactor_type])
    
    # Ajouter les marqueurs thermiques
    for idx, row in df_flamme.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            combustible = row['Combustible']
            color = flamme_colors[combustible]
            name = f"{row['Centrale']} - {row['Tranche']}"
            
            popup_content = f"""
                <b>{name}</b><br>
                Type: {row['Filière']}<br>
                Sous-type: {row['Sous-filière']}<br>
                Combustible: {combustible}<br>
                Puissance: {row['Puissance (MW)']} MW<br>
                Région: {row['Région']}<br>
                Département: {row['Département']}<br>
                Commune: {row['Commune']}<br>
                Date de mise en service: {row['Date mise en service']}
            """
            
            icon = 'fire' if '/' not in combustible else 'industry'
            marker = folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=name,
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            )
            
            if combustible in flamme_clusters:
                marker.add_to(flamme_clusters[combustible])
    
    # Ajouter tous les clusters à leurs groupes respectifs
    for cluster in hydro_clusters.values():
        cluster.add_to(hydro_group)
    
    for cluster in nuclear_clusters.values():
        cluster.add_to(nuclear_group)
    
    for cluster in flamme_clusters.values():
        cluster.add_to(flamme_group)
    
    # Ajouter les groupes principaux à la carte
    hydro_group.add_to(m)
    nuclear_group.add_to(m)
    flamme_group.add_to(m)
    
    # Ajouter le contrôle des couches
    folium.LayerControl().add_to(m)
    
    # Ajouter une légende combinée
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; 
                z-index:9999; 
                background-color: white;
                padding: 10px;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        <p style="margin-bottom: 5px;"><strong>Légende</strong></p>
        
        <div style="margin-bottom: 10px;">
            <p style="margin: 0 0 5px 0;"><strong>Centrales Hydrauliques</strong></p>
    '''
    
    # Ajouter les couleurs des centrales hydrauliques
    for category, color in hydro_colors.items():
        legend_html += f'''
            <div style="margin: 2px 0;">
                <i class="fa fa-tint" style="color: {color};"></i>
                {category}
            </div>
        '''
    
    legend_html += '''
        </div>
        <div style="margin-bottom: 10px;">
            <p style="margin: 0 0 5px 0;"><strong>Centrales Nucléaires</strong></p>
    '''
    
    # Ajouter les couleurs des centrales nucléaires
    for reactor_type, color in nuclear_colors.items():
        legend_html += f'''
            <div style="margin: 2px 0;">
                <i class="fa fa-bolt" style="color: {color};"></i>
                {reactor_type}
            </div>
        '''
    
    legend_html += '''
        </div>
        <div>
            <p style="margin: 0 0 5px 0;"><strong>Centrales Thermiques</strong></p>
    '''
    
    # Ajouter les couleurs des centrales thermiques
    for combustible, color in flamme_colors.items():
        icon = 'fire' if '/' not in combustible else 'industry'
        legend_html += f'''
            <div style="margin: 2px 0;">
                <i class="fa fa-{icon}" style="color: {color};"></i>
                {combustible}
            </div>
        '''
    
    legend_html += '''
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def main():
    # Récupérer les données hydrauliques
    hydro_data = get_hydro_data()
    if hydro_data:
        print(f"Nombre total de centrales hydrauliques: {hydro_data.get('total_count', 0)}")
        
        # Créer le DataFrame hydraulique
        df_hydro = create_hydro_dataframe(hydro_data)
        if df_hydro is None:
            print("Erreur lors de la création du DataFrame hydraulique")
            return
    else:
        print("Erreur lors de la récupération des données hydrauliques")
        return
    
    # Récupérer les données nucléaires
    nuclear_data = get_nuclear_data()
    if nuclear_data:
        print(f"Nombre total de centrales nucléaires: {nuclear_data.get('total_count', 0)}")
        
        # Créer le DataFrame nucléaire
        df_nuclear = create_nuclear_dataframe(nuclear_data)
        if df_nuclear is None:
            print("Erreur lors de la création du DataFrame nucléaire")
            return
    else:
        print("Erreur lors de la récupération des données nucléaires")
        return
    
    # Récupérer les données thermiques
    flamme_data = get_flamme_data()
    if flamme_data:
        print(f"Nombre total de centrales thermiques: {flamme_data.get('total_count', 0)}")
        
        # Créer le DataFrame thermique
        df_flamme = create_flamme_dataframe(flamme_data)
        if df_flamme is None:
            print("Erreur lors de la création du DataFrame thermique")
            return
    else:
        print("Erreur lors de la récupération des données thermiques")
        return
    
    print("\nCréation de la carte combinée...")
    
    # Créer la carte
    m = create_combined_map(df_hydro, df_nuclear, df_flamme)
    
    # Sauvegarder la carte
    m.save('carte_complete.html')
    print("Carte créée ! Ouvrez le fichier 'carte_complete.html' dans votre navigateur pour voir la carte interactive.")

if __name__ == "__main__":
    main()
