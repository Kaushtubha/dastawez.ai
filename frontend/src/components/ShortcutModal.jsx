import React, { useState, useEffect } from 'react';

const ShortcutModal = ({ isOpen: controlledIsOpen, onClose: controlledOnClose }) => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (controlledIsOpen !== undefined) {
      setIsOpen(controlledIsOpen);
    }
  }, [controlledIsOpen]);

  useEffect(() => {
    const handleToggle = () => setIsOpen((prev) => !prev);
    const handleClose = () => setIsOpen(false);

    window.addEventListener('toggle-shortcuts-modal', handleToggle);
    window.addEventListener('close-modals', handleClose);

    return () => {
      window.removeEventListener('toggle-shortcuts-modal', handleToggle);
      window.removeEventListener('close-modals', handleClose);
    };
  }, []);

  const handleClose = () => {
    setIsOpen(false);
    if (controlledOnClose) controlledOnClose();
  };

  if (!isOpen) return null;

  const shortcuts = [
    { keys: ['Ctrl / Cmd', 'K'], description: 'Open Spotlight Command & Search Palette' },
    { keys: ['Ctrl / Alt', 'D'], description: 'Navigate to Dashboard' },
    { keys: ['Ctrl / Alt', 'H'], description: 'Open Document Archive & History' },
    { keys: ['Ctrl / Alt', 'Q'], description: 'Open AI Q&A Assistant' },
    { keys: ['Ctrl / Alt', 'P'], description: 'Open User Profile & Settings' },
    { keys: ['?'], description: 'Toggle Keyboard Shortcuts Modal' },
    { keys: ['Esc'], description: 'Close active modal / dialog' },
    { keys: ['Ctrl', 'Enter'], description: 'Submit Q&A prompt immediately' }
  ];

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10001,
        background: 'rgba(5, 5, 12, 0.78)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
        animation: 'fadeIn 0.15s ease-out'
      }}
      onClick={handleClose}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '520px',
          background: 'rgba(20, 16, 42, 0.98)',
          border: '1px solid var(--border-glass-glow)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
          borderRadius: '16px',
          padding: '1.8rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.2rem'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '1.4rem' }}>⌨️</span>
            <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700 }}>
              Keyboard Shortcuts
            </h3>
          </div>
          <button
            onClick={handleClose}
            className="btn-secondary"
            style={{ padding: '0.35rem 0.7rem', fontSize: '1rem', lineHeight: 1 }}
          >
            ✕
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.4rem' }}>
          {shortcuts.map((item, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '0.6rem 0.8rem',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)'
              }}
            >
              <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                {item.description}
              </span>
              <div style={{ display: 'flex', gap: '0.3rem', alignItems: 'center' }}>
                {item.keys.map((k, kIdx) => (
                  <kbd
                    key={kIdx}
                    style={{
                      background: 'rgba(255, 255, 255, 0.08)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      boxShadow: '0 2px 0 rgba(0, 0, 0, 0.5)',
                      borderRadius: '5px',
                      padding: '0.2rem 0.5rem',
                      fontSize: '0.75rem',
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--text-main)',
                      fontWeight: 600
                    }}
                  >
                    {k}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: '0.5rem',
            textAlign: 'center',
            fontSize: '0.78rem',
            color: 'var(--text-dim)'
          }}
        >
          Press <kbd style={{ padding: '0.1rem 0.4rem', borderRadius: '4px', background: 'rgba(255,255,255,0.1)' }}>Esc</kbd> anytime to dismiss
        </div>
      </div>
    </div>
  );
};

export default ShortcutModal;
