import React from 'react';
import { 
  Loader2, 
} from 'lucide-react';

export const LoadingSpinner = () => (
  <div className="flex flex-col justify-center items-center py-16">
    <Loader2 className="w-16 h-16 text-indigo-500 animate-spin mb-4" />
    <p className="text-gray-400 text-sm">Loading amazing movies...</p>
  </div>
);