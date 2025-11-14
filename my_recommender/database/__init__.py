"""
Database package for MongoDB connection and models
"""
from .connection import get_db, init_db
from .models import User, Movie, Rating

__all__ = ['get_db', 'init_db', 'User', 'Movie', 'Rating']

