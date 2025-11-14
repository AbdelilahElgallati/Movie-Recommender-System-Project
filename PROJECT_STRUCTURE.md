# 📁 Structure du Projet - Vue d'Ensemble

## Structure des Dossiers

```
Movie-Recommender-System-Project/
│
├── 📂 Dataset/                    # Données source
│   ├── u.data                     # Ratings MovieLens
│   ├── u.item                     # Films MovieLens
│   ├── u.user                     # Utilisateurs MovieLens
│   ├── movies_enriched.csv        # Films enrichis (TMDB)
│   └── utilitymatrix.csv          # Matrice utilitaire
│
├── 📂 models/                     # Modèles ML pré-entraînés
│   ├── cf_model.pkl              # Filtrage collaboratif
│   ├── content_model.pkl         # Basé sur le contenu
│   ├── hybrid_system.pkl         # Système hybride
│   └── popularity_model.pkl     # Modèle de popularité
│
├── 📂 my_recommender/             # Backend Python
│   ├── 📂 api/                    # Endpoints Flask
│   │   ├── auth.py               # Authentification
│   │   ├── movies.py             # Gestion des films
│   │   └── recommendations.py    # Recommandations
│   │
│   ├── 📂 database/              # MongoDB
│   │   ├── connection.py         # Connexion MongoDB
│   │   └── models.py             # Modèles de données
│   │
│   ├── 📂 models/                 # Modèles ML
│   │   ├── collaborative.py      # Filtrage collaboratif
│   │   ├── content.py            # Basé sur le contenu
│   │   ├── hybrid.py             # Système hybride
│   │   └── popularity.py        # Popularité
│   │
│   └── 📂 utils/                  # Utilitaires
│       ├── db_manager.py         # Gestion MongoDB
│       ├── data_helpers.py       # Helpers données
│       └── tmdb_api.py           # API TMDB
│
├── 📂 movie_recommender/          # Frontend React
│   ├── 📂 src/
│   │   ├── 📂 components/         # Composants React
│   │   └── App.tsx               # Application principale
│   └── package.json              # Dépendances Node
│
├── 📂 scripts/                    # Scripts utilitaires
│   ├── fetch_movie_data.py       # Enrichissement TMDB
│   ├── migrate_to_mongodb.py     # Migration MongoDB
│   └── train_models.py           # Entraînement modèles
│
├── 📄 config.py                  # Configuration
├── 📄 run.py                     # Point d'entrée Flask
├── 📄 requirements.txt           # Dépendances Python
│
└── 📄 Documentation/
    ├── README.md                  # Documentation principale
    ├── SETUP_INSTRUCTIONS.md      # Guide d'installation
    ├── COMMAND_SEQUENCE.md        # Ordre des commandes
    ├── MONGODB_SETUP.md           # Configuration MongoDB
    ├── MONGODB_CHANGES.md         # Changements MongoDB
    ├── PREPARATION_INTERVIEW.txt  # Préparation entretien
    └── PROJECT_STRUCTURE.md       # Ce fichier
```

## Fichiers Clés

### Configuration
- **`config.py`** : Configuration de l'application (MongoDB, API, chemins)
- **`requirements.txt`** : Dépendances Python
- **`run.py`** : Démarrage du serveur Flask

### Backend
- **`my_recommender/__init__.py`** : Initialisation Flask app
- **`my_recommender/api/`** : Endpoints REST API
- **`my_recommender/database/`** : Gestion MongoDB
- **`my_recommender/models/`** : Algorithmes de recommandation

### Frontend
- **`movie_recommender/src/`** : Application React/TypeScript
- **`movie_recommender/package.json`** : Dépendances Node.js

### Scripts
- **`scripts/migrate_to_mongodb.py`** : Migration des données
- **`scripts/fetch_movie_data.py`** : Enrichissement des données
- **`scripts/train_models.py`** : Entraînement des modèles

## Fichiers Supprimés (Nettoyage)

Les fichiers suivants ont été supprimés car obsolètes :
- ❌ `users.json` → Remplacé par MongoDB
- ❌ `user_ratings.json` → Remplacé par MongoDB
- ❌ `my_recommender/utils/user_manager.py` → Remplacé par `db_manager.py`
- ❌ `my_recommender/services.py` → Fichier vide

## Fichiers Ignorés (.gitignore)

- `__pycache__/` : Cache Python
- `*.pkl` : Modèles ML (trop volumineux)
- `.venv/` : Environnement virtuel
- `.env` : Variables d'environnement
- `node_modules/` : Dépendances Node.js
- `*.log` : Fichiers de log

## Points d'Entrée

### Backend
```bash
python run.py
```

### Frontend
```bash
cd movie_recommender
npm run dev
```

### Migration MongoDB
```bash
python scripts/migrate_to_mongodb.py
```

## Documentation

Consultez les fichiers suivants pour plus d'informations :
- **`SETUP_INSTRUCTIONS.md`** : Installation complète
- **`COMMAND_SEQUENCE.md`** : Ordre des commandes
- **`MONGODB_SETUP.md`** : Configuration MongoDB
- **`PREPARATION_INTERVIEW.txt`** : Préparation entretien

