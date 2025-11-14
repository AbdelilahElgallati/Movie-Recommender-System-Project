"""
Database manager - MongoDB operations wrapper
Replaces the old JSON-based user_manager.py
"""
from typing import Optional, List, Dict, Any
from flask import current_app
from ..database.models import User, Movie, Rating
from ..database.connection import get_db

def get_database():
    """Get database instance from Flask app context"""
    try:
        if hasattr(current_app, 'mongodb') and current_app.mongodb is not None:
            return current_app.mongodb
        return get_db()
    except Exception as e:
        # If Flask app context is not available, try direct connection
        from ..database.connection import get_db
        return get_db()

# ==================== USER OPERATIONS ====================

def load_users() -> List[Dict]:
    """Load all users from MongoDB"""
    db = get_database()
    return list(db.users.find({}, {'_id': 0, 'password': 0}))

def save_users(users_data: List[Dict]) -> bool:
    """Save users to MongoDB (for migration purposes)"""
    db = get_database()
    if not users_data:
        return False
    
    try:
        for user in users_data:
            db.users.update_one(
                {'user_id': user['id']},
                {'$set': {
                    'user_id': user['id'],
                    'username': user['username'],
                    'password': user.get('password', ''),
                    'updated_at': user.get('updated_at')
                }},
                upsert=True
            )
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def get_next_available_user_id() -> int:
    """Get next available user_id"""
    db = get_database()
    return User.get_next_user_id(db)

def find_user_by_username(username: str) -> Optional[Dict]:
    """Find user by username"""
    db = get_database()
    user = User.find_by_username(db, username)
    if user:
        user.pop('_id', None)
        user.pop('password', None)
    return user

def find_user_by_id(user_id: int) -> Optional[Dict]:
    """Find user by user_id"""
    db = get_database()
    user = User.find_by_id(db, user_id)
    if user:
        user.pop('_id', None)
        user.pop('password', None)
    return user

def create_user(username: str, password: str) -> Dict:
    """Create a new user"""
    db = get_database()
    user_id = get_next_available_user_id()
    user_data = User.create(user_id, username, password)
    user = User.create_user(db, user_data)
    user.pop('_id', None)
    user.pop('password', None)
    return user

def verify_user_credentials(username: str, password: str) -> Optional[Dict]:
    """Verify user credentials"""
    db = get_database()
    user = User.find_by_username(db, username)
    if user and user.get('password') == password:
        user.pop('_id', None)
        user.pop('password', None)
        return user
    return None

# ==================== RATING OPERATIONS ====================

def load_user_ratings() -> Dict[str, Dict[str, float]]:
    """Load all user ratings in the old format (for compatibility)"""
    db = get_database()
    ratings = db.ratings.find({})
    
    result = {}
    for rating in ratings:
        user_id = str(rating['user_id'])
        movie_id = str(rating['movie_id'])
        if user_id not in result:
            result[user_id] = {}
        result[user_id][movie_id] = rating['rating']
    
    return result

def save_user_ratings(ratings_data: Dict[str, Dict[str, float]]) -> bool:
    """Save user ratings (for migration purposes)"""
    db = get_database()
    try:
        for user_id_str, movies in ratings_data.items():
            user_id = int(user_id_str)
            for movie_id_str, rating in movies.items():
                movie_id = int(movie_id_str)
                Rating.create_or_update_rating(db, user_id, movie_id, float(rating))
        return True
    except Exception as e:
        print(f"Error saving ratings: {e}")
        return False

def get_user_ratings(user_id: int) -> List[Dict]:
    """Get all ratings for a user"""
    db = get_database()
    return Rating.find_by_user(db, user_id)

def save_rating(user_id: int, movie_id: int, rating: float) -> Dict:
    """Save or update a rating"""
    db = get_database()
    return Rating.create_or_update_rating(db, user_id, movie_id, rating)

def get_user_rating_count(user_id: int) -> int:
    """Get count of ratings for a user"""
    db = get_database()
    return Rating.get_user_rating_count(db, user_id)

def get_user_ratings_with_movies(user_id: int) -> List[Dict]:
    """Get user ratings with movie details"""
    db = get_database()
    return Rating.get_user_ratings_with_movies(db, user_id)

# ==================== MOVIE OPERATIONS ====================

def get_movie_by_id(movie_id: int) -> Optional[Dict]:
    """Get movie by movie_id"""
    db = get_database()
    movie = Movie.find_by_id(db, movie_id)
    if movie:
        movie.pop('_id', None)
    return movie

def search_movies(query: str, limit: int = 20) -> List[Dict]:
    """Search movies by title"""
    db = get_database()
    movies = Movie.search(db, query, limit)
    for movie in movies:
        movie.pop('_id', None)
    return movies

def create_movie(movie_data: Dict) -> Dict:
    """Create a new movie"""
    db = get_database()
    movie = Movie.create_movie(db, movie_data)
    if movie:
        movie.pop('_id', None)
    return movie

def bulk_insert_movies(movies: List[Dict]) -> int:
    """Bulk insert movies"""
    db = get_database()
    return Movie.bulk_insert(db, movies)

