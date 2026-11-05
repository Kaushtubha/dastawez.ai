import React from 'react';
import { useToast } from '../context/ToastContext';

const Toast = () => {
  const { toasts, removeToast } = useToast();

  if (!toasts || toasts.length === 0) return null;

  const getIcon = (type) => {
    switch (type) {
      case 'success': return '✓';
      case 'error': return '✕';
      case 'warning': return '⚠️';
      default: return 'ℹ️';
    }
  };

  const getColor = (type) => {
    switch (type) {
      case 'success': return '#34d399';
      case 'error': return '#f87171';
      case 'warning': return '#fbbf24';
      default: return '#38bdf8';
    }
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: 10001,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      pointerEvents: 'none'
    }}>
      {toasts.map((t) => (
        <div
          key={t.id}
          style={{
            pointerEvents: 'auto',
            background: 'rgba(15, 12, 41, 0.85)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: `1px solid ${getColor(t.type)}40`,
            borderLeft: `4px solid ${getColor(t.type)}`,
            borderRadius: '12px',
            padding: '12px 18px',
            color: '#f8fafc',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(102, 126, 234, 0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            minWidth: '280px',
            maxWidth: '420px',
            fontSize: '0.9rem',
            animation: 'toastSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
          }}
        >
          <span style={{
            color: getColor(t.type),
            fontWeight: 800,
            fontSize: '1rem',
            lineHeight: 1
          }}>
            {getIcon(t.type)}
          </span>
          <span style={{ flex: 1, lineHeight: 1.4 }}>{t.message}</span>
          <button
            onClick={() => removeToast(t.id)}
            style={{
              background: 'none',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '1.1rem',
              padding: '0 4px',
              lineHeight: 1
            }}
          >
            ×
          </button>
        </div>
      ))}
      <style>{`
        @keyframes toastSlideIn {
          from {
            transform: translateX(100%) scale(0.95);
            opacity: 0;
          }
          to {
            transform: translateX(0) scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default Toast;
