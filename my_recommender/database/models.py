"""
MongoDB models/schemas for the movie recommendation system
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId

class User:
    """User model for MongoDB"""
    
    @staticmethod
    def create(user_id: int, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """Create a user document"""
        return {
            'user_id': user_id,
            'username': username,
            'password': password,  # In production, should be hashed
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            **kwargs
        }
    
    @staticmethod
    def find_by_username(db, username: str) -> Optional[Dict]:
        """Find user by username"""
        return db.users.find_one({'username': username})
    
    @staticmethod
    def find_by_id(db, user_id: int) -> Optional[Dict]:
        """Find user by user_id"""
        return db.users.find_one({'user_id': user_id})
    
    @staticmethod
    def create_user(db, user_data: Dict) -> Dict:
        """Insert a new user"""
        result = db.users.insert_one(user_data)
        return db.users.find_one({'_id': result.inserted_id})
    
    @staticmethod
    def get_next_user_id(db) -> int:
        """Get the next available user_id"""
        # Get max user_id from MovieLens dataset
        max_dataset_id = 943  # Default from MovieLens 100K
        
        # Get max user_id from database
        max_user = db.users.find_one(sort=[('user_id', -1)])
        max_db_id = max_user['user_id'] if max_user else 0
        
        return max(max_dataset_id, max_db_id) + 1


class Movie:
    """Movie model for MongoDB"""
    
    @staticmethod
    def create(movie_id: int, title: str, **kwargs) -> Dict[str, Any]:
        """Create a movie document"""
        return {
            'movie_id': movie_id,
            'title': title,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            **kwargs
        }
    
    @staticmethod
    def find_by_id(db, movie_id: int) -> Optional[Dict]:
        """Find movie by movie_id"""
        return db.movies.find_one({'movie_id': movie_id})
    
    @staticmethod
    def find_by_title(db, title: str) -> Optional[Dict]:
        """Find movie by title (exact match)"""
        return db.movies.find_one({'title': title})
    
    @staticmethod
    def search(db, query: str, limit: int = 20) -> List[Dict]:
        """Search movies by title"""
        return list(db.movies.find(
            {'title': {'$regex': query, '$options': 'i'}}
        ).limit(limit))
    
    @staticmethod
    def create_movie(db, movie_data: Dict) -> Dict:
        """Insert a new movie"""
        result = db.movies.insert_one(movie_data)
        return db.movies.find_one({'_id': result.inserted_id})
    
    @staticmethod
    def bulk_insert(db, movies: List[Dict]) -> int:
        """Bulk insert movies"""
        if not movies:
            return 0
        result = db.movies.insert_many(movies, ordered=False)
        return len(result.inserted_ids)
    
    @staticmethod
    def update_movie(db, movie_id: int, update_data: Dict) -> bool:
        """Update movie data"""
        update_data['updated_at'] = datetime.utcnow()
        result = db.movies.update_one(
            {'movie_id': movie_id},
            {'$set': update_data}
        )
        return result.modified_count > 0


class Rating:
    """Rating model for MongoDB"""
    
    @staticmethod
    def create(user_id: int, movie_id: int, rating: float, **kwargs) -> Dict[str, Any]:
        """Create a rating document"""
        return {
            'user_id': user_id,
            'movie_id': movie_id,
            'rating': float(rating),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            **kwargs
        }
    
    @staticmethod
    def find_by_user_and_movie(db, user_id: int, movie_id: int) -> Optional[Dict]:
        """Find rating by user_id and movie_id"""
        return db.ratings.find_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
    
    @staticmethod
    def find_by_user(db, user_id: int) -> List[Dict]:
        """Find all ratings for a user"""
        return list(db.ratings.find({'user_id': user_id}))
    
    @staticmethod
    def find_by_movie(db, movie_id: int) -> List[Dict]:
        """Find all ratings for a movie"""
        return list(db.ratings.find({'movie_id': movie_id}))
    
    @staticmethod
    def create_or_update_rating(db, user_id: int, movie_id: int, rating: float) -> Dict:
        """Create or update a rating (upsert)"""
        rating_data = Rating.create(user_id, movie_id, rating)
        result = db.ratings.update_one(
            {'user_id': user_id, 'movie_id': movie_id},
            {'$set': rating_data},
            upsert=True
        )
        return db.ratings.find_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
    
    @staticmethod
    def delete_rating(db, user_id: int, movie_id: int) -> bool:
        """Delete a rating"""
        result = db.ratings.delete_one({
            'user_id': user_id,
            'movie_id': movie_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    def get_user_rating_count(db, user_id: int) -> int:
        """Get count of ratings for a user"""
        return db.ratings.count_documents({'user_id': user_id})
    
    @staticmethod
    def bulk_insert(db, ratings: List[Dict]) -> int:
        """Bulk insert ratings (handles duplicates gracefully)"""
        if not ratings:
            return 0
        try:
            result = db.ratings.insert_many(ratings, ordered=False)
            return len(result.inserted_ids)
        except Exception as e:
            # If bulk insert fails due to duplicates, insert individually
            inserted = 0
            for rating in ratings:
                try:
                    db.ratings.insert_one(rating)
                    inserted += 1
                except Exception:
                    # Skip duplicates silently
                    pass
            return inserted
    
    @staticmethod
    def get_user_ratings_with_movies(db, user_id: int) -> List[Dict]:
        """Get user ratings with movie details (aggregation)"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {
                '$lookup': {
                    'from': 'movies',
                    'localField': 'movie_id',
                    'foreignField': 'movie_id',
                    'as': 'movie'
                }
            },
            {'$unwind': {'path': '$movie', 'preserveNullAndEmptyArrays': True}},
            {
                '$project': {
                    'user_id': 1,
                    'movie_id': 1,
                    'rating': 1,
                    'created_at': 1,
                    'movie.title': 1,
                    'movie.poster_url': 1,
                    'movie.genres': 1
                }
            }
        ]
        return list(db.ratings.aggregate(pipeline))

