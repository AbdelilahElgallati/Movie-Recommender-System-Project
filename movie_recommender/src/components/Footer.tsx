import { Clapperboard } from 'lucide-react';
import React from 'react';


export const Footer = () => (
  <footer className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border-t border-gray-700/50 mt-20">
    <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex items-center gap-3">
          <Clapperboard className="h-8 w-8 text-indigo-500" />
          <div>
            <p className="text-white font-bold text-lg">FilmRec</p>
            <p className="text-gray-400 text-sm">Discover your next favorite movie</p>
          </div>
        </div>
        <div className="text-center text-gray-400 text-sm">
          <p>&copy; {new Date().getFullYear()} FilmRec. Built with Flask & React.</p>
          <p className="mt-1">Made with ❤️ for movie lovers</p>
        </div>
      </div>
    </div>
  </footer>
);