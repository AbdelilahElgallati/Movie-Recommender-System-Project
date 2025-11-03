from flask import Blueprint, jsonify, request, current_app
import pandas as pd

from config import Config 
from ..models.hybrid import HybridRecommender 
from ..utils.data_helpers import enrich_recs_with_posters

bp = Blueprint('recommendations', __name__)

@bp.route('/recommend', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(data['user_id'])
        
        # --- Get models/data from current_app ---
        hybrid_system = current_app.hybrid_system
        all_movies_df = current_app.all_movies_df

        recs, explanation = hybrid_system.recommend(user_id, n=20, explain=True)
        
        # --- Pass all_movies_df to the helper ---
        formatted_recs = enrich_recs_with_posters(
            recs, all_movies_df, 0, 1, {"score": 2, "model_used": 3}
        )
        return jsonify({ "recommendations": formatted_recs, "explanation": explanation })
    except Exception as e:
        print(f"Error in /api/recommend: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/similar/<path:movie_title>', methods=['GET'])
def get_similar_movies(movie_title):
    try:
        # --- Get models/data from current_app ---
        content_model = current_app.content_model
        all_movies_df = current_app.all_movies_df
        
        recs = content_model.recommend(movie_title, n=10)
        if not recs:
            return jsonify({"error": f"Movie '{movie_title}' not found."}), 404
            
        # --- Pass all_movies_df to the helper ---
        formatted_recs = enrich_recs_with_posters(recs, all_movies_df, 0, 1, {"score": 2})
        return jsonify(formatted_recs)
    except Exception as e:
        print(f"Error in /api/similar: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/recommend/genre/<string:genre_name>', methods=['GET'])
def get_genre_recommendations(genre_name):
    # Utilisation de Config.GENRE_COLS
    if genre_name not in Config.GENRE_COLS:
        return jsonify({"error": "Genre not found"}), 404
    try:
        # --- Get models/data from current_app ---
        hybrid_system = current_app.hybrid_system
        all_movies_df = current_app.all_movies_df
        
        popular_movies_df = hybrid_system.popularity_model.popular_movies
        popular_with_details = pd.merge(popular_movies_df, all_movies_df, on='movie_id', how='left')
        genre_filtered_df = popular_with_details[popular_with_details[genre_name] == 1]
        top_n_genre = genre_filtered_df.head(10)
        recs_list = [
            (row['movie_id'], row['movie_title_x'], row['weighted_score'])
            for _, row in top_n_genre.iterrows()
        ]
        # --- Pass all_movies_df to the helper ---
        formatted_recs = enrich_recs_with_posters(recs_list, all_movies_df, 0, 1, {"score": 2})
        return jsonify(formatted_recs)
    except Exception as e:
        print(f"Error in /api/recommend/genre: {e}")
        return jsonify({"error": str(e)}), 500
    
@bp.route('/recommend/features', methods=['POST'])
def get_feature_recommendations():
    data = request.get_json()
    if not data or 'liked_movies' not in data:
        return jsonify({"error": "liked_movies list is required"}), 400
    try:
        # --- Get models/data from current_app ---
        content_model = current_app.content_model
        all_movies_df = current_app.all_movies_df
        
        liked_movies_list = data['liked_movies']
        user_rated_movies = [(m['title'], float(m['rating'])) for m in liked_movies_list]
        recs = content_model.recommend_for_user(user_rated_movies, n=20)
        
        # --- Pass all_movies_df to the helper ---
        formatted_recs = enrich_recs_with_posters(recs, all_movies_df, 0, 1, {"score": 2})
        return jsonify(formatted_recs)
    except Exception as e:
        print(f"Error in /api/recommend/features: {e}")
        return jsonify({"error": str(e)}), 500
    
    
@bp.route('/rate', methods=['POST'])
def rate_movie():
    data = request.get_json()
    if not data or 'user_id' not in data or 'movie_id' not in data or 'rating' not in data:
        return jsonify({"error": "user_id, movie_id, and rating are required"}), 400

    try:
        user_id = int(data['user_id'])
        movie_id = int(data['movie_id'])
        rating = float(data['rating'])
        timestamp = int(time.time())

        # Format: user_id \t movie_id \t rating \t timestamp
        new_rating_line = f"\n{user_id}\t{movie_id}\t{rating}\t{timestamp}"

        # Append the new rating to the u.data file
        # This is a simple way to persist ratings without a database.
        with open(Config.RATINGS_PATH, 'a') as f:
            f.write(new_rating_line)

        # Note: The in-memory model (current_app.hybrid_system) will not 
        # reflect this new rating until the server is restarted.
        # This is acceptable for this project's scope.
        
        return jsonify({
            "success": True, 
            "message": f"Rating {rating} for movie {movie_id} by user {user_id} saved."
        }), 201

    except Exception as e:
        print(f"Error in /api/rate: {e}")
        return jsonify({"error": str(e)}), 500