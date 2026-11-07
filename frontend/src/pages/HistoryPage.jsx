import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import MatrixBackground from '../components/MatrixBackground';
import DocumentModal from '../components/DocumentModal';
import ConfirmModal from '../components/ConfirmModal';
import { documentService } from '../services/historyService';

const HighlightText = ({ text, highlight }) => {
  if (!highlight || !highlight.trim()) return <span>{text}</span>;
  const regex = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const parts = text.split(regex);
  return (
    <span>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark
            key={i}
            style={{
              background: 'rgba(240, 147, 251, 0.35)',
              color: '#fff',
              padding: '0 2px',
              borderRadius: '3px',
              textShadow: '0 0 8px rgba(240, 147, 251, 0.8)'
            }}
          >
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </span>
  );
};

const HistoryPage = () => {
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState('');
  const [formatFilter, setFormatFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('date-desc');
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState({ isOpen: false, id: null, filename: '' });
  const navigate = useNavigate();

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentService.getDocuments();
      setDocuments(data.documents || []);
    } catch (e) {
      console.error('Error fetching documents', e);
    } finally {
      setLoading(false);
    }
  };

  const getNormalizedType = (doc) => {
    const t = (doc.file_type || '').toLowerCase();
    const name = (doc.filename || '').toLowerCase();
    if (t.includes('pdf') || name.endsWith('.pdf')) return 'PDF';
    if (t.includes('docx') || t.includes('word') || name.endsWith('.docx') || name.endsWith('.doc')) return 'DOCX';
    if (t.includes('md') || name.endsWith('.md') || name.endsWith('.markdown')) return 'MD';
    if (t.includes('txt') || t.includes('text') || name.endsWith('.txt')) return 'TXT';
    return 'OTHER';
  };

  const handleDeletePrompt = (id, filename) => {
    setConfirmDelete({
      isOpen: true,
      id,
      filename
    });
  };

  const handleExecuteDelete = async () => {
    const { id } = confirmDelete;
    if (!id) return;
    try {
      await documentService.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (selectedDoc && selectedDoc.id === id) {
        setSelectedDoc(null);
      }
    } catch (err) {
      alert('Failed to delete document: ' + (err.response?.data?.detail || err.message));
    } finally {
      setConfirmDelete({ isOpen: false, id: null, filename: '' });
    }
  };

  const filteredDocs = documents
    .filter((d) => {
      const matchesSearch = d.filename.toLowerCase().includes(search.toLowerCase());
      if (!matchesSearch) return false;
      if (formatFilter === 'ALL') return true;
      return getNormalizedType(d) === formatFilter;
    })
    .sort((a, b) => {
      if (sortBy === 'date-desc') {
        return new Date(b.upload_date || 0) - new Date(a.upload_date || 0);
      }
      if (sortBy === 'date-asc') {
        return new Date(a.upload_date || 0) - new Date(b.upload_date || 0);
      }
      if (sortBy === 'name-asc') {
        return a.filename.localeCompare(b.filename);
      }
      if (sortBy === 'size-desc') {
        return (b.file_size || 0) - (a.file_size || 0);
      }
      if (sortBy === 'elements-desc') {
        const elA = a.metadata?.analysis?.total_elements || 0;
        const elB = b.metadata?.analysis?.total_elements || 0;
        return elB - elA;
      }
      return 0;
    });

  const filterCounts = {
    ALL: documents.length,
    PDF: documents.filter((d) => getNormalizedType(d) === 'PDF').length,
    DOCX: documents.filter((d) => getNormalizedType(d) === 'DOCX').length,
    TXT: documents.filter((d) => getNormalizedType(d) === 'TXT').length,
    MD: documents.filter((d) => getNormalizedType(d) === 'MD').length
  };

  return (
    <div>
      <Navbar />
      <MatrixBackground opacity={0.16} color="pink" />
      <div className="animated-grid" />
      <div className="orb orb-secondary" />

      <main className="main-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
          <div>
            <span className="badge badge-pink" style={{ marginBottom: '0.6rem' }}>Document Archive</span>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
              Ingested <span className="gradient-text">Document History</span>
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginTop: '0.3rem' }}>
              Manage, search, and review all parsed documents and chunk partitions
            </p>
          </div>

          <button onClick={() => navigate('/dashboard')} className="btn-primary" style={{ padding: '0.75rem 1.4rem' }}>
            + Upload New Document
          </button>
        </div>

        {/* Search, Filter Pills & Sort Controls */}
        <div className="glass-panel" style={{ padding: '1.2rem', marginBottom: '1.8rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ fontSize: '1.2rem' }}>🔍</span>
            <input
              type="text"
              className="input-glass"
              placeholder="Search documents by filename or keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ border: 'none', background: 'transparent', padding: '0.4rem 0.5rem', flex: 1 }}
            />
            <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
              {filteredDocs.length} of {documents.length} records
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '0.8rem', flexWrap: 'wrap', gap: '0.8rem' }}>
            {/* Format Pills */}
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginRight: '0.2rem' }}>Format:</span>
              {['ALL', 'PDF', 'DOCX', 'TXT', 'MD'].map((fmt) => (
                <button
                  key={fmt}
                  onClick={() => setFormatFilter(fmt)}
                  style={{
                    padding: '0.3rem 0.75rem',
                    borderRadius: '8px',
                    fontSize: '0.8rem',
                    fontWeight: formatFilter === fmt ? 600 : 400,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    background: formatFilter === fmt ? 'var(--primary-glow)' : 'rgba(255, 255, 255, 0.04)',
                    color: formatFilter === fmt ? '#fff' : 'var(--text-muted)',
                    border: formatFilter === fmt ? '1px solid var(--primary-color)' : '1px solid var(--border-glass)'
                  }}
                >
                  {fmt} ({filterCounts[fmt] || 0})
                </button>
              ))}
            </div>

            {/* Sorting Dropdown */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>Sort By:</span>
              <select
                className="input-glass"
                style={{ padding: '0.35rem 0.8rem', fontSize: '0.82rem', width: 'auto' }}
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="date-desc">Upload Date (Newest)</option>
                <option value="date-asc">Upload Date (Oldest)</option>
                <option value="name-asc">Document Name (A-Z)</option>
                <option value="size-desc">File Size (Largest)</option>
                <option value="elements-desc">Elements Count (Most)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Document Table */}
        <div className="glass-panel" style={{ overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.92rem' }}>
              <thead>
                <tr style={{ background: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--border-glass)' }}>
                  <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: 600 }}># ID</th>
                  <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: 600 }}>Document Name</th>
                  <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: 600 }}>Type</th>
                  <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: 600 }}>Size</th>
                  <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: 600 }}>Elements</th>
                  <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: 600 }}>Uploaded</th>
                  <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                      {loading ? 'Loading document records...' : 'No documents matching your search criteria.'}
                    </td>
                  </tr>
                ) : (
                  filteredDocs.map((doc) => {
                    const elementsCount = doc.metadata?.analysis?.total_elements || 0;
                    const pagesCount = doc.metadata?.analysis?.total_pages || 1;
                    return (
                      <tr
                        key={doc.id}
                        style={{
                          borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                          transition: 'background 0.2s ease'
                        }}
                      >
                        <td style={{ padding: '1rem 1.5rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                          #{doc.id}
                        </td>
                        <td
                          style={{
                            padding: '1rem 1.5rem',
                            fontWeight: 600,
                            cursor: 'pointer',
                            color: 'var(--text-main)'
                          }}
                          onClick={() => setSelectedDoc(doc)}
                          title="Click to inspect metadata and chunks"
                        >
                          <span style={{ textDecoration: 'underline', textDecorationColor: 'rgba(255, 255, 255, 0.2)' }}>
                            <HighlightText text={doc.filename} highlight={search} />
                          </span>
                        </td>
                        <td style={{ padding: '1rem 1.5rem' }}>
                          <span className="badge badge-purple">{doc.file_type}</span>
                        </td>
                        <td style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)' }}>
                          {Math.round((doc.file_size || 0) / 1024)} KB
                        </td>
                        <td style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)' }}>
                          {elementsCount} in {pagesCount} pgs
                        </td>
                        <td style={{ padding: '1rem 1.5rem', color: 'var(--text-dim)', fontSize: '0.82rem' }}>
                          {doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : 'Recent'}
                        </td>
                        <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                          <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                            <button
                              onClick={() => setSelectedDoc(doc)}
                              className="btn-secondary"
                              style={{ padding: '0.35rem 0.8rem', fontSize: '0.8rem' }}
                              title="Inspect Extracted Chunks"
                            >
                              👁️ Inspect
                            </button>
                            <button
                              onClick={() => navigate('/chat')}
                              className="btn-secondary"
                              style={{ padding: '0.35rem 0.8rem', fontSize: '0.8rem' }}
                            >
                              💬 Query
                            </button>
                            <button
                              onClick={() => handleDeletePrompt(doc.id, doc.filename)}
                              className="btn-secondary"
                              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', color: '#f87171' }}
                              title="Delete Document"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Document Chunk Inspector Modal */}
        {selectedDoc && (
          <DocumentModal doc={selectedDoc} onClose={() => setSelectedDoc(null)} />
        )}

        {/* Delete Confirmation Modal */}
        <ConfirmModal
          isOpen={confirmDelete.isOpen}
          title="Delete Ingested Document"
          message={`Are you sure you want to permanently delete "${confirmDelete.filename}"? This will purge all extracted chunks and layout metadata from the vector index.`}
          confirmText="Delete Document"
          confirmVariant="danger"
          onConfirm={handleExecuteDelete}
          onCancel={() => setConfirmDelete({ isOpen: false, id: null, filename: '' })}
        />
      </main>
    </div>
  );
};

export default HistoryPage;
