import React from 'react';

export function PriorityBadge({ priority }) {
  if (!priority) return null;

  const normalized = String(priority).toUpperCase();

  const getStyleClass = () => {
    switch (normalized) {
      case 'HIGH':
        return 'priority-high';
      case 'MEDIUM':
        return 'priority-medium';
      case 'LOW':
        return 'priority-low';
      default:
        return 'priority-low';
    }
  };

  return (
    <span className={`priority-badge ${getStyleClass()}`}>
      {normalized}
    </span>
  );
}
