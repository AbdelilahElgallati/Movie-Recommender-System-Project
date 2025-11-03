// Fichier : src/utils/types.ts (Mis à Jour)

export interface Movie {
  id: number;
  movie_id?: number;
  title: string;
  rating?: number;
  release_date?: string;
  genres?: string[];
  imdb_url?: string;
  model_used?: string;
  score?: number;
  poster_url?: string; 
}

export interface CurrentUser {
  id: string | null;
  username: string | null;
}

export interface NavigationProps {
  navigateTo: (pageName: string, movie?: Movie | null) => void;
  currentPage?: string;
}

export interface MovieCardProps {
  movie: Movie;
  onClick: (movie: Movie) => void;
}