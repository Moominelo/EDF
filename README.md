# 🗺️ Carte Interactive des Centrales EDF

Une application web interactive permettant de visualiser les différentes centrales électriques d'EDF en France métropolitaine.

🌐 **[Voir la carte en ligne](https://moominelo.github.io/EDF/carte_complete.html)**

## 📋 Description

Cette application affiche une carte interactive de la France avec les emplacements des :
- 💧 Centrales hydrauliques
- ⚛️ Centrales nucléaires
- 🔥 Centrales thermiques à flamme

Chaque type de centrale est représenté par des marqueurs de couleurs différentes, regroupés en clusters pour une meilleure lisibilité. Les utilisateurs peuvent filtrer les centrales par type et accéder à des informations détaillées en cliquant sur les marqueurs.

## ✨ Fonctionnalités

- 🎯 Localisation précise de toutes les centrales EDF
- 🎨 Code couleur distinct pour chaque type de centrale :
  - Centrales hydrauliques : différenciées par catégorie (Lac, Fil de l'eau, etc.)
  - Centrales nucléaires : différenciées par type de réacteur (REP 900, REP 1300)
  - Centrales thermiques : différenciées par combustible (Gaz naturel, Fioul, etc.)
- 📊 Informations détaillées pour chaque centrale :
  - Nom et type de centrale
  - Puissance installée
  - Date de mise en service
  - Localisation administrative
- 🔍 Filtres pour afficher/masquer les différents types de centrales
- 📱 Interface responsive et intuitive

## 🛠️ Technologies Utilisées

- **Python** : Langage principal
- **Bibliothèques** :
  - `folium` : Création de cartes interactives
  - `pandas` : Manipulation des données
  - `requests` : Appels API

## 📦 Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
```

2. Créez un environnement virtuel :
```bash
python -m venv .venv
```

3. Activez l'environnement virtuel :
```bash
# Windows
.venv\Scripts\activate
# Linux/MacOS
source .venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

1. Lancez le script principal :
```bash
python carte_complete.py
```

2. Ouvrez le fichier `carte_complete.html` généré dans votre navigateur

## 📊 Sources de Données

Les données sont récupérées en temps réel depuis l'API Open Data d'EDF :
- Centrales hydrauliques : [API Hydraulique EDF](https://opendata.edf.fr/explore/dataset/centrales-de-production-hydraulique-de-edf-sa)
- Centrales nucléaires : [API Nucléaire EDF](https://opendata.edf.fr/explore/dataset/centrales-de-production-nucleaire-edf)
- Centrales thermiques : [API Thermique EDF](https://opendata.edf.fr/explore/dataset/centrales-de-production-thermique-a-flamme-d-edf-sa-fioul-gaz-charbon)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Améliorer la documentation
- Soumettre des pull requests

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- Moominelo

## 🙏 Remerciements

- EDF pour la mise à disposition des données via leur API Open Data
- La communauté Python pour les excellentes bibliothèques utilisées