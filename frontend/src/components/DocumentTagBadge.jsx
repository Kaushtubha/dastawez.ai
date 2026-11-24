import React from 'react';

const PALETTES = [
  { bg: 'rgba(147, 51, 234, 0.18)', border: 'rgba(168, 85, 247, 0.45)', text: '#d8b4fe' }, // Purple
  { bg: 'rgba(14, 165, 233, 0.18)', border: 'rgba(56, 189, 248, 0.45)', text: '#7dd3fc' }, // Cyan
  { bg: 'rgba(16, 185, 129, 0.18)', border: 'rgba(52, 211, 153, 0.45)', text: '#6ee7b7' }, // Emerald
  { bg: 'rgba(245, 158, 11, 0.18)', border: 'rgba(251, 191, 36, 0.45)', text: '#fde68a' }, // Amber
  { bg: 'rgba(244, 63, 94, 0.18)', border: 'rgba(251, 113, 133, 0.45)', text: '#fda4af' }, // Rose
  { bg: 'rgba(99, 102, 241, 0.18)', border: 'rgba(129, 140, 248, 0.45)', text: '#c7d2fe' }  // Indigo
];

function getTagStyle(tag) {
  let hash = 0;
  for (let i = 0; i < tag.length; i++) {
    hash = tag.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % PALETTES.length;
  return PALETTES[index];
}

const DocumentTagBadge = ({ tag, onClick, onRemove, active = false }) => {
  const palette = getTagStyle(tag);

  return (
    <span
      onClick={onClick ? () => onClick(tag) : undefined}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '3px 10px',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: 600,
        letterSpacing: '0.02em',
        cursor: onClick ? 'pointer' : 'default',
        backgroundColor: active ? palette.text : palette.bg,
        color: active ? '#0f172a' : palette.text,
        border: `1px solid ${palette.border}`,
        backdropFilter: 'blur(6px)',
        transition: 'all 0.2s ease',
        boxShadow: active ? `0 0 10px ${palette.border}` : 'none'
      }}
    >
      <span>#{tag}</span>
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove(tag);
          }}
          style={{
            background: 'none',
            border: 'none',
            color: 'inherit',
            cursor: 'pointer',
            padding: 0,
            fontSize: '0.9rem',
            lineHeight: 1,
            display: 'flex',
            alignItems: 'center',
            opacity: 0.7,
            marginLeft: '2px'
          }}
          title={`Remove tag ${tag}`}
        >
          &times;
        </button>
      )}
    </span>
  );
};

export default DocumentTagBadge;
