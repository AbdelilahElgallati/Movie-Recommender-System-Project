from flask import Blueprint, jsonify, request, current_app
from ..utils.db_manager import (
    find_user_by_username, create_user, verify_user_credentials,
    get_user_ratings_with_movies
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
    
    # Check if username already exists
    existing_user = find_user_by_username(username)
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409
    
    # Create new user
    try:
        new_user = create_user(username, password)
        print(f"New user created: {username} (ID: {new_user['user_id']})")
        return jsonify({
            "message": "User created successfully", 
            "userId": new_user['user_id'],
            "username": new_user['username']
        }), 201
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({"error": "Failed to create user"}), 500

@bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400
        
    username = data['username']
    password = data['password']
    
    # Verify credentials
    user = verify_user_credentials(username, password)
    if user:
        print(f"User logged in: {username} (ID: {user['user_id']})")
        return jsonify({
            "message": "Login successful", 
            "userId": user['user_id'],
            "username": user['username']
        })
    
    return jsonify({"error": "Invalid username or password"}), 401

@bp.route('/user/<int:user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    try:
        # Get ratings with movie details from MongoDB
        ratings_with_movies = get_user_ratings_with_movies(user_id)
        
        if not ratings_with_movies:
            return jsonify([])
        
        # Format response
        rated_movies = []
        for rating in ratings_with_movies:
            movie = rating.get('movie', {})
            rated_movies.append({
                'movie_id': rating['movie_id'],
                'id': rating['movie_id'],  # Pour la compatibilité
                'title': movie.get('title', f"Movie {rating['movie_id']}"),
                'rating': float(rating['rating']),
                'poster_url': movie.get('poster_url', ''),
                'genres': movie.get('genres', movie.get('genres_list', []))
            })
        
        return jsonify(rated_movies)
        
    except Exception as e:
        print(f"Error in /api/user/ratings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500