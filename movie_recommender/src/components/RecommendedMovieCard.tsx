import React from 'react';
import {  
  Star,
} from 'lucide-react';

// URL de l'image de remplacement
const PLACEHOLDER_IMG = 'https://placehold.co/500x750/334155/e2e8f0?text=Image+N/A';

interface RecommendedMovieCardProps {
  movie: any;
  onClick: () => void;
}

export const RecommendedMovieCard = ({ movie, onClick }: RecommendedMovieCardProps) => {
  const modelColor = {
    'popularity': 'from-blue-600 to-blue-700',
    'content_based': 'from-green-600 to-green-700',
    'collaborative': 'from-purple-600 to-purple-700',
  }[movie.model_used] || 'from-gray-600 to-gray-700';

  const getImageUrl = () => {
    if (movie.poster_url && !movie.poster_url.includes('placeholder')) {
      return movie.poster_url;
    }
    return `${PLACEHOLDER_IMG}${encodeURIComponent(movie.title?.substring(0, 20) || 'No+Image')}`;
  };

  const imageUrl = getImageUrl();

  return (
    <div className="group bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl shadow-lg overflow-hidden hover:shadow-2xl hover:shadow-indigo-500/30 transition-all duration-300 transform hover:-translate-y-2">
      <button onClick={onClick} className="block w-full relative overflow-hidden">
        <div className="absolute top-3 right-3 z-20">
          <div className={`bg-gradient-to-r ${modelColor} px-3 py-1.5 rounded-full text-xs font-bold text-white shadow-lg`}>
            {movie.model_used?.replace('_', ' ') || 'unknown'}
          </div>
        </div>
        <img
          src={imageUrl}
          alt={movie.title}
          className="w-full h-auto object-cover aspect-[2/3] group-hover:scale-110 transition-transform duration-500"
          onError={(e) => { e.currentTarget.src = PLACEHOLDER_IMG + 'No+Image'; }}
        />
      </button>
      <div className="p-4 bg-gradient-to-br from-gray-800/50 to-gray-900/50">
        <button onClick={onClick} className="hover:underline w-full text-left">
          <h3 className="text-md font-semibold text-white line-clamp-2 group-hover:text-indigo-400 transition-colors" title={movie.title}>
            {movie.title}
          </h3>
        </button>
        <div className="flex justify-between items-center mt-3">
          <span className="text-sm font-bold text-yellow-400 flex items-center gap-1.5 bg-yellow-400/10 px-3 py-1.5 rounded-full">
            <Star className="w-4 h-4" fill="currentColor" /> 
            {movie.score?.toFixed(2) || '0.00'}
          </span>
        </div>
      </div>
    </div>
  );
};