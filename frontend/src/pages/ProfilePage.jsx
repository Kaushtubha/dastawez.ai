import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MatrixBackground from '../components/MatrixBackground';
import { useAuth } from '../context/AuthContext';
import { documentService } from '../services/historyService';
import api from '../services/api';

const ProfilePage = () => {
  const { user } = useAuth();
  const [docCount, setDocCount] = useState(0);
  const [totalChunks, setTotalChunks] = useState(0);
  const [health, setHealth] = useState(null);

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
  }, []);

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
            Account details, cluster telemetry, and storage metrics
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
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
                <span style={{ fontFamily: 'var(--font-mono)' }}>v{health?.version || '1.0.0'}</span>
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
      </main>
    </div>
  );
};

export default ProfilePage;

