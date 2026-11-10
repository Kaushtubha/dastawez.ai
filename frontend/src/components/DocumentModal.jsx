import React, { useState } from 'react';

const DocumentModal = ({ doc, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [copiedChunkIdx, setCopiedChunkIdx] = useState(null);

  if (!doc) return null;

  const metadata = doc.metadata || {};
  const analysis = metadata.analysis || {};
  const chunks = metadata.chunks || [];
  const typeCounts = analysis.type_counts || {};

  const handleCopyChunk = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedChunkIdx(idx);
    setTimeout(() => setCopiedChunkIdx(null), 2000);
  };

  const handleExportFormat = (fmt) => {
    const url = `/api/v1/documents/${doc.id}/export/${fmt}`;
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${(doc.filename || 'document').replace(/\.[^/.]+$/, "")}_${fmt}.${fmt === 'csv' ? 'csv' : 'md'}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'rgba(5, 5, 12, 0.75)',
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
          maxWidth: '850px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(18, 15, 38, 0.95)',
          border: '1px solid var(--border-glass-glow)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
          borderRadius: '16px',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
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
            <span style={{ fontSize: '1.5rem' }}>📄</span>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
                {doc.filename}
              </h2>
              <div style={{ display: 'flex', gap: '0.6rem', marginTop: '0.2rem', alignItems: 'center' }}>
                <span className="badge badge-purple" style={{ fontSize: '0.75rem' }}>
                  #{doc.id}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                  {doc.file_type || 'Unknown Type'} • {Math.round((doc.file_size || 0) / 1024)} KB
                </span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <button
              onClick={() => handleExportFormat('markdown')}
              className="btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
              title="Download reconstructed Markdown document"
            >
              <span>📝</span>
              <span>Export MD</span>
            </button>
            <button
              onClick={() => handleExportFormat('csv')}
              className="btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
              title="Download extracted chunks as CSV dataset"
            >
              <span>📊</span>
              <span>Export CSV</span>
            </button>
            <button
              onClick={onClose}
              className="btn-secondary"
              style={{ padding: '0.4rem 0.8rem', fontSize: '1.1rem', lineHeight: 1 }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div
          style={{
            display: 'flex',
            padding: '0.5rem 1.8rem',
            gap: '1rem',
            borderBottom: '1px solid var(--border-glass)',
            background: 'rgba(0, 0, 0, 0.2)'
          }}
        >
          <button
            onClick={() => setActiveTab('overview')}
            style={{
              background: 'none',
              border: 'none',
              color: activeTab === 'overview' ? 'var(--primary-color)' : 'var(--text-dim)',
              fontWeight: activeTab === 'overview' ? 600 : 400,
              padding: '0.6rem 0.2rem',
              borderBottom: activeTab === 'overview' ? '2px solid var(--primary-color)' : '2px solid transparent',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            📊 Analysis Overview
          </button>
          <button
            onClick={() => setActiveTab('chunks')}
            style={{
              background: 'none',
              border: 'none',
              color: activeTab === 'chunks' ? 'var(--primary-color)' : 'var(--text-dim)',
              fontWeight: activeTab === 'chunks' ? 600 : 400,
              padding: '0.6rem 0.2rem',
              borderBottom: activeTab === 'chunks' ? '2px solid var(--primary-color)' : '2px solid transparent',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            🧩 Extracted Chunks ({chunks.length})
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '1.8rem', overflowY: 'auto', flex: 1 }}>
          {activeTab === 'overview' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Metrics Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '1rem'
                }}
              >
                <div className="glass-panel" style={{ padding: '1rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Total Elements</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
                    {analysis.total_elements || 0}
                  </div>
                </div>
                <div className="glass-panel" style={{ padding: '1rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Page Count</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--accent-cyan)', marginTop: '0.2rem' }}>
                    {analysis.total_pages || 1}
                  </div>
                </div>
                <div className="glass-panel" style={{ padding: '1rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Avg Length / Element</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--accent-pink)', marginTop: '0.2rem' }}>
                    {Math.round(analysis.avg_element_length || 0)} <span style={{ fontSize: '0.85rem' }}>chars</span>
                  </div>
                </div>
                <div className="glass-panel" style={{ padding: '1rem', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Ingestion Timestamp</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-muted)', marginTop: '0.6rem' }}>
                    {doc.upload_date ? new Date(doc.upload_date).toLocaleString() : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Element Type Distribution */}
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.8rem', color: 'var(--text-muted)' }}>
                  Element Classification Distribution
                </h4>
                {Object.keys(typeCounts).length === 0 ? (
                  <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>No element breakdown available.</p>
                ) : (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
                    {Object.entries(typeCounts).map(([type, count]) => (
                      <div
                        key={type}
                        className="glass-panel"
                        style={{
                          padding: '0.6rem 1rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.6rem',
                          fontSize: '0.85rem'
                        }}
                      >
                        <span style={{ fontWeight: 600 }}>{type}</span>
                        <span className="badge badge-purple" style={{ fontSize: '0.75rem' }}>
                          {count}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'chunks' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {chunks.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
                  No individual chunks stored in metadata preview.
                </div>
              ) : (
                chunks.map((chunk, idx) => (
                  <div
                    key={idx}
                    className="glass-panel"
                    style={{
                      padding: '1rem',
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid rgba(255, 255, 255, 0.06)'
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '0.5rem',
                        fontSize: '0.8rem'
                      }}
                    >
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span className="badge badge-pink" style={{ fontSize: '0.72rem' }}>
                          Chunk #{idx + 1}
                        </span>
                        <span style={{ color: 'var(--text-dim)' }}>
                          Type: <strong>{chunk.type || chunk.element_type || 'Text'}</strong>
                        </span>
                        {chunk.page_number && (
                          <span style={{ color: 'var(--text-dim)' }}>
                            Page {chunk.page_number}
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => handleCopyChunk(chunk.text || chunk.content || '', idx)}
                        className="btn-secondary"
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                      >
                        {copiedChunkIdx === idx ? '✓ Copied' : '📋 Copy'}
                      </button>
                    </div>

                    <p
                      style={{
                        margin: 0,
                        fontSize: '0.88rem',
                        lineHeight: 1.5,
                        color: 'var(--text-main)',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        maxHeight: '140px',
                        overflowY: 'auto'
                      }}
                    >
                      {chunk.text || chunk.content || 'Empty chunk payload'}
                    </p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div
          style={{
            padding: '1rem 1.8rem',
            borderTop: '1px solid var(--border-glass)',
            display: 'flex',
            justifyContent: 'flex-end',
            background: 'rgba(0, 0, 0, 0.2)'
          }}
        >
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.5rem 1.2rem' }}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentModal;
