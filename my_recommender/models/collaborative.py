"""
Improved User-Based Collaborative Filtering
With better handling of sparse data and edge cases
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix


class ImprovedCollaborativeFiltering:
    """
    User-based collaborative filtering with improvements:
    - Handles sparse matrices efficiently
    - Better similarity calculation
    - Configurable neighborhood size
    - Confidence weighting based on common ratings
    """
    
    def __init__(self, ratings_df, min_common_items=2, similarity_threshold=0.0):
        """
        Initialize the collaborative filtering model
        
        Args:
            ratings_df: DataFrame with user_id, movie_id, rating columns
            min_common_items: Minimum number of common items for similarity
            similarity_threshold: Minimum similarity score to consider
        """
        self.ratings_df = ratings_df
        self.min_common_items = min_common_items
        self.similarity_threshold = similarity_threshold
        
        # Create utility matrix
        self.utility_matrix = ratings_df.pivot_table(
            index='user_id', 
            columns='movie_id', 
            values='rating'
        ).fillna(0)
        
        self.user_ids = self.utility_matrix.index.tolist()
        self.movie_ids = self.utility_matrix.columns.tolist()
        self.matrix_values = self.utility_matrix.values
        
        # Pre-compute user means for normalization
        self.user_means = {}
        for user_id in self.user_ids:
            user_ratings = self.matrix_values[self.user_ids.index(user_id)]
            rated_items = user_ratings[user_ratings > 0]
            self.user_means[user_id] = np.mean(rated_items) if len(rated_items) > 0 else 3.0
    
    def calculate_similarity(self, user_vec1, user_vec2):
        """
        Calculate Pearson correlation with minimum common items check
        
        Args:
            user_vec1: First user's rating vector
            user_vec2: Second user's rating vector
            
        Returns:
            Similarity score between -1 and 1
        """
        # Find common rated items
        common_mask = (user_vec1 > 0) & (user_vec2 > 0)
        
        if common_mask.sum() < self.min_common_items:
            return 0.0
        
        user1_common = user_vec1[common_mask]
        user2_common = user_vec2[common_mask]
        
        # Calculate means
        mean1 = np.mean(user1_common)
        mean2 = np.mean(user2_common)
        
        # Pearson correlation
        numerator = np.sum((user1_common - mean1) * (user2_common - mean2))
        denominator = np.sqrt(
            np.sum((user1_common - mean1) ** 2) * 
            np.sum((user2_common - mean2) ** 2)
        )
        
        if denominator == 0:
            return 0.0
        
        similarity = numerator / denominator
        
        # Apply threshold
        return similarity if abs(similarity) >= self.similarity_threshold else 0.0
    
    def find_k_neighbors(self, user_id, k=10):
        """
        Find K most similar users
        
        Args:
            user_id: Target user ID
            k: Number of neighbors
            
        Returns:
            List of (neighbor_id, similarity) tuples
        """
        if user_id not in self.user_ids:
            return []
        
        user_idx = self.user_ids.index(user_id)
        user_vec = self.matrix_values[user_idx]
        
        similarities = []
        for idx, neighbor_id in enumerate(self.user_ids):
            if neighbor_id == user_id:
                continue
            
            neighbor_vec = self.matrix_values[idx]
            sim = self.calculate_similarity(user_vec, neighbor_vec)
            
            if sim > 0:
                similarities.append((neighbor_id, sim))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def predict_rating(self, user_id, movie_id, k=10):
        """
        Predict rating for a user-movie pair
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            k: Number of neighbors to use
            
        Returns:
            Predicted rating (1-5 scale)
        """
        if user_id not in self.user_ids or movie_id not in self.movie_ids:
            return self.user_means.get(user_id, 3.0)
        
        user_idx = self.user_ids.index(user_id)
        movie_idx = self.movie_ids.index(movie_id)
        
        # If user already rated this movie, return the rating
        if self.matrix_values[user_idx, movie_idx] > 0:
            return self.matrix_values[user_idx, movie_idx]
        
        # Find neighbors
        neighbors = self.find_k_neighbors(user_id, k)
        
        if not neighbors:
            return self.user_means[user_id]
        
        # Calculate weighted average
        weighted_sum = 0.0
        similarity_sum = 0.0
        user_mean = self.user_means[user_id]
        
        for neighbor_id, similarity in neighbors:
            neighbor_idx = self.user_ids.index(neighbor_id)
            neighbor_rating = self.matrix_values[neighbor_idx, movie_idx]
            
            if neighbor_rating > 0:
                neighbor_mean = self.user_means[neighbor_id]
                weighted_sum += similarity * (neighbor_rating - neighbor_mean)
                similarity_sum += abs(similarity)
        
        if similarity_sum > 0:
            prediction = user_mean + (weighted_sum / similarity_sum)
        else:
            prediction = user_mean
        
        # Clip to valid range
        return np.clip(prediction, 1, 5)
    
    def recommend(self, user_id, n=10, k=10, exclude_rated=True):
        """
        Generate top N recommendations for a user
        
        Args:
            user_id: User ID
            n: Number of recommendations
            k: Number of neighbors to use
            exclude_rated: Whether to exclude already rated movies
            
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        if user_id not in self.user_ids:
            return []
        
        user_idx = self.user_ids.index(user_id)
        user_ratings = self.matrix_values[user_idx]
        
        predictions = []
        for movie_idx, movie_id in enumerate(self.movie_ids):
            # Skip if already rated and exclude_rated is True
            if exclude_rated and user_ratings[movie_idx] > 0:
                continue
            
            pred_rating = self.predict_rating(user_id, movie_id, k)
            predictions.append((movie_id, pred_rating))
        
        # Sort by predicted rating
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]
    
    def get_user_profile_strength(self, user_id):
        """
        Calculate how well-defined a user's profile is
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (num_ratings, avg_rating, profile_strength_score)
        """
        if user_id not in self.user_ids:
            return (0, 0.0, 0.0)
        
        user_idx = self.user_ids.index(user_id)
        user_ratings = self.matrix_values[user_idx]
        rated_items = user_ratings[user_ratings > 0]
        
        num_ratings = len(rated_items)
        avg_rating = np.mean(rated_items) if num_ratings > 0 else 0.0
        
        # Profile strength: combination of quantity and variance
        # More ratings + diverse ratings = stronger profile
        if num_ratings == 0:
            strength = 0.0
        else:
            quantity_score = min(num_ratings / 50, 1.0)  # Normalize to 50 ratings
            variance = np.var(rated_items) if num_ratings > 1 else 0.0
            diversity_score = min(variance / 2.0, 1.0)  # Normalize variance
            strength = (quantity_score * 0.7) + (diversity_score * 0.3)
        
        return (num_ratings, avg_rating, strength)


# # Example usage
# if __name__ == "__main__":
#     # Load data
#     r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']
#     ratings = pd.read_csv('Dataset/u.data', sep='\t', names=r_cols, encoding='latin-1')
    
#     # Create model
#     cf_model = ImprovedCollaborativeFiltering(
#         ratings, 
#         min_common_items=3,
#         similarity_threshold=0.1
#     )
    
#     # Test user
#     test_user = 196
    
#     # Check profile strength
#     num_ratings, avg_rating, strength = cf_model.get_user_profile_strength(test_user)
#     print(f"User {test_user} Profile:")
#     print(f"  Number of ratings: {num_ratings}")
#     print(f"  Average rating: {avg_rating:.2f}")
#     print(f"  Profile strength: {strength:.2f}")
    
#     # Get recommendations
#     print(f"\nTop 10 Recommendations for User {test_user}:")
#     recommendations = cf_model.recommend(test_user, n=10, k=20)
#     for movie_id, pred_rating in recommendations:
#         print(f"  Movie {movie_id}: {pred_rating:.2f}")