import pandas as pd
import numpy as np
import pickle
import ast  
from flask import Flask
from flask_cors import CORS
from config import Config
from .models.content import ImprovedContentBased 
from .models.hybrid import HybridRecommender 

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app) 

    try:
        all_movies_df = pd.read_csv(Config.ENRICHED_MOVIES_PATH)
        # Prétraiter la colonne genres_list (using ast.literal_eval)
        all_movies_df['genres_list'] = all_movies_df['genres_list'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else []
        )

        all_movies_df = all_movies_df.replace({np.nan: None})
    except FileNotFoundError:
        print(f"ERREUR: Le fichier {Config.ENRICHED_MOVIES_PATH} n'existe pas.")
        print("Veuillez exécuter 'python scripts/fetch_movie_data.py' d'abord.")
        exit()

    try:
        ratings_df = pd.read_csv(Config.RATINGS_PATH, sep='\t', 
                                 names=['user_id', 'movie_id', 'rating', 'unix_timestamp'], 
                                 encoding='latin-1')
    except Exception as e:
        print(f"Erreur chargement ratings: {e}")
        ratings_df = pd.DataFrame()

    try:
        with open(Config.HYBRID_MODEL_PATH, 'rb') as f:
            hybrid_system = pickle.load(f)
        print("Hybrid Recommender loaded.")
    except Exception as e:
        print(f"Erreur chargement hybrid_system: {e}. Initialisation...")
        hybrid_system = HybridRecommender(all_movies_df, ratings_df)

    try:
        content_model = ImprovedContentBased.load_model(Config.CONTENT_MODEL_PATH)
        hybrid_system.cb_model = content_model
        print("Content-Based model loaded.")
    except Exception as e:
        print(f"Erreur chargement content_model: {e}")
        content_model = hybrid_system.cb_model
    # --- END OF DATA/MODEL LOADING ---

    # --- Attach models and data to the app instance ---
    app.all_movies_df = all_movies_df
    app.ratings_df = ratings_df
    app.hybrid_system = hybrid_system
    app.content_model = content_model

    # Enregistrer les blueprints (routes)
    from .api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    from .api.movies import bp as movies_bp
    app.register_blueprint(movies_bp, url_prefix='/api')
    
    from .api.recommendations import bp as recs_bp
    app.register_blueprint(recs_bp, url_prefix='/api')

    print("Flask app created successfully.")
    return app