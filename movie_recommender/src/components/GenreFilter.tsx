import React  from 'react';
import { 
  ChevronDown, 
} from 'lucide-react';


// Liste des genres (basée sur u.item)
const GENRES = [
  'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 
  'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 
  'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
];

export const GenreFilter = ({ selectedGenre, setSelectedGenre }) => (
  <div className="relative">
    <select
      value={selectedGenre}
      onChange={(e) => setSelectedGenre(e.target.value)}
      className="w-full md:w-64 appearance-none bg-gray-800/70 border border-gray-700 rounded-xl py-3.5 px-4 pr-10 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-white cursor-pointer"
    >
      <option value="">All Genres</option>
      {GENRES.map(genre => (
        <option key={genre} value={genre}>{genre}</option>
      ))}
    </select>
    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
  </div>
);