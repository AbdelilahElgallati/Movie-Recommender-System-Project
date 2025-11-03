import React, { useState } from 'react';
import { 
  Clapperboard, 
  Home, 
  Sparkles, 
  User, 
  LogIn,
  LogOut,
  UserPlus,
} from 'lucide-react';
import type { CurrentUser } from '../utils/types'; // <-- CHANGER L'IMPORT

const API_URL = 'http://127.0.0.1:5001';

interface NavbarProps {
  navigateTo: (pageName: string) => void;
  currentPage: string;
  currentUser: CurrentUser;
  setCurrentUser: (user: CurrentUser) => void;
}

export const Navbar = ({ navigateTo, currentPage, currentUser, setCurrentUser }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [inputUsername, setInputUsername] = useState('');
  const [inputPassword, setInputPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const NavLink = ({ page, label, icon: Icon }) => {
    const isActive = currentPage === page;
    return (
      <button
        onClick={() => navigateTo(page)}
        className={`group flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
          isActive
            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/50'
            : 'text-gray-300 hover:bg-gray-800 hover:text-white'
        }`}
      >
        <Icon className={`w-5 h-5 ${isActive ? 'animate-pulse' : 'group-hover:scale-110 transition-transform'}`} />
        <span>{label}</span>
      </button>
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    if (!inputUsername.trim() || !inputPassword.trim()) {
      setError("Username and password are required.");
      setLoading(false);
      return;
    }

    const endpoint = isLogin ? '/api/login' : '/api/signup';
    
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: inputUsername.trim(),
          password: inputPassword.trim()
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'An unknown error occurred');
      }

      setCurrentUser({ id: data.userId.toString(), username: data.username });
      setInputUsername('');
      setInputPassword('');
      setError(null);
      
      if (!isLogin) {
        navigateTo('profile');
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setCurrentUser({ id: null, username: null });
    navigateTo('home'); 
  };

  return (
    <nav className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl fixed top-0 left-0 right-0 z-50 border-b border-gray-700/50 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <div className="flex items-center">
            <button onClick={() => navigateTo('home')} className="flex-shrink-0 flex items-center space-x-3 group">
              <div className="relative">
                <Clapperboard className="h-10 w-10 text-indigo-500 group-hover:text-indigo-400 transition-colors" />
                <div className="absolute inset-0 bg-indigo-500 blur-xl opacity-50 group-hover:opacity-75 transition-opacity"></div>
              </div>
              <span className="text-white text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                FilmRec
              </span>
            </button>
          </div>
          
          <div className="flex items-center">
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-2">
                <NavLink page="home" label="Home" icon={Home} />
                <NavLink page="discover" label="Discover" icon={Sparkles} />
                {currentUser.id && (
                  <NavLink page="profile" label="My Recommendations" icon={User} />
                )}
              </div>
            </div>
            
            <div className="ml-6 pl-6 border-l border-gray-700">
              {currentUser.id ? (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2 bg-gray-800/50 px-4 py-2 rounded-lg">
                    <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">{currentUser.username[0].toUpperCase()}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-300">{currentUser.username}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-2 text-gray-300 hover:bg-red-500/10 hover:text-red-400 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
              ) : (
                <div>
                  <form onSubmit={handleSubmit} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={inputUsername}
                      onChange={(e) => setInputUsername(e.target.value)}
                      placeholder="Username"
                      className="bg-gray-800/70 border border-gray-600 rounded-lg py-2 px-3 text-sm w-32 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      required
                    />
                    <input
                      type="password"
                      value={inputPassword}
                      onChange={(e) => setInputPassword(e.target.value)}
                      placeholder="Password"
                      className="bg-gray-800/70 border border-gray-600 rounded-lg py-2 px-3 text-sm w-32 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      required
                    />
                    <button
                      type="submit"
                      disabled={loading}
                      className={`flex items-center space-x-2 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50 shadow-lg ${
                        isLogin 
                          ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600' 
                          : 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600'
                      }`}
                    >
                      {isLogin ? <LogIn className="w-4 h-4" /> : <UserPlus className="w-4 h-4" />}
                      <span>{loading ? '...' : (isLogin ? 'Login' : 'Sign Up')}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setIsLogin(!isLogin);
                        setError(null);
                      }}
                      className="text-indigo-400 hover:text-indigo-300 text-sm underline pl-2 transition-colors"
                    >
                      {isLogin ? 'Create Account' : 'Login'}
                    </button>
                  </form>
                  {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};