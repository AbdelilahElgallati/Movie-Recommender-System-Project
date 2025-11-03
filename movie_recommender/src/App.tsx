import React, { useState } from 'react';
import { DiscoverPage } from './components/DiscoverPage';
import { Footer } from './components/Footer';
import { HomePage } from './components/HomePage';
import { MovieDetailPage } from './components/MovieDetailPage';
import { Navbar } from './components/Navbar';
import { ProfilePage } from './components/ProfilePage';

interface CurrentUser {
  id: number | null;
  username: string | null;
}

export default function App() {
  const [page, setPage] = useState('home'); 
  const [selectedMovie, setSelectedMovie] = useState<any>(null); 
  const [currentUser, setCurrentUser] = useState<CurrentUser>({ id: null, username: null }); 

  const navigateTo = (pageName: string, movie: any = null) => {
    setPage(pageName);
    setSelectedMovie(movie);
    window.scrollTo({ top: 0, behavior: 'smooth' }); 
  };

  const renderPage = () => {
    switch (page) {
      case 'home':
        return <HomePage navigateTo={navigateTo} currentUser={currentUser} />;
      case 'movie':
        return <MovieDetailPage movie={selectedMovie} navigateTo={navigateTo} />;
      case 'discover':
        return <DiscoverPage navigateTo={navigateTo} />;
      case 'profile':
        return <ProfilePage navigateTo={navigateTo} currentUser={currentUser} />;
      default:
        return <HomePage navigateTo={navigateTo} currentUser={currentUser} />;
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white min-h-screen font-sans">
      <Navbar 
        navigateTo={navigateTo} 
        currentPage={page} 
        currentUser={currentUser}
        setCurrentUser={setCurrentUser}
      />
      <main className="pt-24 pb-8">
        {renderPage()}
      </main>
      <Footer />
    </div>
  );
}