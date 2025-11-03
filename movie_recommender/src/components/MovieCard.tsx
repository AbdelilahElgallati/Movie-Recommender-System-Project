import React from 'react';
import { StarRating } from './StarRating';
import { Film } from 'lucide-react';

// URL de l'image de remplacement
const PLACEHOLDER_IMG = 'https://placehold.co/500x750/1e293b/94a3b8?text=';

interface MovieCardProps {
  movie: any;
  onClick: () => void;
  rating: number;
  onRatingChange: (movieId: string | number, rating: number) => void;
}

export const MovieCard = ({ movie, onClick, rating, onRatingChange }: MovieCardProps) => {
  const movieId = movie.id || movie.movie_id;
  
  const getImageUrl = () => {
    if (movie.poster_url && !movie.poster_url.includes('placeholder')) {
      return movie.poster_url;
    }
    return `${PLACEHOLDER_IMG}${encodeURIComponent(movie.title?.substring(0, 20) || 'No+Image')}`;
  };

  const imageUrl = getImageUrl();

  return (
    <div className="group relative bg-gradient-to-b from-gray-800 to-gray-900 rounded-xl overflow-hidden shadow-lg hover:shadow-2xl hover:shadow-indigo-500/20 transition-all duration-300 transform hover:-translate-y-2">
      <button 
        onClick={onClick}
        className="block w-full relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10" />
        <img
          src={imageUrl}
          alt={movie.title}
          className="w-full h-auto object-cover aspect-[2/3] group-hover:scale-110 transition-transform duration-500"
          onError={(e) => { 
            e.currentTarget.src = PLACEHOLDER_IMG + 'No+Image'; 
          }}
        />
        <div className="absolute bottom-0 left-0 right-0 p-3 transform translate-y-full group-hover:translate-y-0 transition-transform duration-300 z-20">
          <div className="flex items-center gap-2 text-white">
            <Film className="w-4 h-4" />
            <span className="text-sm font-medium">View Details</span>
          </div>
        </div>
      </button>

      <div className="p-4">
        <button onClick={onClick} className="w-full text-left mb-3">
          <h3 className="text-sm font-semibold text-white line-clamp-2 group-hover:text-indigo-400 transition-colors" title={movie.title}>
            {movie.title}
          </h3>
        </button>

        <div onClick={(e) => e.stopPropagation()}>
          <StarRating 
            rating={rating || 0} 
            onRatingChange={(newRating) => onRatingChange(movieId, newRating)}
            size="sm"
          />
        </div>
      </div>
    </div>
  );
};