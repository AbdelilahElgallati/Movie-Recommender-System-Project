import pandas as pd
import re
import requests

from config import Config

def get_tmdb_id_from_url(imdb_url):
    """Extracts the IMDb ID from the URL (unchanged)"""
    if pd.isna(imdb_url) or not imdb_url:
        return None
    try:
        match = re.search(r'tt\d+', str(imdb_url))
        return match.group(0) if match else None
    except:
        return None

def fetch_tmdb_data(imdb_id):
    """Fetches movie data from TMDB using IMDb ID"""
    if not imdb_id:
        return None
    
    try:
        url = f"{Config.TMDB_API_BASE_URL}/find/{imdb_id}?api_key={Config.TMDB_API_KEY}&external_source=imdb_id"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('movie_results'):
                return data['movie_results'][0]  # First match is usually the correct one
        else:
            print(f"TMDB API error for {imdb_id}: {response.status_code}")
        return None
    except Exception as e:
        print(f"Error fetching TMDB data for {imdb_id}: {e}")
        return None

def get_movie_poster(tmdb_data):
    """Extracts the poster URL from TMDB data"""
    if not tmdb_data:
        return None
    
    try:
        poster_path = tmdb_data.get('poster_path')
        if poster_path:
            return f"{Config.TMDB_IMAGE_BASE_URL}{poster_path}"
        return None
    except Exception as e:
        print(f"Error extracting poster: {e}")
        return None

def get_movie_overview(tmdb_data):
    """Extracts the overview (description) from TMDB data"""
    if not tmdb_data:
        return "Description not available."
    
    try:
        overview = tmdb_data.get('overview')
        return overview if overview else "Description not available."
    except Exception as e:
        print(f"Error extracting overview: {e}")
        return "Description not available."