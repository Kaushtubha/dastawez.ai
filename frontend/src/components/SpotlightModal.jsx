import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

const SpotlightModal = ({ isOpen: controlledIsOpen, onClose: controlledOnClose }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [documents, setDocuments] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const { toggleTheme } = useTheme();

  useEffect(() => {
    if (controlledIsOpen !== undefined) {
      setIsOpen(controlledIsOpen);
    }
  }, [controlledIsOpen]);

  useEffect(() => {
    const handleToggle = () => setIsOpen((prev) => !prev);
    const handleClose = () => setIsOpen(false);

    window.addEventListener('toggle-spotlight-modal', handleToggle);
    window.addEventListener('close-modals', handleClose);

    return () => {
      window.removeEventListener('toggle-spotlight-modal', handleToggle);
      window.removeEventListener('close-modals', handleClose);
    };
  }, []);

  // Fetch recent documents when opened
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);

      api.get('/documents')
        .then((res) => {
          if (Array.isArray(res.data)) {
            setDocuments(res.data);
          } else if (res.data?.documents) {
            setDocuments(res.data.documents);
          }
        })
        .catch(() => setDocuments([]));
    }
  }, [isOpen]);

  const handleClose = () => {
    setIsOpen(false);
    if (controlledOnClose) controlledOnClose();
  };

  // Static navigation and actions
  const navItems = [
    { id: 'nav-dash', type: 'page', title: 'Dashboard', subtitle: 'Overview & quick ingest', icon: '📊', action: () => navigate('/dashboard') },
    { id: 'nav-hist', type: 'page', title: 'Document Catalog & History', subtitle: 'Search, filter, and inspect docs', icon: '📁', action: () => navigate('/history') },
    { id: 'nav-chat', type: 'page', title: 'Conversational AI Q&A', subtitle: 'Grounded multi-document synthesis', icon: '💬', action: () => navigate('/chat') },
    { id: 'nav-prof', type: 'page', title: 'User Profile & Settings', subtitle: 'Account credentials & API telemetry', icon: '👤', action: () => navigate('/profile') },
    { id: 'act-theme', type: 'action', title: 'Switch Accent Theme', subtitle: 'Cycle through Cyberpunk, Emerald, etc.', icon: '🎨', action: () => toggleTheme() },
    { id: 'act-help', type: 'action', title: 'Keyboard Shortcut Guide', subtitle: 'View system hotkey reference', icon: '⌨️', action: () => window.dispatchEvent(new CustomEvent('toggle-shortcuts-modal')) }
  ];

  // Filter actions based on query
  const q = query.trim().toLowerCase();
  const matchedNav = navItems.filter((item) =>
    item.title.toLowerCase().includes(q) || item.subtitle.toLowerCase().includes(q)
  );

  // Filter documents based on query
  const matchedDocs = documents.filter((doc) => {
    if (!q) return true;
    const nameMatch = doc.filename?.toLowerCase().includes(q);
    const typeMatch = doc.file_type?.toLowerCase().includes(q);
    return nameMatch || typeMatch;
  }).slice(0, 5);

  const combinedItems = [
    ...matchedNav.map((item) => ({ ...item, kind: 'action' })),
    ...matchedDocs.map((doc) => ({
      id: `doc-${doc.id}`,
      kind: 'document',
      title: doc.filename,
      subtitle: `${doc.file_type?.toUpperCase().replace('.', '') || 'FILE'} • ${doc.chunks_count || doc.total_chunks || 0} chunks • ${(doc.file_size ? (doc.file_size / 1024).toFixed(1) + ' KB' : 'Unknown size')}`,
      icon: doc.file_type === '.pdf' ? '📕' : doc.file_type === '.docx' ? '📘' : doc.file_type === '.md' ? '📝' : '📄',
      action: () => navigate(`/chat?doc=${doc.id}`)
    }))
  ];

  // Keep selectedIndex in bounds
  useEffect(() => {
    if (selectedIndex >= combinedItems.length) {
      setSelectedIndex(Math.max(0, combinedItems.length - 1));
    }
  }, [combinedItems.length, selectedIndex]);

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % Math.max(1, combinedItems.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + combinedItems.length) % Math.max(1, combinedItems.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (combinedItems[selectedIndex]) {
        combinedItems[selectedIndex].action();
        handleClose();
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10002,
        background: 'rgba(5, 5, 12, 0.82)',
        backdropFilter: 'blur(10px)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '10vh',
        paddingLeft: '1.5rem',
        paddingRight: '1.5rem',
        animation: 'fadeIn 0.15s ease-out'
      }}
      onClick={handleClose}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '640px',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          background: 'var(--panel-bg, #0d1117)',
          boxShadow: '0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 30px rgba(99, 102, 241, 0.15)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '1rem 1.25rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <span style={{ fontSize: '1.25rem' }}>🔍</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Type a command, page name, or document filename..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-main, #f3f4f6)',
              fontSize: '1rem',
              fontWeight: 500
            }}
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: 'none',
                color: 'var(--text-dim)',
                borderRadius: '50%',
                width: '22px',
                height: '22px',
                cursor: 'pointer',
                fontSize: '0.75rem'
              }}
            >
              ✕
            </button>
          )}
          <kbd style={{
            fontSize: '0.7rem',
            padding: '0.2rem 0.45rem',
            borderRadius: '4px',
            background: 'rgba(255, 255, 255, 0.08)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            color: 'var(--text-dim)',
            fontFamily: 'monospace'
          }}>
            ESC to close
          </kbd>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: '380px', overflowY: 'auto', padding: '0.5rem' }}>
          {combinedItems.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--text-dim)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔭</div>
              <p style={{ margin: 0, fontWeight: 500 }}>No matching commands or documents found.</p>
              <p style={{ margin: '0.3rem 0 0', fontSize: '0.85rem' }}>Try searching for "PDF", "Dashboard", or "Theme"</p>
            </div>
          ) : (
            combinedItems.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={item.id}
                  onClick={() => {
                    item.action();
                    handleClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.85rem',
                    padding: '0.75rem 1rem',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    border: isSelected ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
                    transition: 'all 0.1s ease-in-out'
                  }}
                >
                  <div style={{
                    width: '34px',
                    height: '34px',
                    borderRadius: '8px',
                    background: isSelected ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.15rem'
                  }}>
                    {item.icon}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontWeight: 600,
                      fontSize: '0.92rem',
                      color: isSelected ? 'var(--primary, #818cf8)' : 'var(--text-main, #f3f4f6)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {item.title}
                    </div>
                    <div style={{
                      fontSize: '0.75rem',
                      color: 'var(--text-dim)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {item.subtitle}
                    </div>
                  </div>
                  <div style={{
                    fontSize: '0.7rem',
                    color: 'var(--text-dim)',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    background: 'rgba(255, 255, 255, 0.04)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {item.kind === 'document' ? 'Ask AI' : 'Jump'}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts hint */}
        <div style={{
          padding: '0.6rem 1.25rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(0, 0, 0, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          color: 'var(--text-dim)'
        }}>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <span><kbd>↑</kbd> <kbd>↓</kbd> Navigate</span>
            <span><kbd>↵</kbd> Select</span>
            <span><kbd>Esc</kbd> Close</span>
          </div>
          <span>Dastawez.ai Spotlight v1.3.1</span>
        </div>
      </div>
    </div>
  );
};

export default SpotlightModal;
