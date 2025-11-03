import pandas as pd
import numpy as np

# Imports corrigés (relatifs)
from .content import ImprovedContentBased
from .collaborative import ImprovedCollaborativeFiltering
from .popularity import PopularityModel

class HybridRecommender:
    def __init__(self, movies_df, ratings_df, credits_df=None):
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        
        print("Initializing Popularity Model...")
        self.popularity_model = PopularityModel(movies_df, ratings_df)
        
        print("Initializing Collaborative Filtering Model...")
        self.cf_model = ImprovedCollaborativeFiltering(ratings_df)
        
        print("Initializing Content-Based Model...")
        cb_movies_df = movies_df.copy()
        genre_cols = [col for col in movies_df.columns if col in [
            'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 
            'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 
            'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
        ]]
        cb_movies_df = cb_movies_df[['movie_id', 'movie_title'] + genre_cols]
        self.cb_model = ImprovedContentBased(cb_movies_df, credits_df)
        
        self.id_to_title = dict(zip(
            movies_df['movie_id'],
            movies_df['movie_title']
        ))
        self.title_to_id = {v: k for k, v in self.id_to_title.items()}
        print("Hybrid Recommender initialized successfully!")

    def get_user_rating_count(self, user_id):
        if self.ratings_df.empty:
            return 0
        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
        return len(user_ratings)

    def get_user_category(self, user_id):
        rating_count = self.get_user_rating_count(user_id)
        if rating_count == 0:
            return ('new', rating_count)
        elif rating_count <= 10:
            return ('sparse', rating_count)
        elif rating_count <= 30:
            return ('moderate', rating_count)
        else:
            return ('active', rating_count)

    def recommend(self, user_id, n=10, explain=False):
        category, rating_count = self.get_user_category(user_id)
        recommendations = []
        explanation = {
            'user_id': user_id, 'category': category, 'rating_count': rating_count,
            'models_used': [], 'strategy': ''
        }
        
        user_ratings = pd.DataFrame()
        if not self.ratings_df.empty:
            user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]

        if category == 'new':
            explanation['strategy'] = "New user - using popularity-based"
            explanation['models_used'].append(('popularity', 1.0))
            pop_recs = self.popularity_model.recommend(n)
            for movie_id, title, score in pop_recs:
                recommendations.append((movie_id, title, score, 'popularity'))

        elif category == 'sparse':
            explanation['strategy'] = "Sparse user - Content (70%) + Popularity (30%)"
            explanation['models_used'].extend([('content_based', 0.7), ('popularity', 0.3)])
            
            rated_movies = [
                (self.id_to_title.get(row['movie_id'], ''), row['rating'])
                for _, row in user_ratings.iterrows() if row['movie_id'] in self.id_to_title
            ]
            n_content = int(n * 0.7)
            n_pop = n - n_content
            if rated_movies:
                cb_recs = self.cb_model.recommend_for_user(rated_movies, n_content)
                for movie_id, title, score in cb_recs:
                    recommendations.append((movie_id, title, score, 'content_based'))
            pop_recs = self.popularity_model.recommend(n_pop)
            for movie_id, title, score in pop_recs:
                recommendations.append((movie_id, title, score, 'popularity'))

        elif category == 'moderate':
            explanation['strategy'] = "Moderate user - CF (60%) + Content (30%) + Pop (10%)"
            explanation['models_used'].extend([('collaborative', 0.6), ('content_based', 0.3), ('popularity', 0.1)])
            n_cf = int(n * 0.6)
            n_cb = int(n * 0.3)
            n_pop = n - n_cf - n_cb
            
            cf_recs = self.cf_model.recommend(user_id, n_cf, k=20)
            for movie_id, score in cf_recs:
                title = self.id_to_title.get(movie_id, f"Movie {movie_id}")
                recommendations.append((movie_id, title, score, 'collaborative'))
                
            rated_movies = [
                (self.id_to_title.get(row['movie_id'], ''), row['rating'])
                for _, row in user_ratings.iterrows() if row['movie_id'] in self.id_to_title
            ]
            if rated_movies:
                cb_recs = self.cb_model.recommend_for_user(rated_movies, n_cb)
                for movie_id, title, score in cb_recs:
                    recommendations.append((movie_id, title, score, 'content_based'))
                    
            pop_recs = self.popularity_model.recommend(n_pop)
            for movie_id, title, score in pop_recs:
                recommendations.append((movie_id, title, score, 'popularity'))

        else:  # active
            explanation['strategy'] = "Active user - CF (80%) + Content (20%)"
            explanation['models_used'].extend([('collaborative', 0.8), ('content_based', 0.2)])
            n_cf = int(n * 0.8)
            n_cb = n - n_cf
            
            cf_recs = self.cf_model.recommend(user_id, n_cf, k=30)
            for movie_id, score in cf_recs:
                title = self.id_to_title.get(movie_id, f"Movie {movie_id}")
                recommendations.append((movie_id, title, score, 'collaborative'))
                
            rated_movies = [
                (self.id_to_title.get(row['movie_id'], ''), row['rating'])
                for _, row in user_ratings.iterrows() if row['movie_id'] in self.id_to_title
            ]
            if rated_movies:
                cb_recs = self.cb_model.recommend_for_user(rated_movies, n_cb)
                for movie_id, title, score in cb_recs:
                    recommendations.append((movie_id, title, score, 'content_based'))

        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec[0] not in seen:
                seen.add(rec[0])
                unique_recs.append(rec)
        
        final_recs = unique_recs[:n]
        
        if explain:
            return final_recs, explanation
        return final_recs