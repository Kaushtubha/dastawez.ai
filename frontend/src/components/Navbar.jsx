import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import ShortcutModal from './ShortcutModal';
import SpotlightModal from './SpotlightModal';
import api from '../services/api';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { toggleTheme, currentThemeConfig } = useTheme();
  const navigate = useNavigate();
  const [isOnline, setIsOnline] = useState(true);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showSpotlight, setShowSpotlight] = useState(false);

  useEffect(() => {
    api.get('/health')
      .then(() => setIsOnline(true))
      .catch(() => setIsOnline(false));
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div 
          onClick={() => navigate('/dashboard')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}
        >
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
            boxShadow: '0 0 15px rgba(102, 126, 234, 0.5)'
          }}>
            📄
          </div>
          <div>
            <span style={{ fontWeight: 800, fontSize: '1.25rem', letterSpacing: '-0.02em' }}>
              Dastawez<span className="gradient-text">.ai</span>
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', display: 'block', marginTop: '-3px' }}>
              DocuMind Enterprise IDP
            </span>
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          marginLeft: '0.5rem',
          padding: '0.2rem 0.6rem',
          borderRadius: '999px',
          background: isOnline ? 'rgba(52, 211, 153, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${isOnline ? 'rgba(52, 211, 153, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          fontSize: '0.72rem',
          color: isOnline ? '#34d399' : '#f87171'
        }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: isOnline ? '#10b981' : '#ef4444',
            boxShadow: isOnline ? '0 0 8px #10b981' : 'none'
          }} />
          {isOnline ? 'ENGINE ONLINE' : 'OFFLINE'}
        </div>

        {/* Global Spotlight Search Launcher Pill */}
        <button
          onClick={() => setShowSpotlight(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '8px',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            color: 'var(--text-dim)',
            fontSize: '0.8rem',
            cursor: 'pointer',
            marginLeft: '0.5rem',
            transition: 'all 0.2s ease'
          }}
          title="Search documents and commands (Ctrl+K)"
        >
          <span>🔍 Quick Search...</span>
          <kbd style={{
            fontSize: '0.68rem',
            padding: '0.12rem 0.38rem',
            borderRadius: '4px',
            background: 'rgba(255, 255, 255, 0.08)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            fontFamily: 'monospace',
            color: 'var(--text-muted)'
          }}>
            Ctrl+K
          </kbd>
        </button>
      </div>

      <div className="nav-links">
        <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          📊 Dashboard
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          📁 History
        </NavLink>
        <NavLink to="/chat" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          💬 AI Q&A
        </NavLink>
        <NavLink to="/profile" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          👤 {user?.username || 'Profile'}
        </NavLink>

        {/* Ambient Theme Selector Button */}
        <button
          onClick={toggleTheme}
          className="btn-secondary"
          style={{ padding: '0.45rem 0.75rem', fontSize: '0.85rem' }}
          title={`Active Theme: ${currentThemeConfig?.name || 'Theme'}. Click to switch accent.`}
        >
          {currentThemeConfig?.icon || '🎨'}
        </button>

        {/* Keyboard Shortcuts Trigger Button */}
        <button
          onClick={() => setShowShortcuts(true)}
          className="btn-secondary"
          style={{ padding: '0.45rem 0.75rem', fontSize: '0.9rem' }}
          title="Keyboard Shortcuts (?)"
        >
          ⌨️
        </button>

        <button onClick={handleLogout} className="btn-secondary" style={{ padding: '0.45rem 1rem', fontSize: '0.85rem' }}>
          Logout
        </button>
      </div>

      <ShortcutModal isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
      <SpotlightModal isOpen={showSpotlight} onClose={() => setShowSpotlight(false)} />
    </nav>
  );
};

export default Navbar;
