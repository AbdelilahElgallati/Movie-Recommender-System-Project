import React from 'react';
import {  
  Search, 
  X, 
} from 'lucide-react';

export const SearchBar = ({ searchTerm, setSearchTerm }) => (
  <div className="relative flex-grow">
    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
    <input
      type="text"
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search for movies..."
      className="w-full bg-gray-800/70 border border-gray-700 rounded-xl py-3.5 pl-12 pr-12 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-white placeholder-gray-400"
    />
    {searchTerm && (
      <button 
        onClick={() => setSearchTerm('')} 
        className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
      >
        <X className="w-5 h-5" />
      </button>
    )}
  </div>
);