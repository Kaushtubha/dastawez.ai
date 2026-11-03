import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import MatrixBackground from '../components/MatrixBackground';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const res = await login(email, password);
    if (res.success) {
      navigate('/dashboard');
    } else {
      setError(res.error);
    }
  };

  return (
    <div className="auth-wrapper">
      <MatrixBackground opacity={0.28} color="purple" />
      <div className="orb orb-primary" />
      <div className="orb orb-secondary" />

      <div className="auth-container">
        {/* Branding Side */}
        <div className="auth-branding">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1.5rem' }}>
              <div style={{
                width: '45px',
                height: '45px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.4rem',
                boxShadow: '0 0 20px rgba(102, 126, 234, 0.6)'
              }}>
                📄
              </div>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>
                Dastawez<span className="gradient-text">.ai</span>
              </h1>
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '1.05rem', lineHeight: 1.6, marginBottom: '2rem' }}>
              Enterprise-grade document intelligence, layout-preserving extraction, and verified Q&A.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <span style={{ fontSize: '1.2rem' }}>⚡</span>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Multi-Format Parsing</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>PDF, DOCX, TXT with spatial layout tracking</p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <span style={{ fontSize: '1.2rem' }}>🎯</span>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Attributed AI Q&A</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Confidence scoring and exact page citations</p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <span style={{ fontSize: '1.2rem' }}>📊</span>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Visual Document Analytics</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Element distributions and keyword density</p>
                </div>
              </div>
            </div>
          </div>

          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            DocuMind AI Engine v1.0.0 • Secure & Encrypted
          </div>
        </div>

        {/* Form Side */}
        <div className="auth-form-side">
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>Welcome Back</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Sign in to access your document workspace
            </p>
          </div>

          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#fca5a5',
              padding: '0.75rem 1rem',
              borderRadius: '10px',
              fontSize: '0.85rem',
              marginBottom: '1.5rem'
            }}>
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.4rem', color: 'var(--text-muted)' }}>
                Email or Username
              </label>
              <input
                type="text"
                className="input-glass"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.4rem', color: 'var(--text-muted)' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input-glass"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    fontSize: '1rem'
                  }}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
              style={{ width: '100%', marginTop: '0.6rem', padding: '0.9rem' }}
            >
              {loading ? 'Authenticating...' : 'Sign In →'}
            </button>
          </form>

          <p style={{ marginTop: '1.8rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: 'var(--accent-pink)', textDecoration: 'none', fontWeight: 600 }}>
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

