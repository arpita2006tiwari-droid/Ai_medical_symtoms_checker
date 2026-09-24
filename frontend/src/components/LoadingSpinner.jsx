import React from 'react';

const LoadingSpinner = ({ text = "Loading..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      <p className="text-slate-500 font-medium animate-pulse">{text}</p>
    </div>
  );
};

export default LoadingSpinner;
