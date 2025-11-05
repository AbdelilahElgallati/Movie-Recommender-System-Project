import React, { useState, useEffect, useCallback } from 'react';
import { SearchBar } from './SearchBar';
import { ErrorMessage } from './ErrorMessage';
import { GenreFilter } from './GenreFilter';
import { LoadingSpinner } from './LoadingSpinner';
import { MovieGrid } from './MovieGrid';
import { Pagination } from './Pagination';
import type { CurrentUser } from '../utils/types'; 

const API_URL = 'http://127.0.0.1:5001';

interface HomePageProps {
  navigateTo: (pageName: string, movie?: any) => void;
  currentUser: CurrentUser;
  userRatings: Record<string | number, number>; // <-- NOUVEAU
  onRatingChange: (movieId: string | number, rating: number) => void; // <-- NOUVEAU
}

export const HomePage = ({ navigateTo, currentUser, userRatings, onRatingChange }: HomePageProps) => {
  const [movies, setMovies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  // L'état local userRatings et handleRatingChange sont supprimés
  
  const fetchMovies = useCallback(async (search: string, genre: string, pageNum: number) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        search: search,
        genre: genre,
        page: pageNum.toString()
      });
      const response = await fetch(`${API_URL}/api/movies?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch movies');
      const data = await response.json();
      setMovies(data.movies);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMovies('', '', 1);
  }, [fetchMovies]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      setPage(1);
      fetchMovies(searchTerm, selectedGenre, 1);
    }, 500); 
    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, selectedGenre, fetchMovies]);
  
  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) return;
    setPage(newPage);
    fetchMovies(searchTerm, selectedGenre, newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // La fonction handleRatingChange est supprimée

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-10">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          Discover Amazing Movies
        </h1>
        <p className="text-gray-400 text-lg">
          Explore thousands of movies and find your next favorite
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <SearchBar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />
        <GenreFilter selectedGenre={selectedGenre} setSelectedGenre={setSelectedGenre} />
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && (
        <>
          <MovieGrid 
            movies={movies} 
            onMovieClick={(movie) => navigateTo('movie', movie)}
            userRatings={userRatings} // <-- Prop globale
            onRatingChange={onRatingChange} // <-- Prop globale
          />
          <Pagination currentPage={page} totalPages={totalPages} onPageChange={handlePageChange} />
        </>
      )}
    </div>
  );
};