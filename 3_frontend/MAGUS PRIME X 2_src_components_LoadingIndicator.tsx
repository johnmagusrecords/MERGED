import React from 'react';

interface LoadingIndicatorProps {
  message?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-indicator">
      <div className="spinner"></div>
      {message}
    </div>
  );
};

export default LoadingIndicator;
