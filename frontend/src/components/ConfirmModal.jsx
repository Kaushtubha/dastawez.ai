import React from 'react';

const ConfirmModal = ({
  isOpen,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'danger',
  onConfirm,
  onCancel
}) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10000,
        background: 'rgba(5, 5, 12, 0.78)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
        animation: 'fadeIn 0.15s ease-out'
      }}
      onClick={onCancel}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '460px',
          background: 'rgba(20, 16, 42, 0.98)',
          border: confirmVariant === 'danger' ? '1px solid rgba(239, 68, 68, 0.35)' : '1px solid var(--border-glass-glow)',
          boxShadow: confirmVariant === 'danger'
            ? '0 20px 40px -10px rgba(239, 68, 68, 0.25)'
            : '0 20px 40px -10px rgba(0, 0, 0, 0.6)',
          borderRadius: '16px',
          padding: '1.8rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.2rem'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: confirmVariant === 'danger' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(124, 58, 237, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.4rem',
              flexShrink: 0
            }}
          >
            {confirmVariant === 'danger' ? '⚠️' : 'ℹ️'}
          </div>

          <div style={{ flex: 1 }}>
            <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700 }}>
              {title}
            </h3>
            <p
              style={{
                margin: '0.5rem 0 0',
                fontSize: '0.92rem',
                color: 'var(--text-muted)',
                lineHeight: 1.5
              }}
            >
              {message}
            </p>
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '0.8rem',
            marginTop: '0.4rem',
            paddingTop: '0.8rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.06)'
          }}
        >
          <button
            onClick={onCancel}
            className="btn-secondary"
            style={{ padding: '0.55rem 1.2rem', fontSize: '0.88rem' }}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            style={{
              padding: '0.55rem 1.3rem',
              fontSize: '0.88rem',
              fontWeight: 600,
              borderRadius: '8px',
              cursor: 'pointer',
              border: 'none',
              transition: 'all 0.2s ease',
              background: confirmVariant === 'danger'
                ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                : 'linear-gradient(135deg, var(--primary-color) 0%, var(--accent-pink) 100%)',
              color: '#ffffff',
              boxShadow: confirmVariant === 'danger'
                ? '0 4px 14px rgba(239, 68, 68, 0.4)'
                : '0 4px 14px var(--primary-glow)'
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
