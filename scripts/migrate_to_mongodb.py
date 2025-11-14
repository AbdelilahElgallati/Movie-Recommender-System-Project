"""
Migration script to move data from JSON files and CSV to MongoDB
Run this script once to migrate existing data to MongoDB
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from my_recommender.database.connection import get_db, init_db
from my_recommender.database.models import User, Movie, Rating
from flask import Flask

def migrate_users():
    """Migrate users from JSON file to MongoDB"""
    print("\n" + "="*60)
    print("MIGRATING USERS")
    print("="*60)
    
    db = get_db()
    
    # Load from JSON
    if os.path.exists(Config.USERS_FILE_PATH):
        with open(Config.USERS_FILE_PATH, 'r') as f:
            users_data = json.load(f)
        
        migrated = 0
        skipped = 0
        
        for user in users_data:
            user_id = user.get('id', user.get('user_id'))
            username = user.get('username')
            
            if not user_id or not username:
                skipped += 1
                continue
            
            # Check if user already exists
            existing = User.find_by_id(db, user_id)
            if existing:
                print(f"  User {user_id} ({username}) already exists, skipping...")
                skipped += 1
                continue
            
            # Create user document
            user_doc = User.create(
                user_id=user_id,
                username=username,
                password=user.get('password', ''),
                created_at=datetime.utcnow()
            )
            
            User.create_user(db, user_doc)
            migrated += 1
            print(f"  ✓ Migrated user {user_id}: {username}")
        
        print(f"\nUsers migration complete: {migrated} migrated, {skipped} skipped")
    else:
        print(f"  No users.json file found at {Config.USERS_FILE_PATH}")
    
    return True

def migrate_ratings():
    """Migrate ratings from JSON file to MongoDB"""
    print("\n" + "="*60)
    print("MIGRATING RATINGS")
    print("="*60)
    
    db = get_db()
    
    # Load from JSON
    ratings_path = os.path.join(Config.BASE_DIR, 'user_ratings.json')
    if os.path.exists(ratings_path):
        with open(ratings_path, 'r') as f:
            ratings_data = json.load(f)
        
        migrated = 0
        skipped = 0
        
        for user_id_str, movies in ratings_data.items():
            user_id = int(user_id_str)
            for movie_id_str, rating in movies.items():
                movie_id = int(movie_id_str)
                rating_value = float(rating)
                
                # Check if rating already exists
                existing = Rating.find_by_user_and_movie(db, user_id, movie_id)
                if existing:
                    skipped += 1
                    continue
                
                # Create rating
                Rating.create_or_update_rating(db, user_id, movie_id, rating_value)
                migrated += 1
        
        print(f"\nRatings migration complete: {migrated} migrated, {skipped} skipped")
    else:
        print(f"  No user_ratings.json file found at {ratings_path}")
    
    # Also migrate from MovieLens dataset if available
    if os.path.exists(Config.RATINGS_PATH):
        print("\nMigrating MovieLens ratings dataset...")
        try:
            ratings_df = pd.read_csv(
                Config.RATINGS_PATH,
                sep='\t',
                names=['user_id', 'movie_id', 'rating', 'unix_timestamp'],
                encoding='latin-1'
            )
            
            # Get all existing ratings as a set for fast lookup
            print("  Loading existing ratings for duplicate check...")
            existing_ratings = set()
            for rating in db.ratings.find({}, {'user_id': 1, 'movie_id': 1}):
                existing_ratings.add((rating['user_id'], rating['movie_id']))
            print(f"  Found {len(existing_ratings)} existing ratings")
            
            migrated = 0
            skipped = 0
            batch_size = 1000
            
            for i in range(0, len(ratings_df), batch_size):
                batch = ratings_df.iloc[i:i+batch_size]
                ratings_list = []
                
                for _, row in batch.iterrows():
                    user_id = int(row['user_id'])
                    movie_id = int(row['movie_id'])
                    rating = float(row['rating'])
                    
                    # Check if already exists using set (much faster)
                    if (user_id, movie_id) in existing_ratings:
                        skipped += 1
                        continue
                    
                    # Add to set to avoid duplicates in same batch
                    existing_ratings.add((user_id, movie_id))
                    ratings_list.append(Rating.create(user_id, movie_id, rating))
                
                if ratings_list:
                    try:
                        # Use ordered=False to continue on errors
                        result = db.ratings.insert_many(ratings_list, ordered=False)
                        migrated += len(result.inserted_ids)
                    except Exception as bulk_error:
                        # If bulk insert fails, insert one by one
                        print(f"  Warning: Batch insert failed, inserting individually...")
                        for rating_doc in ratings_list:
                            try:
                                db.ratings.insert_one(rating_doc)
                                migrated += 1
                            except Exception as e:
                                if 'duplicate' not in str(e).lower():
                                    print(f"  Error inserting rating: {e}")
                                skipped += 1
                
                if (i + batch_size) % 10000 == 0:
                    print(f"  Processed {min(i + batch_size, len(ratings_df))} / {len(ratings_df)} ratings... (migrated: {migrated}, skipped: {skipped})")
            
            print(f"\nMovieLens ratings migration complete: {migrated} migrated, {skipped} skipped")
        except Exception as e:
            print(f"  Error migrating MovieLens ratings: {e}")
            import traceback
            traceback.print_exc()
    
    return True

def migrate_movies():
    """Migrate movies from CSV to MongoDB"""
    print("\n" + "="*60)
    print("MIGRATING MOVIES")
    print("="*60)
    
    db = get_db()
    
    # Migrate from enriched movies CSV
    if os.path.exists(Config.ENRICHED_MOVIES_PATH):
        print("Migrating from enriched movies CSV...")
        try:
            movies_df = pd.read_csv(Config.ENRICHED_MOVIES_PATH)
            
            migrated = 0
            skipped = 0
            batch_size = 100
            
            for i in range(0, len(movies_df), batch_size):
                batch = movies_df.iloc[i:i+batch_size]
                movies_list = []
                
                for _, row in batch.iterrows():
                    movie_id = int(row['movie_id'])
                    
                    # Check if movie already exists
                    existing = Movie.find_by_id(db, movie_id)
                    if existing:
                        skipped += 1
                        continue
                    
                    # Prepare movie document
                    movie_doc = Movie.create(
                        movie_id=movie_id,
                        title=row.get('movie_title', ''),
                        release_date=row.get('release date', ''),
                        imdb_url=row.get('IMDb URL', ''),
                        poster_url=row.get('poster_url', ''),
                        overview=row.get('overview', ''),
                        genres_list=row.get('genres_list', [])
                    )
                    
                    # Add genre columns
                    genre_cols = [col for col in Config.GENRE_COLS if col in row]
                    for genre in genre_cols:
                        movie_doc[genre] = int(row[genre]) if pd.notna(row[genre]) else 0
                    
                    movies_list.append(movie_doc)
                
                if movies_list:
                    Movie.bulk_insert(db, movies_list)
                    migrated += len(movies_list)
                
                if (i + batch_size) % 500 == 0:
                    print(f"  Processed {min(i + batch_size, len(movies_df))} / {len(movies_df)} movies...")
            
            print(f"\nMovies migration complete: {migrated} migrated, {skipped} skipped")
        except Exception as e:
            print(f"  Error migrating movies: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"  No enriched movies CSV found at {Config.ENRICHED_MOVIES_PATH}")
    
    return True

def main():
    """Main migration function"""
    print("="*60)
    print("MONGODB MIGRATION SCRIPT")
    print("="*60)
    print("\nThis script will migrate data from JSON files and CSV to MongoDB.")
    print("Existing data in MongoDB will be preserved (no duplicates).\n")
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        return
    
    # Initialize Flask app for database connection
    app = Flask(__name__)
    app.config.from_object(Config)
    
    try:
        # Initialize database
        init_db(app)
        
        # Run migrations
        migrate_users()
        migrate_ratings()
        migrate_movies()
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETE!")
        print("="*60)
        print("\nYou can now use MongoDB for all data operations.")
        print("The old JSON files are preserved but no longer used.")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

