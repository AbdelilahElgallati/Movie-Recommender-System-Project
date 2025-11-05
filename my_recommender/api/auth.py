from flask import Blueprint, jsonify, request, current_app
from ..utils.user_manager import (
    load_users, save_users, get_next_available_user_id,
    load_user_ratings 
)
from ..utils.data_helpers import enrich_recs_with_posters

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['POST'])
def signup_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400
        
    username = data['username']
    password = data['password']
    
    users = load_users()
    
    for user in users:
        if user['username'] == username:
            return jsonify({"error": "Username already exists"}), 409
            
    new_user_id = int(get_next_available_user_id())
    new_user = {
        "id": new_user_id,
        "username": username,
        "password": password 
    }
    
    users.append(new_user)
    save_users(users)
    
    print(f"New user created: {username} (ID: {new_user_id})")
    return jsonify({
        "message": "User created successfully", 
        "userId": new_user_id,
        "username": username
    }), 201

@bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400
        
    username = data['username']
    password = data['password']
    
    users = load_users()
    
    for user in users:
        if user['username'] == username:
            if user['password'] == password:
                print(f"User logged in: {username} (ID: {user['id']})")
                return jsonify({
                    "message": "Login successful", 
                    "userId": user['id'],
                    "username": user['username']
                })
            else:
                return jsonify({"error": "Invalid username or password"}), 401
    
    return jsonify({"error": "Invalid username or password"}), 401

@bp.route('/user/<int:user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    try:
        ratings_data = load_user_ratings()
        user_ratings_dict = ratings_data.get(str(user_id), {})

        if not user_ratings_dict:
            return jsonify([])

        all_movies_df = current_app.all_movies_df
        
        rated_movies = []
        for movie_id_str, rating in user_ratings_dict.items():
            try:
                movie_id = int(movie_id_str)
                movie_row = all_movies_df[all_movies_df['movie_id'] == movie_id]
                if not movie_row.empty:
                    movie_data = movie_row.iloc[0]
                    rated_movies.append({
                        'movie_id': movie_id,
                        'id': movie_id,  # Pour la compatibilité
                        'title': movie_data['movie_title'],
                        'rating': float(rating),
                        'poster_url': movie_data.get('poster_url', ''),
                        'genres': movie_data.get('genres_list', [])
                    })
            except (ValueError, TypeError) as e:
                print(f"Error processing movie_id {movie_id_str}: {e}")
                continue

        return jsonify(rated_movies)
        
    except Exception as e:
        print(f"Error in /api/user/ratings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500