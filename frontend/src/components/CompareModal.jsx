import React, { useState, useEffect } from 'react';
import { documentService } from '../services/historyService';

const CompareModal = ({ isOpen, onClose, docIdA, docIdB, docAFilename, docBFilename }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && docIdA && docIdB) {
      setLoading(true);
      setError('');
      setData(null);

      documentService.compareDocuments(docIdA, docIdB)
        .then((res) => setData(res))
        .catch((err) => {
          setError(err.response?.data?.detail || 'Comparison analysis failed.');
        })
        .finally(() => setLoading(false));
    }
  }, [isOpen, docIdA, docIdB]);

  if (!isOpen) return null;

  const simPct = data?.similarity_percentage ?? 0;
  const simColor = simPct >= 80 ? '#34d399' : simPct >= 50 ? '#38bdf8' : '#f59e0b';

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10000,
        background: 'rgba(5, 5, 12, 0.82)',
        backdropFilter: 'blur(10px)',
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
          maxWidth: '820px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(16, 14, 34, 0.96)',
          border: '1px solid var(--border-glass-glow)',
          boxShadow: '0 25px 60px -15px rgba(0, 0, 0, 0.75), 0 0 35px rgba(124, 58, 237, 0.2)',
          borderRadius: '16px',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.8rem',
          borderBottom: '1px solid var(--border-glass)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(255, 255, 255, 0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.6rem' }}>⚖️</span>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
                Document Semantic Comparison
              </h2>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                TF-IDF Cosine Similarity & Structural Diff Engine
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="btn-secondary"
            style={{ padding: '0.35rem 0.75rem', fontSize: '1.1rem', lineHeight: 1 }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '1.8rem', overflowY: 'auto', flex: 1 }}>
          {loading && (
            <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem', animation: 'spin 1.5s infinite linear' }}>
                ⚡
              </div>
              <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>Computing semantic vectors and vocabulary divergence...</p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>Comparing Doc #{docIdA} vs Doc #{docIdB}</p>
            </div>
          )}

          {error && (
            <div style={{
              padding: '1.2rem',
              borderRadius: '10px',
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#fca5a5',
              fontSize: '0.9rem'
            }}>
              {error}
            </div>
          )}

          {data && !loading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Similarity Score Banner */}
              <div style={{
                padding: '1.4rem 1.8rem',
                borderRadius: '12px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.8rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                    Semantic Correlation Score
                  </span>
                  <span style={{ fontSize: '1.8rem', fontWeight: 800, color: simColor }}>
                    {simPct}%
                  </span>
                </div>

                {/* Progress bar */}
                <div style={{
                  width: '100%',
                  height: '8px',
                  borderRadius: '999px',
                  background: 'rgba(255, 255, 255, 0.08)',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${simPct}%`,
                    height: '100%',
                    borderRadius: '999px',
                    background: `linear-gradient(90deg, #6366f1, ${simColor})`,
                    transition: 'width 0.8s ease'
                  }} />
                </div>

                <p style={{ margin: '0.2rem 0 0', fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                  {data.summary}
                </p>
              </div>

              {/* Side-by-Side Comparison Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.2rem' }}>
                {/* Doc A */}
                <div style={{
                  padding: '1.2rem',
                  borderRadius: '10px',
                  background: 'rgba(99, 102, 241, 0.06)',
                  border: '1px solid rgba(99, 102, 241, 0.25)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.8rem' }}>
                    <span className="badge badge-purple" style={{ fontSize: '0.72rem' }}>Document A</span>
                    <span style={{ fontSize: '0.92rem', fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {data.document_a.filename}
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Format:</span>
                      <strong style={{ color: 'var(--text-main)' }}>{data.document_a.file_type}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>File Size:</span>
                      <strong style={{ color: 'var(--text-main)' }}>{(data.document_a.file_size / 1024).toFixed(1)} KB</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Chunks:</span>
                      <strong style={{ color: '#38bdf8' }}>{data.document_a.chunks_count} units</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Layout Elements:</span>
                      <strong style={{ color: '#a78bfa' }}>{data.document_a.elements_count} items</strong>
                    </div>
                  </div>
                </div>

                {/* Doc B */}
                <div style={{
                  padding: '1.2rem',
                  borderRadius: '10px',
                  background: 'rgba(244, 114, 182, 0.06)',
                  border: '1px solid rgba(244, 114, 182, 0.25)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.8rem' }}>
                    <span className="badge badge-pink" style={{ fontSize: '0.72rem' }}>Document B</span>
                    <span style={{ fontSize: '0.92rem', fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {data.document_b.filename}
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Format:</span>
                      <strong style={{ color: 'var(--text-main)' }}>{data.document_b.file_type}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>File Size:</span>
                      <strong style={{ color: 'var(--text-main)' }}>{(data.document_b.file_size / 1024).toFixed(1)} KB</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Chunks:</span>
                      <strong style={{ color: '#f472b6' }}>
                        {data.document_b.chunks_count} units ({data.deltas.chunks_delta >= 0 ? `+${data.deltas.chunks_delta}` : data.deltas.chunks_delta})
                      </strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>Layout Elements:</span>
                      <strong style={{ color: '#f472b6' }}>
                        {data.document_b.elements_count} items ({data.deltas.elements_delta >= 0 ? `+${data.deltas.elements_delta}` : data.deltas.elements_delta})
                      </strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Vocabulary Overlap Section */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                  🔍 Vocabulary & Key Term Divergence
                </h4>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', fontSize: '0.82rem' }}>
                  {/* Shared Keywords */}
                  <div>
                    <span style={{ color: 'var(--text-dim)', display: 'block', marginBottom: '0.3rem' }}>
                      Shared Terminology ({data.vocabulary.shared_keywords.length}):
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                      {data.vocabulary.shared_keywords.length === 0 ? (
                        <span style={{ color: 'var(--text-dim)' }}>None detected</span>
                      ) : (
                        data.vocabulary.shared_keywords.map((kw, i) => (
                          <span key={i} className="badge badge-purple" style={{ fontSize: '0.72rem' }}>
                            {kw}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Unique to Doc A */}
                  {data.vocabulary.unique_to_a.length > 0 && (
                    <div>
                      <span style={{ color: 'var(--text-dim)', display: 'block', marginBottom: '0.3rem' }}>
                        Unique to {data.document_a.filename}:
                      </span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {data.vocabulary.unique_to_a.map((kw, i) => (
                          <span key={i} className="badge badge-cyan" style={{ fontSize: '0.72rem' }}>
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Unique to Doc B */}
                  {data.vocabulary.unique_to_b.length > 0 && (
                    <div>
                      <span style={{ color: 'var(--text-dim)', display: 'block', marginBottom: '0.3rem' }}>
                        Unique to {data.document_b.filename}:
                      </span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {data.vocabulary.unique_to_b.map((kw, i) => (
                          <span key={i} className="badge badge-pink" style={{ fontSize: '0.72rem' }}>
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '0.8rem 1.8rem',
          borderTop: '1px solid var(--border-glass)',
          background: 'rgba(0, 0, 0, 0.25)',
          display: 'flex',
          justifyContent: 'flex-end'
        }}>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.5rem 1.2rem', fontSize: '0.85rem' }}>
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
};

export default CompareModal;
