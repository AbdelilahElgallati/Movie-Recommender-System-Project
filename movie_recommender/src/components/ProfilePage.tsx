import React, { useState, useEffect } from 'react';
import { ErrorMessage } from './ErrorMessage';
import { LoadingSpinner } from './LoadingSpinner';
import { RecommendedMovieCard } from './RecommendedMovieCard';
import type { CurrentUser } from '../utils/types'; 
import { 
  User, 
  Sparkles, 
  Star, 
  Film 
} from 'lucide-react';

const API_URL = 'http://127.0.0.1:5001';

interface ProfilePageProps {
  navigateTo: (pageName: string, movie?: any) => void;
  currentUser: CurrentUser;
}

export const ProfilePage = ({ navigateTo, currentUser }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!currentUser.id) {
      setRecommendations([]);
      setExplanation(null);
      setError(null); 
      return;
    }

    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);
      setRecommendations([]);
      setExplanation(null);
      
      try {
        const res = await fetch(`${API_URL}/api/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: parseInt(currentUser.id, 10) })
        });
        if (!res.ok) throw new Error(`User ID ${currentUser.id} not found or API error.`);
        const data = await res.json();
        setRecommendations(data.recommendations);
        setExplanation(data.explanation);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [currentUser.id]);

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-10">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          My Recommendations
        </h1>
        <p className="text-gray-400 text-lg">
          Personalized movie recommendations just for you
        </p>
      </div>
      
      {!currentUser.id && !loading && (
        <div className="bg-gradient-to-r from-indigo-900/30 to-purple-900/30 border border-indigo-500/30 rounded-xl p-8 text-center">
          <User className="w-16 h-16 text-indigo-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Login Required</h3>
          <p className="text-gray-400">Please login to see your personalized recommendations.</p>
        </div>
      )}

      {error && <ErrorMessage message={error} />}
      
      {explanation && (
        <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 p-6 rounded-xl mb-10 border border-indigo-500/30 shadow-xl">
          <div className="flex items-start gap-4">
            <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-3 rounded-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-indigo-300 mb-3">Recommendation Strategy</h3>
              <div className="space-y-2 text-sm text-gray-300">
                <p>
                  <span className="font-medium text-white">User:</span> {currentUser.username} 
                  <span className="ml-2 text-gray-400">(ID: {explanation.user_id})</span>
                  <span className="ml-2 px-2 py-1 bg-indigo-600/30 rounded text-xs">{explanation.category}</span>
                </p>
                <p>
                  <span className="font-medium text-white">Strategy:</span> {explanation.strategy}
                </p>
              </div>
              <div className="flex flex-wrap gap-2 mt-4">
                {explanation.models_used.map(([model, weight]) => (
                  <span key={model} className="px-3 py-1.5 bg-gray-800/70 text-xs rounded-lg font-medium border border-gray-700">
                    {model}: <span className="text-indigo-400">{Math.round(weight * 100)}%</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {loading && <LoadingSpinner />}

      {!loading && recommendations.length > 0 && currentUser.id && (
        <div>
          {/* ... (h2 title) ... */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {recommendations.map(movie => (
              <RecommendedMovieCard 
                key={movie.movie_id} 
                movie={movie} 
                onClick={() => navigateTo('movie', movie)} 
              />
            ))}
          </div>
        </div>
      )}

      {!loading && recommendations.length === 0 && currentUser.id && !error && (
        <div className="text-center py-16 bg-gray-800/30 rounded-xl border border-gray-700">
          <Film className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Recommendations Yet</h3>
          <p className="text-gray-400 mb-6">
            We don't have enough data to recommend movies yet. Try rating more movies on the home page!
          </p>
          <button
            onClick={() => navigateTo('home')}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-indigo-500 hover:to-purple-500 transition-all"
          >
            Browse Movies
          </button>
        </div>
      )}
    </div>
  );
};