import React from 'react';

export function StatusBadge({ status }) {
  if (!status) return null;

  const normalized = String(status).toUpperCase();

  const getStyleClass = () => {
    switch (normalized) {
      case 'PLANNING':
        return 'badge-blue';
      case 'ACTIVE':
        return 'badge-green';
      case 'COMPLETED':
        return 'badge-purple';
      case 'TODO':
        return 'badge-slate';
      case 'IN_PROGRESS':
        return 'badge-amber';
      case 'DONE':
        return 'badge-emerald';
      case 'PENDING':
        return 'badge-amber';
      case 'RUNNING':
        return 'badge-sky';
      case 'FAILED':
        return 'badge-red';
      default:
        return 'badge-slate';
    }
  };

  const formatLabel = () => {
    return normalized.replace('_', ' ');
  };

  return (
    <span className={`status-badge-custom ${getStyleClass()}`}>
      <span className="badge-dot" />
      {formatLabel()}
    </span>
  );
}
