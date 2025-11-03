import React from 'react';
import { 
  AlertTriangle,
} from 'lucide-react';

export const ErrorMessage = ({ message }) => (
  <div className="bg-gradient-to-r from-red-900/50 to-red-800/50 border border-red-700 text-red-300 px-6 py-4 rounded-xl flex items-center gap-4 shadow-lg">
    <AlertTriangle className="w-6 h-6 flex-shrink-0" />
    <span className="font-medium">{message}</span>
  </div>
);