import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import MatrixBackground from '../components/MatrixBackground';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const res = await register(username, email, password);
    if (res.success) {
      navigate('/dashboard');
    } else {
      setError(res.error);
    }
  };

  return (
    <div className="auth-wrapper">
      <MatrixBackground opacity={0.28} color="pink" />
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
                background: 'linear-gradient(135deg, #f093fb, #f5576c)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.4rem',
                boxShadow: '0 0 20px rgba(240, 147, 251, 0.6)'
              }}>
                🚀
              </div>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>
                Get Started<span className="gradient-text">.ai</span>
              </h1>
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '1.05rem', lineHeight: 1.6, marginBottom: '2rem' }}>
              Create your account to unlock automated document parsing, semantic indexing, and natural language Q&A.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <span style={{ fontSize: '1.2rem' }}>🛡️</span>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Zero Data Leakage</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Strict prompt guardrails and isolated tenant scopes</p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <span style={{ fontSize: '1.2rem' }}>📑</span>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>200+ Page Scale</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Proven performance on large technical manuals & contracts</p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <span style={{ fontSize: '1.2rem' }}>📈</span>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Interactive Visualizations</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Dynamic Chart.js metrics for each document</p>
                </div>
              </div>
            </div>
          </div>

          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            Free Developer Tier • Instant Activation
          </div>
        </div>

        {/* Form Side */}
        <div className="auth-form-side">
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>Create Account</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Join Dastawez.ai today
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
                Full Name / Username
              </label>
              <input
                type="text"
                className="input-glass"
                placeholder="kaushan"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.4rem', color: 'var(--text-muted)' }}>
                Email Address
              </label>
              <input
                type="email"
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
              <input
                type="password"
                className="input-glass"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
              style={{ width: '100%', marginTop: '0.6rem', padding: '0.9rem', background: 'linear-gradient(135deg, #f093fb, #764ba2)' }}
            >
              {loading ? 'Creating Account...' : 'Register Workspace →'}
            </button>
          </form>

          <p style={{ marginTop: '1.8rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;

