import React, { useState, useEffect } from 'react';
import { DiscoverPage } from './components/DiscoverPage';
import { Footer } from './components/Footer';
import { HomePage } from './components/HomePage';
import { MovieDetailPage } from './components/MovieDetailPage';
import { Navbar } from './components/Navbar';
import { ProfilePage } from './components/ProfilePage';
import type { CurrentUser, Movie } from './utils/types'; 

const API_URL = 'http://127.0.0.1:5001';

export default function App() {
  const [page, setPage] = useState('home'); 
  const [selectedMovie, setSelectedMovie] = useState<any>(null); 
  
  const [currentUser, setCurrentUser] = useState<CurrentUser>(() => {
    try {
      const storedUser = localStorage.getItem('currentUser');
      if (storedUser) {
        return JSON.parse(storedUser);
      }
    } catch (e) {
      console.error("Failed to parse user from localStorage", e);
    }
    return { id: null, username: null };
  });

  const [userRatings, setUserRatings] = useState<Record<string | number, number>>({});

  useEffect(() => {
    if (currentUser.id) {
      const fetchRatings = async () => {
        try {
          const res = await fetch(`${API_URL}/api/user/${currentUser.id}/ratings`);
          if (res.ok) {
            const moviesData: Movie[] = await res.json();
            const ratingsMap = moviesData.reduce((acc, movie) => {
              // S'assurer d'utiliser la bonne clé (movie_id ou id)
              const id = movie.movie_id || movie.id;
              if (id && movie.rating) {
                acc[id] = movie.rating;
              }
              return acc;
            }, {});
            setUserRatings(ratingsMap);
          }
        } catch (e) {
          console.error("Failed to fetch user ratings", e);
        }
      };
      fetchRatings();
    } else {
      setUserRatings({}); 
    }
  }, [currentUser.id]);

  const handleRatingChange = async (movieId: string | number, newRating: number) => {
    if (!currentUser.id) { 
      alert("Please login to rate movies.");
      return;
    }

    const oldRatings = { ...userRatings };
    setUserRatings(prevRatings => ({
      ...prevRatings,
      [movieId]: newRating
    }));

    try {
      const res = await fetch(`${API_URL}/api/rate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          movie_id: Number(movieId), 
          rating: newRating,
          user_id: parseInt(currentUser.id, 10) 
        })
      });
      if (!res.ok) throw new Error('Failed to save rating');
    } catch (err) {
      console.error("Failed to send rating to API:", err);
      setUserRatings(oldRatings); 
    }
  };

  const navigateTo = (pageName: string, movie: any = null) => {
    setPage(pageName);
    setSelectedMovie(movie);
    window.scrollTo({ top: 0, behavior: 'smooth' }); 
  };
  
  const handleSetCurrentUser = (user: CurrentUser) => {
    if (user.id) {
      localStorage.setItem('currentUser', JSON.stringify(user));
    } else {
      localStorage.removeItem('currentUser');
    }
    setCurrentUser(user);
  };

  const renderPage = () => {
    switch (page) {
      case 'home':
        return <HomePage 
                  navigateTo={navigateTo} 
                  currentUser={currentUser}
                  userRatings={userRatings}
                  onRatingChange={handleRatingChange} 
                />;
      case 'movie':
        return <MovieDetailPage 
                  movie={selectedMovie} 
                  navigateTo={navigateTo}
                  userRatings={userRatings}
                  onRatingChange={handleRatingChange}
                />;
      case 'discover':
        return <DiscoverPage 
                  navigateTo={navigateTo} 
                  userRatings={userRatings}
                  onRatingChange={handleRatingChange}
                />;
      case 'profile':
        return <ProfilePage 
                  navigateTo={navigateTo} 
                  currentUser={currentUser}
                  userRatings={userRatings}
                  onRatingChange={handleRatingChange}
                />;
      default:
        return <HomePage 
                  navigateTo={navigateTo} 
                  currentUser={currentUser}
                  userRatings={userRatings}
                  onRatingChange={handleRatingChange} 
                />;
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white min-h-screen font-sans">
      <Navbar 
        navigateTo={navigateTo} 
        currentPage={page} 
        currentUser={currentUser}
        setCurrentUser={handleSetCurrentUser} // Utiliser la nouvelle fonction
      />
      <main className="pt-24 pb-8">
        {renderPage()}
      </main>
      <Footer />
    </div>
  );
}