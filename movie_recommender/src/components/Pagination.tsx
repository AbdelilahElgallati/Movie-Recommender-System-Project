import React from 'react';
import { 
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;
  
  const pages = [];
  const showPages = 5;
  let startPage = Math.max(1, currentPage - Math.floor(showPages / 2));
  let endPage = Math.min(totalPages, startPage + showPages - 1);
  
  if (endPage - startPage < showPages - 1) {
    startPage = Math.max(1, endPage - showPages + 1);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  return (
    <div className="flex items-center justify-center gap-2 mt-12">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="flex items-center gap-2 px-4 py-2.5 bg-gray-800 rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
      >
        <ChevronLeft className="w-4 h-4" />
        Previous
      </button>
      
      <div className="flex gap-2">
        {startPage > 1 && (
          <>
            <button
              onClick={() => onPageChange(1)}
              className="px-4 py-2.5 bg-gray-800 rounded-lg hover:bg-gray-700 transition-all font-medium"
            >
              1
            </button>
            {startPage > 2 && <span className="px-2 py-2.5 text-gray-500">...</span>}
          </>
        )}
        
        {pages.map(page => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={`px-4 py-2.5 rounded-lg font-medium transition-all ${
              currentPage === page
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            {page}
          </button>
        ))}
        
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span className="px-2 py-2.5 text-gray-500">...</span>}
            <button
              onClick={() => onPageChange(totalPages)}
              className="px-4 py-2.5 bg-gray-800 rounded-lg hover:bg-gray-700 transition-all font-medium"
            >
              {totalPages}
            </button>
          </>
        )}
      </div>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="flex items-center gap-2 px-4 py-2.5 bg-gray-800 rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
      >
        Next
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
};