import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MatrixBackground from '../components/MatrixBackground';
import { useAuth } from '../context/AuthContext';
import { useTheme, THEMES } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { documentService } from '../services/historyService';
import api from '../services/api';

const ProfilePage = () => {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();
  const { showToast } = useToast();
  const [docCount, setDocCount] = useState(0);
  const [totalChunks, setTotalChunks] = useState(0);
  const [health, setHealth] = useState(null);
  const [storageBytes, setStorageBytes] = useState(0);

  useEffect(() => {
    documentService.getDocuments()
      .then((data) => {
        setDocCount(data.total || data.documents?.length || 0);
        let chunks = 0;
        data.documents?.forEach((d) => {
          chunks += d.metadata?.chunks_added || 0;
        });
        setTotalChunks(chunks);
      })
      .catch((e) => console.error(e));

    api.get('/health')
      .then((res) => setHealth(res.data))
      .catch((e) => console.error(e));

    // Calculate approximate localStorage size
    let bytes = 0;
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        bytes += (localStorage[key].length + key.length) * 2;
      }
    }
    setStorageBytes(bytes);
  }, []);

  const handleClearCache = () => {
    const token = localStorage.getItem('dastawez_token');
    const userJson = localStorage.getItem('dastawez_user');
    localStorage.clear();
    if (token) localStorage.setItem('dastawez_token', token);
    if (userJson) localStorage.setItem('dastawez_user', userJson);
    setStorageBytes(0);
    if (showToast) {
      showToast('Client cache and query history purged', 'success', 2000);
    }
  };

  return (
    <div>
      <Navbar />
      <MatrixBackground opacity={0.16} color="cyan" />
      <div className="animated-grid" />
      <div className="orb orb-accent" />

      <main className="main-content">
        <div style={{ marginBottom: '2rem' }}>
          <span className="badge badge-cyan" style={{ marginBottom: '0.6rem' }}>User & Engine Settings</span>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
            Workspace <span className="gradient-text">Profile & Configuration</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginTop: '0.3rem' }}>
            Account details, cluster telemetry, and ambient workspace preferences
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
          {/* User Card */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.2rem', marginBottom: '1.5rem' }}>
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #a78bfa, #f472b6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.8rem',
                boxShadow: '0 0 20px rgba(167, 139, 250, 0.5)'
              }}>
                👤
              </div>
              <div>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>{user?.username || 'Authenticated Operator'}</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{user?.email || 'admin@documind.ai'}</p>
                <span className="badge badge-green" style={{ marginTop: '0.4rem' }}>Active Member</span>
              </div>
            </div>

            <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.8rem', fontSize: '0.9rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-dim)' }}>Role:</span>
                <span style={{ fontWeight: 600 }}>IDP Platform Operator</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-dim)' }}>Session Status:</span>
                <span style={{ color: '#34d399', fontWeight: 600 }}>Active (JWT Authenticated)</span>
              </div>
            </div>
          </div>

          {/* Engine Status Card */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1.2rem' }}>
              ⚡ Cluster & Pipeline Telemetry
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.92rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.6rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Core Engine:</span>
                <span style={{ fontWeight: 600 }}>{health?.app || 'Dastawez.ai - DocuMind'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.6rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Version:</span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>v{health?.version || '1.3.0'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.6rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Documents Ingested:</span>
                <span style={{ fontWeight: 700, color: '#38bdf8' }}>{docCount} files</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.6rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Vector Chunks:</span>
                <span style={{ fontWeight: 700, color: '#f472b6' }}>{totalChunks} units</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Vector Engine:</span>
                <span className="badge badge-purple">Hybrid (Qdrant + TF-IDF)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Ambient Accent Theme Customizer */}
        <div className="glass-panel" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.4rem' }}>
            🎨 Ambient Workspace Themes
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.2rem' }}>
            Choose an accent palette that dynamically customizes gradients, borders, and ambient light orbs across the application.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {Object.values(THEMES).map((th) => {
              const isActive = theme === th.id;
              return (
                <div
                  key={th.id}
                  onClick={() => setTheme(th.id)}
                  style={{
                    padding: '1.2rem',
                    borderRadius: '12px',
                    background: isActive ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                    border: isActive ? `2px solid ${th.primary}` : '1px solid var(--border-glass)',
                    boxShadow: isActive ? `0 0 20px ${th.primary}44` : 'none',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.6rem'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '1.4rem' }}>{th.icon}</span>
                    {isActive && (
                      <span className="badge badge-purple" style={{ fontSize: '0.72rem' }}>Active</span>
                    )}
                  </div>
                  <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{th.name}</h4>
                  <div style={{ display: 'flex', gap: '0.3rem', marginTop: '0.4rem' }}>
                    <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: th.primary }} />
                    <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: th.accentPink }} />
                    <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: th.accentCyan }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Client Storage & Session Management */}
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>
                🧹 Client Storage & Session Cache
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '0.3rem 0 0' }}>
                Local storage footprint: <strong>{Math.round(storageBytes / 1024)} KB</strong>. Clears temporary tokens and UI filters without modifying the database.
              </p>
            </div>
            <button
              onClick={handleClearCache}
              className="btn-secondary"
              style={{ padding: '0.55rem 1.2rem', fontSize: '0.88rem', color: '#f87171' }}
            >
              Purge Local Cache
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
