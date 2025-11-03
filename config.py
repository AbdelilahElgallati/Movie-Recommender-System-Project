# config.py
import os

class Config:
    # Chemins des données
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_PATH = os.path.join(BASE_DIR, 'Dataset/u.item')
    RATINGS_PATH = os.path.join(BASE_DIR, 'Dataset/u.data')
    USERS_PATH = os.path.join(BASE_DIR, 'Dataset/u.user')
    DATA_PATH_TMDB = os.path.join(BASE_DIR, 'Dataset/tmdb_5000_movies.csv')
    USERS_FILE_PATH = os.path.join(BASE_DIR, 'users.json')
    
    # Chemin pour le nouveau fichier de données enrichies
    ENRICHED_MOVIES_PATH = os.path.join(BASE_DIR, 'Dataset/movies_enriched.csv')

    # Chemins des modèles
    HYBRID_MODEL_PATH = os.path.join(BASE_DIR, 'models/hybrid_system.pkl')
    CONTENT_MODEL_PATH = os.path.join(BASE_DIR, 'models/content_model.pkl')

    # Configuration API
    # IMDB_API_BASE_URL = 'https://imdbapi.dev/api'
    # TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
    API_Read_Access_Token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1NGU3ZTE0MmEwNTU2MGRmMjUzZDgzY2Q3MmQyMjYzMyIsIm5iZiI6MTc1NDE2MDQzNi44NjA5OTk4LCJzdWIiOiI2ODhlNWQzNGQxNThkZGRjZWRmM2RlZjEiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.1cbitsYIg3z0ra_pqZibmgg3hz58GtmnobzzjmOnk0c'
    TMDB_API_KEY = '54e7e142a05560df253d83cd72d22633'  
    TMDB_API_BASE_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
    
    # Genres
    GENRE_COLS = [
        'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 
        'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 
        'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]