import React, { useState } from 'react';
import { ErrorMessage } from './ErrorMessage';
import { LoadingSpinner } from './LoadingSpinner';
import { MovieGrid } from './MovieGrid';
import { TrendingUp, Film } from 'lucide-react';

const API_URL = 'http://127.0.0.1:5001';

// Liste des genres (copiée de GenreFilter.tsx)
const GENRES = [
  'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 
  'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 
  'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
];

export const DiscoverPage = ({ navigateTo }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState('');

  const getRecommendationsByGenre = async (genre) => {
    if (selectedGenre === genre && recommendations.length > 0) return;

    setSelectedGenre(genre);
    setLoading(true);
    setError(null);
    setRecommendations([]);

    try {
      const res = await fetch(`${API_URL}/api/recommend/genre/${encodeURIComponent(genre)}`);
      if (!res.ok) {
        throw new Error(`Unable to load recommendations for ${genre}.`);
      }
      const data = await res.json();
      
      // Normalize movie data: ensure each movie has an 'id' field
      const normalizedData = data.map(movie => ({
        ...movie,
        id: movie.id || movie.movie_id // Use id if exists, otherwise use movie_id
      }));
      
      setRecommendations(normalizedData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-10">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          Discover by Genre
        </h1>
        <p className="text-gray-400 text-lg">
          Click on a genre to see the most popular movies
        </p>
      </div>

      <div className="flex flex-wrap gap-3 mb-10">
        {GENRES.map(genre => {
          const isActive = selectedGenre === genre;
          return (
            <button
              key={genre}
              onClick={() => getRecommendationsByGenre(genre)}
              className={`px-6 py-3 rounded-full font-medium transition-all duration-200 shadow-lg ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-indigo-500/50 scale-105'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:scale-105'
              }`}
            >
              {genre}
            </button>
          );
        })}
      </div>

      <div>
        {loading && <LoadingSpinner />}
        {error && <ErrorMessage message={error} />}
        
        {!loading && !error && recommendations.length > 0 && (
          <div>
            <div className="flex items-center gap-3 mb-6">
              <TrendingUp className="w-8 h-8 text-indigo-500" />
              <h2 className="text-3xl font-bold">Top 10 - {selectedGenre}</h2>
            </div>
            <MovieGrid 
              movies={recommendations}
              onMovieClick={(movie) => navigateTo('movie', movie)}
              userRatings={{}}
              onRatingChange={() => {}}
            />
          </div>
        )}

        {!loading && !error && recommendations.length === 0 && selectedGenre && (
          <div className="text-center py-16">
            <Film className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No movies found for this genre.</p>
          </div>
        )}
      </div>
    </div>
  );
};