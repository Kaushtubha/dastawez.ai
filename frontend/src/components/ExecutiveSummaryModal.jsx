import React, { useState, useEffect } from 'react';
import { documentService } from '../services/historyService';

const ExecutiveSummaryModal = ({ docId, filename, isOpen, onClose }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && docId) {
      loadSummary();
    }
  }, [isOpen, docId]);

  const loadSummary = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await documentService.getDocumentSummary(docId);
      setData(res);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate executive summary.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!data) return;
    const textToCopy = `Executive Summary: ${data.filename}\n\n${data.executive_summary}\n\nKey Insights:\n${(data.key_takeaways || []).map((t) => `• ${t}`).join('\n')}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10002,
        background: 'rgba(5, 5, 12, 0.78)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
        animation: 'fadeIn 0.2s ease-out'
      }}
      onClick={onClose}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '750px',
          maxHeight: '88vh',
          background: 'rgba(18, 15, 38, 0.98)',
          border: '1px solid var(--border-glass-glow)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          style={{
            padding: '1.4rem 1.8rem',
            borderBottom: '1px solid var(--border-glass)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'rgba(255, 255, 255, 0.02)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <span style={{ fontSize: '1.5rem' }}>✨</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700 }}>
                Executive AI Summary
              </h3>
              <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                {filename}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn-secondary"
            style={{ padding: '0.4rem 0.8rem', fontSize: '1.1rem', lineHeight: 1 }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '1.8rem', overflowY: 'auto', flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.8rem' }}>⚙️</div>
              Synthesizing executive brief and highlights...
            </div>
          ) : error ? (
            <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.15)', borderRadius: '10px', color: '#fca5a5' }}>
              ⚠️ {error}
            </div>
          ) : data ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.4rem' }}>
              {/* Quick Metrics */}
              <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
                <span className="badge badge-purple">
                  📖 {data.metrics?.total_pages || 1} Page(s)
                </span>
                <span className="badge badge-pink">
                  🧩 {data.metrics?.total_elements || 0} Elements
                </span>
                <span className="badge badge-cyan">
                  ⏱️ ~{data.metrics?.estimated_reading_time_minutes || 1} min read
                </span>
              </div>

              {/* Executive Overview Box */}
              <div
                className="glass-panel"
                style={{
                  padding: '1.2rem',
                  background: 'rgba(124, 58, 237, 0.08)',
                  border: '1px solid rgba(124, 58, 237, 0.3)',
                  borderRadius: '12px'
                }}
              >
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: 'var(--accent-pink)', fontWeight: 600 }}>
                  Overview & Scope
                </h4>
                <p style={{ margin: 0, fontSize: '0.92rem', lineHeight: 1.6, color: 'var(--text-main)' }}>
                  {data.executive_summary}
                </p>
              </div>

              {/* Key Takeaways */}
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.6rem', color: 'var(--text-muted)' }}>
                  Key Extracted Highlights
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {(data.key_takeaways || []).map((t, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '0.8rem 1rem',
                        borderRadius: '8px',
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid rgba(255, 255, 255, 0.06)',
                        fontSize: '0.88rem',
                        lineHeight: 1.5,
                        color: 'var(--text-muted)'
                      }}
                    >
                      • {t}
                    </div>
                  ))}
                </div>
              </div>

              {/* Topics */}
              {data.key_topics && data.key_topics.length > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.92rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-dim)' }}>
                    Extracted Core Topics
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {data.key_topics.map((top, idx) => (
                      <span key={idx} className="badge badge-cyan" style={{ fontSize: '0.78rem' }}>
                        #{top}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '1rem 1.8rem',
            borderTop: '1px solid var(--border-glass)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'rgba(0, 0, 0, 0.2)'
          }}
        >
          <button
            onClick={handleCopy}
            className="btn-secondary"
            style={{ padding: '0.45rem 1rem', fontSize: '0.85rem' }}
            disabled={!data}
          >
            {copied ? '✓ Copied Brief' : '📋 Copy Summary'}
          </button>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.45rem 1.2rem', fontSize: '0.85rem' }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveSummaryModal;
