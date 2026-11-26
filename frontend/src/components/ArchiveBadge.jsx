import React, { useState } from 'react';

const ArchiveBadge = ({ isArchived, archivedAt, onRestore }) => {
  const [isRestoring, setIsRestoring] = useState(false);

  if (!isArchived) {
    return null;
  }

  const handleRestore = async (e) => {
    e.stopPropagation();
    if (!onRestore) return;
    setIsRestoring(true);
    try {
      await onRestore();
    } finally {
      setIsRestoring(false);
    }
  };

  const formattedDate = archivedAt
    ? new Date(archivedAt).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    : null;

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '3px 8px',
        borderRadius: '6px',
        fontSize: '0.72rem',
        fontWeight: 600,
        backgroundColor: 'rgba(245, 158, 11, 0.15)',
        color: '#fbbf24',
        border: '1px solid rgba(245, 158, 11, 0.35)',
        backdropFilter: 'blur(4px)'
      }}
      title={formattedDate ? `Archived on ${formattedDate}` : 'Archived document'}
    >
      <span>📦 Archived</span>
      {onRestore && (
        <button
          type="button"
          onClick={handleRestore}
          disabled={isRestoring}
          style={{
            background: 'rgba(251, 191, 36, 0.2)',
            border: 'none',
            borderRadius: '4px',
            color: '#fbbf24',
            cursor: isRestoring ? 'wait' : 'pointer',
            padding: '1px 5px',
            fontSize: '0.68rem',
            fontWeight: 700,
            transition: 'background 0.2s ease'
          }}
        >
          {isRestoring ? '...' : 'Restore'}
        </button>
      )}
    </div>
  );
};

export default ArchiveBadge;
