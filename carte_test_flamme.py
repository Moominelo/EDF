import folium
import pandas as pd
import requests
from folium.plugins import MarkerCluster

def get_flamme_data():
    """Récupère les données des centrales thermiques à flamme depuis l'API EDF."""
    url = "https://opendata.edf.fr/api/explore/v2.1/catalog/datasets/centrales-de-production-thermique-a-flamme-d-edf-sa-fioul-gaz-charbon/records"
    
    try:
        # D'abord obtenir le nombre total de centrales
        response = requests.get(url)
        response.raise_for_status()
        total_count = response.json().get('total_count', 0)
        print(f"Nombre total de centrales trouvées dans l'API: {total_count}")
        
        # Ensuite, récupérer toutes les centrales avec un limit approprié
        params = {
            "limit": total_count,
            "offset": 0
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Afficher les informations sur les centrales trouvées
        if 'results' in data:
            print("\nTypes de combustible trouvés:")
            combustibles = set(item.get('combustible') for item in data['results'])
            for combustible in sorted(combustibles):
                count = sum(1 for item in data['results'] if item.get('combustible') == combustible)
                print(f"- {combustible}: {count} centrale(s)")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API thermique: {e}")
        return None

def create_flamme_dataframe(data):
    """Crée un DataFrame pandas à partir des données des centrales thermiques."""
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

def create_flamme_map(df_flamme):
    """Crée une carte interactive des centrales thermiques."""
    # Créer la carte centrée sur la France
    m = folium.Map(location=[46.6034, 1.8883], zoom_start=6)
    
    # Obtenir la liste unique des combustibles
    combustibles = sorted(df_flamme['Combustible'].unique())
    
    # Créer un dictionnaire de couleurs pour les combustibles
    # Liste de couleurs disponibles dans Folium
    available_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                       'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 
                       'darkpurple', 'pink', 'lightblue', 'lightgreen']
    
    # Attribuer une couleur à chaque type de combustible
    flamme_colors = {}
    for i, combustible in enumerate(combustibles):
        flamme_colors[combustible] = available_colors[i % len(available_colors)]
    
    # Afficher les associations combustible-couleur
    print("\nCouleurs attribuées aux types de combustible:")
    for combustible, color in flamme_colors.items():
        print(f"- {combustible}: {color}")
    
    # Créer les groupes principaux par type de combustible
    fuel_groups = {}
    
    # Créer les groupes et ajouter les marqueurs
    for combustible in combustibles:
        count = len(df_flamme[df_flamme['Combustible'] == combustible])
        print(f"- {combustible}: {count} centrale(s)")
        
        # Créer un groupe pour ce type de combustible
        nom_groupe = "Centrales Mixtes" if '/' in combustible else f"Centrales {combustible}"
        fuel_groups[combustible] = folium.FeatureGroup(name=nom_groupe)
        
        # Créer un cluster pour ce type de combustible
        cluster = MarkerCluster()
        
        # Filtrer les centrales pour ce combustible
        df_fuel = df_flamme[df_flamme['Combustible'] == combustible]
        
        # Ajouter les marqueurs pour ce type de combustible
        for idx, row in df_fuel.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
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
                
                # Choisir une icône différente pour les centrales mixtes
                icon = 'fire' if '/' not in combustible else 'industry'
                
                marker = folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=name,
                    icon=folium.Icon(color=color, icon=icon, prefix='fa')
                )
                marker.add_to(cluster)
        
        # Ajouter le cluster au groupe du combustible
        cluster.add_to(fuel_groups[combustible])
        # Ajouter le groupe à la carte
        fuel_groups[combustible].add_to(m)
    
    # Ajouter le contrôle des couches
    folium.LayerControl().add_to(m)
    
    # Ajouter une légende
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; 
                z-index:9999; 
                background-color: white;
                padding: 10px;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        <p style="margin-bottom: 5px;"><strong>Légende des Centrales Thermiques</strong></p>
        <div style="margin-top: 5px;">
    '''
    
    # Ajouter les types de combustibles dans la légende
    for combustible in combustibles:
        color = flamme_colors[combustible]
        icon = 'fire' if '/' not in combustible else 'industry'
        legend_html += f'''
            <div style="margin: 4px 0;">
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
    # Récupérer les données
    data = get_flamme_data()
    if data:
        print(f"Nombre total de centrales thermiques: {data.get('total_count', 0)}")
        
        # Créer le DataFrame
        df_flamme = create_flamme_dataframe(data)
        if df_flamme is not None:
            print("\nCréation de la carte...")
            
            # Créer la carte
            m = create_flamme_map(df_flamme)
            
            # Sauvegarder la carte
            m.save('carte_flamme.html')
            print("Carte créée ! Ouvrez le fichier 'carte_flamme.html' dans votre navigateur pour voir la carte interactive.")
        else:
            print("Erreur lors de la création du DataFrame")
    else:
        print("Erreur lors de la récupération des données")

if __name__ == "__main__":
    main()
