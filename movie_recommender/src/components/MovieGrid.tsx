import React from 'react';
import { MovieCard } from './MovieCard';

interface MovieGridProps {
  movies: any[];
  onMovieClick: (movie: any) => void;
  userRatings: Record<string | number, number>;
  onRatingChange: (movieId: string | number, rating: number) => void;
}

export const MovieGrid = ({ movies, onMovieClick, userRatings = {}, onRatingChange }: MovieGridProps) => (
  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
    {movies.map(movie => {
      const movieId = movie.id || movie.movie_id;
      return (
        <MovieCard 
          key={movieId} 
          movie={movie} 
          onClick={() => onMovieClick(movie)}
          rating={userRatings[movieId]}
          onRatingChange={onRatingChange}
        />
      );
    })}
  </div>
);