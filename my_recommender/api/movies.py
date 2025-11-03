from flask import Blueprint, jsonify, request, current_app
import pandas as pd
import numpy as np 
from config import Config 
from my_recommender.utils.tmdb_api import fetch_tmdb_data, get_tmdb_id_from_url

bp = Blueprint('movies', __name__)

@bp.route('/movies', methods=['GET'])
def get_all_movies():
    search_query = request.args.get('search', '').lower()
    genre_query = request.args.get('genre', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    temp_df = current_app.all_movies_df

    if search_query:
        temp_df = temp_df[temp_df['movie_title'].str.lower().str.contains(search_query)]

    if genre_query and genre_query in Config.GENRE_COLS:
        temp_df = temp_df[temp_df[genre_query] == 1]
    
    total_movies = len(temp_df)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_df = temp_df.iloc[start:end]
    movie_list = [
        {
            "id": int(row['movie_id']), "title": row['movie_title'],
            "genres": row['genres_list'], "poster_url": row['poster_url'] 
        }
        for _, row in paginated_df.iterrows()
    ]

    return jsonify({
        "movies": movie_list, "total_movies": total_movies,
        "page": page, "total_pages": int(np.ceil(total_movies / per_page))
    })

@bp.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    try:
        movie = current_app.all_movies_df[current_app.all_movies_df['movie_id'] == movie_id].iloc[0]
        
        # Basic movie info
        result = {
            "id": int(movie['movie_id']), 
            "title": movie['movie_title'],
            "release_date": movie['release date'] if not pd.isna(movie['release date']) else "Unknown",
            "genres": movie['genres_list'],
            "imdb_url": movie['IMDb URL'] if not pd.isna(movie['IMDb URL']) else "",
        }
        
        # Try to get poster URL
        poster_url = movie['poster_url']
        if pd.isna(poster_url) or not poster_url:
            # Create a placeholder image based on movie title
            poster_url = f"https://placehold.co/500x750/1e293b/94a3b8?text={movie['movie_title'].replace(' ', '+')}"
        result["poster_url"] = poster_url
        
        # Try to get overview
        overview = movie['overview']
        if pd.isna(overview) or not overview or overview == "Description not available.":
            overview = f"{movie['movie_title']} is a film from {movie['release date'] if not pd.isna(movie['release date']) else 'unknown year'}. Genres: {', '.join(movie['genres_list'])}."
        result["overview"] = overview
        
        # Try to fetch fresh IMDb data
        imdb_id = get_tmdb_id_from_url(movie['IMDb URL'])
        if imdb_id:
            try:
                imdb_data = fetch_tmdb_data(imdb_id)
                if imdb_data:
                    if imdb_data.get('rating'):
                        result['imdb_rating'] = imdb_data['rating']
                    if imdb_data.get('year'):
                        result['year'] = imdb_data['year']
                    if imdb_data.get('runtime'):
                        result['runtime'] = imdb_data['runtime']
                    if imdb_data.get('director'):
                        result['director'] = imdb_data['director']
                    if imdb_data.get('cast'):
                        result['cast'] = imdb_data['cast'][:5]
            except Exception as e:
                print(f"Could not fetch fresh IMDb data for {imdb_id}: {e}")

        
        return jsonify(result)
    except IndexError:
        return jsonify({"error": "Movie not found"}), 404
    except Exception as e:
        print(f"Error in /api/movie: {e}")
        return jsonify({"error": str(e)}), 500

@bp.app_errorhandler(404)
def handle_not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@bp.app_errorhandler(500)
def handle_internal_error(error):
    # Vous pouvez logger l'erreur ici
    return jsonify({"error": "An internal server error occurred"}), 500