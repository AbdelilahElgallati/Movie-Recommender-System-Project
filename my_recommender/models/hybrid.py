import pandas as pd
import numpy as np

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
        # S'assurer que ratings_df n'est pas vide avant d'initialiser CF
        if not ratings_df.empty:
            self.cf_model = ImprovedCollaborativeFiltering(ratings_df)
        else:
            self.cf_model = None # Gérer le cas où il n'y a pas de notes initiales
            print("Warning: Ratings_df is empty, Collaborative model not initialized.")

        
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

    def get_user_rating_count(self, user_id, user_ratings_df=None):
        if user_ratings_df is not None:
            return len(user_ratings_df)
        
        if self.ratings_df.empty:
            return 0
        user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
        return len(user_ratings)

    def get_user_category(self, user_id, user_ratings_df=None):
        rating_count = self.get_user_rating_count(user_id, user_ratings_df)
        if rating_count == 0:
            return ('new', rating_count)
        elif rating_count <= 10:
            return ('sparse', rating_count)
        elif rating_count <= 30:
            return ('moderate', rating_count)
        else:
            return ('active', rating_count)

    def recommend(self, user_id, n=10, explain=False, user_ratings_df=None):
        # Utilise user_ratings_df s'il est fourni, sinon tombe sur self.ratings_df
        category, rating_count = self.get_user_category(user_id, user_ratings_df)
        
        recommendations = []
        explanation = {
            'user_id': user_id, 'category': category, 'rating_count': rating_count,
            'models_used': [], 'strategy': ''
        }
        
        # Sélectionne le bon DataFrame de notes
        user_ratings = user_ratings_df if user_ratings_df is not None else pd.DataFrame()
        if user_ratings_df is None and not self.ratings_df.empty:
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
            
            rated_movies = []
            for _, row in user_ratings.iterrows():
                movie_id = row['movie_id']
                title = self.id_to_title.get(movie_id)
                if title:  # Only add if we have a valid title
                    rated_movies.append((title, row['rating']))
            
            n_content = int(n * 0.7)
            n_pop = n - n_content
            if rated_movies:
                print(f"Passing {len(rated_movies)} rated movies to content model: {rated_movies}")
                cb_recs = self.cb_model.recommend_for_user(rated_movies, n_content)
                print(f"Content model returned {len(cb_recs)} recommendations")
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
            
            # --- CORRECTION POUR NOUVEL UTILISATEUR ---
            # Vérifie si l'utilisateur existe dans le modèle CF avant de l'appeler
            cf_recs = []
            if self.cf_model and user_id in self.cf_model.user_ids:
                cf_recs = self.cf_model.recommend(user_id, n_cf, k=20)
            else:
                # L'utilisateur est nouveau, réallouer le budget CF au Contenu et Pop
                explanation['strategy'] += " (CF fallback: user not in model)"
                n_cb += int(n_cf * 0.7) # 70% du budget CF va au CB
                n_pop += n_cf - int(n_cf * 0.7) # le reste à Pop
            # --- FIN CORRECTION ---

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
            
            # --- CORRECTION POUR NOUVEL UTILISATEUR ---
            cf_recs = []
            if self.cf_model and user_id in self.cf_model.user_ids:
                cf_recs = self.cf_model.recommend(user_id, n_cf, k=30)
            else:
                # L'utilisateur est nouveau, réallouer tout le budget CF au Contenu
                explanation['strategy'] += " (CF fallback: user not in model)"
                n_cb += n_cf
            # --- FIN CORRECTION ---
                
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