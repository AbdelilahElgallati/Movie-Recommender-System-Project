import React, { useState, useEffect } from 'react';
import { ErrorMessage } from './ErrorMessage';
import { LoadingSpinner } from './LoadingSpinner';
import { MovieGrid } from './MovieGrid';
import { Film, Sparkles, Calendar, ExternalLink, Star, Clock, Users } from 'lucide-react';

const API_URL = 'http://127.0.0.1:5001';
const PLACEHOLDER_IMG = 'https://placehold.co/500x750/1e293b/94a3b8?text=No+Image+Available';

interface MovieDetailPageProps {
  movie: any;
  navigateTo: (pageName: string, movie?: any) => void;
  userRatings: Record<string | number, number>; // <-- NOUVEAU
  onRatingChange: (movieId: string | number, rating: number) => void; // <-- NOUVEAU
}

export const MovieDetailPage = ({ movie, navigateTo, userRatings, onRatingChange }: MovieDetailPageProps) => {
  const [details, setDetails] = useState<any>(null);
  const [similarMovies, setSimilarMovies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!movie) {
      setError("No movie selected");
      setLoading(false);
      return;
    }

    const fetchDetails = async () => {
      setLoading(true);
      setError(null);
      setDetails(null);
      setSimilarMovies([]);

      try {
        const movieId = movie.id || movie.movie_id;
        
        if (!movieId) {
          throw new Error('Movie ID not found');
        }

        const detailRes = await fetch(`${API_URL}/api/movie/${movieId}`);
        if (!detailRes.ok) throw new Error('Failed to fetch movie details');
        const detailData = await detailRes.json();
        setDetails(detailData);

        try {
          const similarRes = await fetch(
            `${API_URL}/api/similar/${encodeURIComponent(movie.title)}`
          );
          if (similarRes.ok) {
            const similarData = await similarRes.json();
            
            const normalizedSimilar = similarData.slice(0, 10).map(m => ({
              ...m,
              id: m.id || m.movie_id
            }));
            
            setSimilarMovies(normalizedSimilar);
          }
        } catch (similarErr) {
          console.warn("Similar movies fetch failed:", similarErr);
          setSimilarMovies([]);
        }
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [movie]);

  if (loading) return <div className="h-[80vh] flex items-center justify-center"><LoadingSpinner /></div>;
  if (error) return <div className="container mx-auto px-4 py-8"><ErrorMessage message={error} /></div>;
  if (!details) return <div className="container mx-auto px-4 py-8"><ErrorMessage message="Movie details not available" /></div>;

  const imageUrl = details.poster_url && !details.poster_url.includes('placeholder') 
    ? details.poster_url 
    : PLACEHOLDER_IMG;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-sm border border-gray-700/50">
        {/* ... (contenu de la page de détail, pas de changement ici) ... */}
         <div className="flex flex-col lg:flex-row gap-8 p-8">
          <div className="lg:w-1/3 flex justify-center">
            <div className="relative group max-w-sm">
              <div className="absolute inset-0 bg-gradient-to-t from-indigo-600/20 to-transparent rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <img
                src={imageUrl}
                alt={details.title}
                className="w-full h-auto rounded-xl shadow-2xl object-cover max-h-[600px]"
                onError={(e) => {
                  e.currentTarget.src = PLACEHOLDER_IMG;
                }}
              />
            </div>
          </div>

          <div className="lg:w-2/3 space-y-6">
            <div>
              <h1 className="text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                {details.title}
              </h1>

              <div className="flex flex-wrap gap-4 mb-4">
                {details.release_date && details.release_date !== "Unknown" && (
                  <p className="text-lg text-gray-400 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-indigo-400" />
                    {details.release_date}
                  </p>
                )}

                {details.year && (
                  <p className="text-lg text-gray-400 flex items-center gap-2">
                    <Users className="w-5 h-5 text-indigo-400" />
                    {details.year}
                  </p>
                )}

                {details.runtime && (
                  <p className="text-lg text-gray-400 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-indigo-400" />
                    {details.runtime}
                  </p>
                )}
              </div>
            </div>

            {details.imdb_rating && (
              <div className="flex items-center gap-4 mb-4">
                <div className="flex items-center gap-2 bg-yellow-600/20 px-4 py-2 rounded-lg border border-yellow-500/30">
                  <Star className="w-5 h-5 text-yellow-400" fill="currentColor" />
                  <span className="text-yellow-400 font-semibold">
                    IMDb: {details.imdb_rating}/10
                  </span>
                </div>
              </div>
            )}

            {details.genres && details.genres.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {details.genres.map((genre: string) => (
                  <span
                    key={genre}
                    className="px-4 py-2 bg-gradient-to-r from-gray-700 to-gray-800 text-sm rounded-full font-medium border border-gray-600 hover:border-indigo-500 transition-colors"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            )}

            <div className="border-t border-gray-700 pt-6">
              <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                <Film className="w-6 h-6 text-indigo-400" />
                Synopsis
              </h2>
              <p className="text-gray-300 leading-relaxed text-lg">
                {details.overview}
              </p>
            </div>

            {details.director && (
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-300">Director</h3>
                <p className="text-gray-400">{details.director}</p>
              </div>
            )}

            {details.cast && details.cast.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2 text-gray-300">Cast</h3>
                <div className="flex flex-wrap gap-2">
                  {details.cast.map((actor: string, index: number) => (
                    <span key={index} className="px-3 py-1 bg-gray-700/50 rounded-full text-sm text-gray-300">
                      {actor}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {details.imdb_url && (
              <a
                href={details.imdb_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-3 bg-gradient-to-r from-yellow-500 to-yellow-600 text-black px-6 py-3 rounded-xl font-semibold hover:from-yellow-400 hover:to-yellow-500 transition-all shadow-lg hover:shadow-yellow-500/50 hover:scale-105"
              >
                <ExternalLink className="w-5 h-5" />
                View on IMDb
              </a>
            )}
          </div>
        </div>
      </div>

      {similarMovies.length > 0 && (
        <div className="mt-16">
          <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-indigo-400" />
            Similar Movies
          </h2>
          <MovieGrid
            movies={similarMovies}
            onMovieClick={(m) => navigateTo('movie', m)}
            userRatings={userRatings} // <-- Passage des props
            onRatingChange={onRatingChange} // <-- Passage des props
          />
        </div>
      )}
    </div>
  );
};