import React from 'react';
import { AlertTriangle, Home } from 'lucide-react';

export function NotFound({ onGoHome }) {
  return (
    <div className="empty-state-card glass-card my-12 text-center">
      <AlertTriangle size={64} className="text-warning mb-4 mx-auto" />
      <h2>Page Not Found</h2>
      <p className="text-muted mt-2">The page or resource you requested could not be found.</p>
      <button onClick={onGoHome} className="btn btn-primary mt-4">
        <Home size={18} />
        <span>Return to Dashboard</span>
      </button>
    </div>
  );
}
