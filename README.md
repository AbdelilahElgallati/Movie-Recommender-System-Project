# MovieRec - Système de Recommandation de Films Hybride

MovieRec est une application web full-stack (Flask et React) qui fournit des recommandations de films personnalisées. Le cœur du projet est un **moteur de recommandation hybride** qui combine des approches de filtrage collaboratif, de filtrage basé sur le contenu et de popularité pour s'adapter dynamiquement au profil de chaque utilisateur.

## 🚀 Fonctionnalités Clés

  * **Moteur Hybride Adaptatif (Switching) :** Le système sélectionne la meilleure stratégie de recommandation en fonction du nombre de notes de l'utilisateur (cold start, utilisateur modéré, utilisateur actif).
  * **Authentification Utilisateur :** Système complet de création de compte et de connexion pour gérer les profils utilisateurs (via `users.json`).
  * **Notation de Films :** Les utilisateurs peuvent noter les films de 1 à 5 étoiles, et ces notes sont persistantes (`u.data`).
  * **Exploration et Découverte :**
      * Recherche de films par titre.
      * Filtrage par genre.
      * Pagination pour naviguer dans le catalogue.
  * **Pages Détaillées :** Affichage du synopsis, du poster, du casting, de la note IMDb et des **films similaires** (basés sur le contenu).
  * **Profil Utilisateur :** Une page dédiée où les utilisateurs connectés reçoivent leurs recommandations personnalisées et voient quelle stratégie hybride a été utilisée pour les générer.

## 🧠 Comment ça Marche : Le Moteur Hybride

Le projet utilise une stratégie de "switching" (commutation) pour déterminer quelles recommandations montrer, en se basant sur la logique définie dans `my_recommender/models/hybrid.py` :

1.  **Nouvel Utilisateur (0 note) - *Cold Start***

      * **Stratégie :** 100% **Modèle de Popularité**.
      * **Logique :** Affiche les films les mieux notés et les plus populaires (basé sur un score pondéré) pour engager l'utilisateur.

2.  **Utilisateur Novice (1-10 notes)**

      * **Stratégie :** 70% **Basé sur le Contenu** + 30% **Popularité**.
      * **Logique :** Analyse les genres/tags des films que l'utilisateur a aimés pour trouver des films similaires. La popularité assure la pertinence des suggestions.

3.  **Utilisateur Modéré (11-30 notes)**

      * **Stratégie :** 60% **Filtrage Collaboratif** + 30% **Basé sur le Contenu** + 10% **Popularité**.
      * **Logique :** Commence à utiliser les schémas d'utilisateurs similaires (collaboratif) tout en gardant une forte composante de contenu et une base de popularité.

4.  **Utilisateur Actif (31+ notes)**

      * **Stratégie :** 80% **Filtrage Collaboratif** + 20% **Basé sur le Contenu**.
      * **Logique :** Se fie principalement au filtrage collaboratif, qui est le plus performant avec un historique de notes suffisant. Le contenu ajoute de la diversité et de la "sérendipité".

## 🛠️ Stack Technique

  * **Backend :**
      * **Framework :** Flask
      * **Modèles ML :** Pandas, NumPy, Scikit-learn (pour TF-IDF, Cosine Similarity), NLTK (pour le stemming)
      * **Serveur :** Gunicorn (implicite pour la prod), Flask-CORS
  * **Frontend :**
      * **Bibliothèque :** React
      * **Langage :** TypeScript
      * **Styling :** Tailwind CSS
      * **Icônes :** Lucide React
  * **Données :**
      * **Dataset de base :** MovieLens 100k (`u.data`, `u.item`, `u.user`)
      * **Données enrichies :** API TMDB (via `scripts/fetch_movie_data.py`)
      * **Stockage Utilisateurs :** Fichier plat `users.json`
      * **Modèles :** Fichiers `.pkl` sérialisés (Pickle)

## 📁 Structure du Projet (Simplifiée)

