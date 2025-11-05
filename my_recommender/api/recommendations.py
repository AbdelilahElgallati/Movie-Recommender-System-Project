from flask import Blueprint, jsonify, request, current_app
import pandas as pd

from config import Config 
from ..models.hybrid import HybridRecommender 
from ..utils.data_helpers import enrich_recs_with_posters
from ..utils.user_manager import load_user_ratings, save_user_ratings

bp = Blueprint('recommendations', __name__)

@bp.route('/recommend', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(data['user_id'])
        
        hybrid_system = current_app.hybrid_system
        all_movies_df = current_app.all_movies_df

        ratings_data = load_user_ratings()
        user_ratings_dict = ratings_data.get(str(user_id), {})
        
        print(f"User {user_id} ratings from JSON: {user_ratings_dict}")
        
        user_ratings_list = []
        for movie_id_str, rating in user_ratings_dict.items():
            try:
                movie_id_int = int(movie_id_str)
                user_ratings_list.append({
                    'user_id': user_id,
                    'movie_id': movie_id_int, 
                    'rating': float(rating)
                })
            except (ValueError, TypeError):
                continue
        
        user_ratings_df = pd.DataFrame(user_ratings_list) if user_ratings_list else pd.DataFrame()
        
        original_ratings_df = pd.DataFrame()
        if not current_app.ratings_df.empty:
            original_ratings_df = current_app.ratings_df[current_app.ratings_df['user_id'] == user_id].copy()
        
        if not user_ratings_df.empty and not original_ratings_df.empty:
            newly_rated_ids = set(user_ratings_df['movie_id'])
            original_filtered = original_ratings_df[~original_ratings_df['movie_id'].isin(newly_rated_ids)]
            combined_ratings_df = pd.concat([user_ratings_df, original_filtered], ignore_index=True)
        elif not user_ratings_df.empty:
            combined_ratings_df = user_ratings_df
        else:
            combined_ratings_df = original_ratings_df
        
        category, rating_count = hybrid_system.get_user_category(user_id, combined_ratings_df)
        
        recs, explanation = hybrid_system.recommend(
            user_id, 
            n=20, 
            explain=True, 
            user_ratings_df=combined_ratings_df
        )
                
        formatted_recs = enrich_recs_with_posters(
            recs, all_movies_df, 0, 1, {"score": 2, "model_used": 3}
        )
        
        return jsonify({ 
            "recommendations": formatted_recs, 
            "explanation": explanation 
        })
        
    except Exception as e:
        print(f"Error in /api/recommend: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/similar/<path:movie_title>', methods=['GET'])
def get_similar_movies(movie_title):
    try:
        content_model = current_app.content_model
        all_movies_df = current_app.all_movies_df
        
        recs = content_model.recommend(movie_title, n=10)
        if not recs:
            return jsonify({"error": f"Movie '{movie_title}' not found."}), 404
            
        formatted_recs = enrich_recs_with_posters(recs, all_movies_df, 0, 1, {"score": 2})
        return jsonify(formatted_recs)
    except Exception as e:
        print(f"Error in /api/similar: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/recommend/genre/<string:genre_name>', methods=['GET'])
def get_genre_recommendations(genre_name):
    if genre_name not in Config.GENRE_COLS:
        return jsonify({"error": "Genre not found"}), 404
    try:
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
        content_model = current_app.content_model
        all_movies_df = current_app.all_movies_df
        
        liked_movies_list = data['liked_movies']
        user_rated_movies = [(m['title'], float(m['rating'])) for m in liked_movies_list]
        recs = content_model.recommend_for_user(user_rated_movies, n=20)
        
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
        user_id = str(data['user_id'])
        movie_id = str(data['movie_id'])
        rating = float(data['rating'])

        # --- NOUVELLE LOGIQUE JSON ---
        ratings_data = load_user_ratings()
        
        # setdefault crée la clé user_id si elle n'existe pas
        ratings_data.setdefault(user_id, {})[movie_id] = rating
        
        save_user_ratings(ratings_data)
        # --- FIN DE LA NOUVELLE LOGIQUE ---
        
        return jsonify({
            "success": True, 
            "message": f"Rating {rating} for movie {movie_id} by user {user_id} saved."
        }), 201

    except Exception as e:
        print(f"Error in /api/rate: {e}")
        return jsonify({"error": str(e)}), 500
    

# Ajouter dans recommendations.py
@bp.route('/debug/user/<int:user_id>', methods=['GET'])
def debug_user_data(user_id):
    """Endpoint de débogage pour vérifier les données utilisateur"""
    try:
        ratings_data = load_user_ratings()
        user_ratings = ratings_data.get(str(user_id), {})
        
        return jsonify({
            'user_id': user_id,
            'ratings_count': len(user_ratings),
            'ratings': user_ratings,
            'user_in_cf_model': user_id in current_app.hybrid_system.cf_model.user_ids if current_app.hybrid_system.cf_model else False
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.route('/debug/content_model', methods=['GET'])
def debug_content_model():
    """Debug endpoint pour vérifier l'état du modèle de contenu"""
    try:
        content_model = current_app.content_model
        return jsonify({
            'movies_count': len(content_model.movies_df),
            'title_to_idx_size': len(content_model.title_to_idx),
            'idx_to_title_size': len(content_model.idx_to_title),
            'sample_titles': list(content_model.title_to_idx.keys())[:10],
            'similarity_matrix_shape': content_model.similarity_matrix.shape
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500