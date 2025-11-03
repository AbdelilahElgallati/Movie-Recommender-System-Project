import pandas as pd
import numpy as np

class PopularityModel:
    def __init__(self, movies_df, ratings_df, min_votes=50):
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        self.min_votes = min_votes
        self.popular_movies = None
        self._calculate_popularity()

    def _calculate_popularity(self):
        movie_stats = self.ratings_df.groupby('movie_id').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        movie_stats.columns = ['movie_id', 'avg_rating', 'vote_count']
        qualified = movie_stats[movie_stats['vote_count'] >= self.min_votes].copy()
        C = movie_stats['avg_rating'].mean()
        m = self.min_votes

        def weighted_rating(x, m=m, C=C):
            v = x['vote_count']
            R = x['avg_rating']
            return (v / (v + m) * R) + (m / (v + m) * C)

        qualified['weighted_score'] = qualified.apply(weighted_rating, axis=1)
        self.popular_movies = qualified.merge(
            self.movies_df[['movie_id', 'movie_title']],
            on='movie_id'
        ).sort_values('weighted_score', ascending=False)

    def recommend(self, n=10):
        recommendations = self.popular_movies.copy()
        top_n = recommendations.head(n)
        return [
            (row['movie_id'], row['movie_title'], row['weighted_score'])
            for _, row in top_n.iterrows()
        ]