```
/
├── Dataset/
│   ├── u.data          # (À télécharger)
│   ├── u.item          # (À télécharger)
│   ├── u.user          # (À télécharger)
│   └── movies_enriched.csv # (Généré par le script)
│
├── models/
│   ├── cf_model.pkl    # (Généré par le notebook)
│   ├── content_model.pkl
│   ├── hybrid_system.pkl
│   └── popularity_model.pkl
│
├── my_recommender/     # Cœur de l'application Flask
│   ├── api/            # Endpoints (auth, movies, recommendations)
│   ├── models/         # Logique Python des modèles ML
│   ├── utils/          # Helpers (API TMDB, gestion utilisateurs)
│   └── __init__.py     # Factory de l'app Flask
│
├── scripts/
│   └── fetch_movie_data.py # Script pour récupérer les posters/synopsis
│
├── src/                # Code source du Frontend React
│   ├── components/     # Composants React (Pages, MovieCard, Navbar...)
│   └── App.tsx
│
├── Complete_Hybrid_Recommender_System.ipynb # Notebook d'analyse et d'entraînement
├── config.py           # Chemins et clés API
├── requirements.txt    # Dépendances Python
├── run.py              # Point d'entrée du serveur Flask
└── users.json          # "Base de données" des utilisateurs
```

## ⚙️ Installation et Lancement

Suivez ces étapes pour lancer le projet en local.

### Prérequis

  * Python (3.9+ recommandé)
  * Node.js et npm (pour le frontend React)
  * Une clé API TMDB (The Movie Database)

### 1\. Configuration du Backend (Flask)

1.  **Clonez le dépôt :**

    ```bash
    git clone [URL_DU_PROJET]
    cd [NOM_DU_PROJET]
    ```

2.  **Créez un environnement virtuel et installez les dépendances :**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur macOS/Linux
    # ou
    venv\Scripts\activate     # Sur Windows

    pip install -r requirements.txt
    ```

3.  **Configurez votre clé API :**

      * Ouvrez le fichier `config.py`.
      * Remplacez la valeur de `TMDB_API_KEY` par votre propre clé API TMDB.

4.  **Préparez les Données et les Modèles :**

      * **Étape A :** Téléchargez le dataset **MovieLens 100k** (fichier `ml-100k.zip`).
      * Décompressez-le et placez les fichiers `u.data`, `u.item`, et `u.user` dans le dossier `Dataset/`.
      * **Étape B :** Exécutez le script pour enrichir vos données avec les posters et synopsis de TMDB. Cela créera `Dataset/movies_enriched.csv`.
        ```bash
        python scripts/fetch_movie_data.py
        ```
      * **Étape C :** Ouvrez et exécutez le notebook `Complete_Hybrid_Recommender_System.ipynb`. Cela va entraîner les modèles et sauvegarder les fichiers `.pkl` nécessaires dans le dossier `models/`.

5.  **Lancez le serveur Backend :**

    ```bash
    python run.py
    ```

    *Le serveur Flask devrait être accessible sur `http://127.0.0.1:5001`.*

### 2\. Configuration du Frontend (React)

*Note : Les fichiers de configuration du frontend (comme `package.json`, `vite.config.ts`) n'étaient pas fournis, mais voici la procédure standard pour un projet React/Vite.*

1.  **Ouvrez un *nouveau* terminal** et placez-vous dans le dossier racine du projet (là où se trouve le dossier `src/`).

2.  **Installez les dépendances Node :**

    ```bash
    npm install
    ```

3.  **Lancez le serveur de développement Frontend :**

    ```bash
    npm run dev
    ```

    *Le serveur de développement React sera accessible sur `http://localhost:5173` (ou un port similaire).*

4.  Ouvrez `http://localhost:5173` dans votre navigateur pour utiliser l'application.

## 🌐 Endpoints API (Aperçu)

  * `POST /api/login` : Connecte un utilisateur.
  * `POST /api/signup` : Crée un nouvel utilisateur.
  * `GET /api/movies` : Récupère la liste des films (avec recherche, filtre, pagination).
  * `GET /api/movie/<id>` : Récupère les détails d'un film.
  * `POST /api/rate` : Permet à un utilisateur de noter un film.
  * `POST /api/recommend` : Récupère les recommandations hybrides pour un `user_id`.
  * `GET /api/similar/<title>` : Récupère les films similaires (basé sur le contenu).
  * `GET /api/recommend/genre/<genre>` : Récupère les films populaires pour un genre.
