"""
MongoDB connection management
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, InvalidURI
from urllib.parse import quote_plus
from flask import current_app
from config import Config

# Global MongoDB client
_client = None
_db = None

def get_client():
    """Get or create MongoDB client"""
    global _client
    if _client is None:
        try:
            # Validate and sanitize MongoDB URI
            mongodb_uri = Config.MONGODB_URI.strip()
            
            # Basic validation
            if not mongodb_uri.startswith('mongodb://') and not mongodb_uri.startswith('mongodb+srv://'):
                raise InvalidURI(f"Invalid MongoDB URI format. Must start with 'mongodb://' or 'mongodb+srv://'")
            
            # If URI contains credentials, ensure they are properly encoded
            if '@' in mongodb_uri and '://' in mongodb_uri:
                # Extract parts of the URI
                protocol, rest = mongodb_uri.split('://', 1)
                if '@' in rest:
                    # Has credentials - ensure they are encoded
                    credentials, host_part = rest.split('@', 1)
                    if ':' in credentials:
                        username, password = credentials.split(':', 1)
                        # Only encode if not already encoded (check for %)
                        if '%' not in username:
                            username_encoded = quote_plus(username)
                        else:
                            username_encoded = username
                        if '%' not in password:
                            password_encoded = quote_plus(password)
                        else:
                            password_encoded = password
                        mongodb_uri = f'{protocol}://{username_encoded}:{password_encoded}@{host_part}'
            
            # Create client
            _client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            # Test connection
            _client.admin.command('ping')
            # Don't print full URI if it contains credentials
            display_uri = mongodb_uri
            if '@' in display_uri:
                # Hide password in display
                parts = display_uri.split('@')
                if len(parts) == 2:
                    display_uri = f"{parts[0].split(':')[0]}:****@{parts[1]}"
            print(f"✓ Connected to MongoDB at {display_uri}")
        except InvalidURI as e:
            print(f"✗ Invalid MongoDB URI: {e}")
            print(f"  Current URI: {Config.MONGODB_URI}")
            print(f"  URI format should be: mongodb://[username:password@]host:port/")
            print(f"  For local MongoDB without auth: mongodb://localhost:27017/")
            raise
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            print(f"  Make sure MongoDB is running on {Config.MONGODB_HOST}:{Config.MONGODB_PORT}")
            raise
        except Exception as e:
            print(f"✗ Unexpected error connecting to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            raise
    return _client

def get_db():
    """Get database instance"""
    global _db
    if _db is None:
        client = get_client()
        _db = client[Config.MONGODB_DB]
    return _db

def init_db(app):
    """Initialize database connection for Flask app"""
    global _db
    try:
        _db = get_db()
        app.mongodb = _db
        print(f"✓ Database '{Config.MONGODB_DB}' initialized")
        
        # Create indexes for better performance
        create_indexes()
        return _db
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        raise

def create_indexes():
    """Create database indexes for better query performance"""
    db = get_db()
    
    try:
        # Users collection indexes
        db.users.create_index("username", unique=True)
        db.users.create_index("user_id", unique=True)
        
        # Movies collection indexes
        db.movies.create_index("movie_id", unique=True)
        db.movies.create_index("title")
        db.movies.create_index([("title", "text")])  # Text search index
        
        # Ratings collection indexes
        db.ratings.create_index([("user_id", 1), ("movie_id", 1)], unique=True)
        db.ratings.create_index("user_id")
        db.ratings.create_index("movie_id")
        db.ratings.create_index("rating")
        
        print("✓ Database indexes created successfully")
    except Exception as e:
        print(f"Warning: Could not create all indexes: {e}")

def close_connection():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("✓ MongoDB connection closed")

