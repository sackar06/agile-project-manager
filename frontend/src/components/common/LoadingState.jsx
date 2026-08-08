import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingState({ message = 'Loading data...' }) {
  return (
    <div className="loading-container">
      <Loader2 className="loading-spinner" size={28} />
      <p className="loading-text">{message}</p>
    </div>
  );
}
