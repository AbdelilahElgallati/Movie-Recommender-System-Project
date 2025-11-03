import React, { useState } from 'react';
import { 
  Star, 
} from 'lucide-react';

export const StarRating = ({ rating, onRatingChange, size = 'md', interactive = true }) => {
  const [hover, setHover] = useState(0);
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => interactive && onRatingChange(star)}
          onMouseEnter={() => interactive && setHover(star)}
          onMouseLeave={() => interactive && setHover(0)}
          disabled={!interactive}
          className={`transition-all ${interactive ? 'hover:scale-110 cursor-pointer' : 'cursor-default'} focus:outline-none`}
        >
          <Star 
            className={`${sizeClasses[size]} transition-colors ${
              star <= (hover || rating) ? 'text-yellow-400' : 'text-gray-600'
            }`}
            fill={star <= (hover || rating) ? "currentColor" : "none"} 
          />
        </button>
      ))}
      {rating > 0 && <span className="ml-1 text-sm text-gray-400">({rating})</span>}
    </div>
  );
};