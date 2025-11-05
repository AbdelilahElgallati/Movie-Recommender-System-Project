import pandas as pd
import numpy as np
import pickle

from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ImprovedContentBased:
    def __init__(self, movies_df, credits_df=None, use_stemming=False):
        self.use_stemming = use_stemming
        self.ps = PorterStemmer() if use_stemming else None
        if credits_df is not None:
            self.movies_df = self._merge_and_process(movies_df, credits_df)
        else:
            self.movies_df = self._process_movies(movies_df)
        self.vectorizer = TfidfVectorizer(
            max_features=5000, stop_words='english', ngram_range=(1, 2), min_df=2
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.movies_df['tags'])
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        self.title_to_idx = {
            title: idx for idx, title in enumerate(self.movies_df['title'])
        }
        self.idx_to_title = {
            idx: title for title, idx in self.title_to_idx.items()
        }

    def _process_movies(self, movies_df):
        processed = movies_df.copy()
        genre_cols = [col for col in movies_df.columns if col in [
            'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 
            'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 
            'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
        ]]
        
        def get_genres(row):
            genres = []
            for col in genre_cols:
                if row[col] == 1:
                    genres.append(col.replace("'", "").replace(" ", ""))
            return genres
        
        processed['genres'] = movies_df.apply(get_genres, axis=1)
        processed['tags'] = processed['genres'].apply(lambda x: ' '.join(x))
        processed['title'] = processed['movie_title']
        return processed[['movie_id', 'title', 'tags']]

    def _stem_text(self, text):
        if not self.use_stemming:
            return text
        words = text.split()
        stemmed = [self.ps.stem(word) for word in words]
        return " ".join(stemmed)

    def recommend(self, movie_title, n=10):
        if movie_title not in self.title_to_idx:
            matches = [t for t in self.title_to_idx if movie_title.lower() in t.lower()]
            if not matches:
                print(f"Warning: Title '{movie_title}' not found.")
                return []
            movie_title = matches[0] 
            
        idx = self.title_to_idx[movie_title]
        similarity_scores = self.similarity_matrix[idx]
        similar_indices = similarity_scores.argsort()[::-1][1:n + 1]
        recommendations = []
        for sim_idx in similar_indices:
            movie_id = self.movies_df.iloc[sim_idx]['movie_id']
            title = self.idx_to_title[sim_idx]
            score = similarity_scores[sim_idx]
            recommendations.append((movie_id, title, score))
        return recommendations

    def recommend_for_user(self, user_rated_movies, n=10):
        weighted_similarity = np.zeros(len(self.movies_df))
        total_weight = 0
        valid_movies_rated = 0
        
        for movie_title, rating in user_rated_movies:
            idx = self.title_to_idx.get(movie_title)
            if idx is None:
                matches = [t for t in self.title_to_idx if movie_title.lower() in t.lower()]
                if matches:
                    idx = self.title_to_idx[matches[0]]
                else:
                    print(f"Warning: Title '{movie_title}' not found in content model.")
                    continue

            valid_movies_rated += 1
            weight = rating - 3.0  # Mean-center the rating
            weighted_similarity += self.similarity_matrix[idx] * weight
            total_weight += abs(weight)

        if total_weight < 1e-6 or valid_movies_rated == 0:
            print("Warning: No valid movies provided for feature recommendation.")
            return []

        weighted_similarity /= total_weight
        rated_titles = [title for title, _ in user_rated_movies]
        rated_indices = [self.title_to_idx[t] for t in rated_titles if t in self.title_to_idx]
        
        weighted_similarity[rated_indices] = -1
        top_indices = weighted_similarity.argsort()[::-1][:n]
        
        recommendations = []
        for idx in top_indices:
            if weighted_similarity[idx] < 0:
                continue
            try:
                movie_id = self.movies_df.iloc[idx]['movie_id']
                title = self.idx_to_title[idx]  # C'est ici que l'erreur se produit
                score = weighted_similarity[idx]
                recommendations.append((movie_id, title, score))
            except KeyError as e:
                print(f"Warning: Index {idx} not found in idx_to_title mapping. Skipping.")
                continue
            except IndexError as e:
                print(f"Warning: Index {idx} out of bounds for movies_df. Skipping.")
                continue
        
        return recommendations

    def save_model(self, filepath='content_model.pkl'):
        model_data = {
            'movies_df': self.movies_df,
            'similarity_matrix': self.similarity_matrix,
            'title_to_idx': self.title_to_idx,
            'idx_to_title': self.idx_to_title,
            'vectorizer': self.vectorizer, 
            'tfidf_matrix': self.tfidf_matrix
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    @classmethod
    def load_model(cls, filepath='content_model.pkl'):
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        instance = cls.__new__(cls)
        instance.movies_df = model_data['movies_df']
        instance.similarity_matrix = model_data['similarity_matrix']
        instance.title_to_idx = model_data['title_to_idx']
        instance.idx_to_title = model_data['idx_to_title']
        instance.vectorizer = model_data.get('vectorizer')
        instance.tfidf_matrix = model_data.get('tfidf_matrix')
        instance.use_stemming = False 
        instance.ps = None
        
        print("ImprovedContentBased model loaded successfully.")
        return instance