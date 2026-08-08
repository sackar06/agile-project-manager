import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-card">
      <div className="error-card-content">
        <AlertTriangle className="error-icon" size={24} />
        <div>
          <h4 className="error-title">Error Encountered</h4>
          <p className="error-message-text">{message || 'Failed to complete operation.'}</p>
        </div>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-outline btn-sm mt-3">
          <RefreshCw size={14} /> Try Again
        </button>
      )}
    </div>
  );
}
