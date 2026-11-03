import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import MatrixBackground from '../components/MatrixBackground';
import { documentService } from '../services/historyService';

const HistoryPage = () => {
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
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

  const handleDelete = async (id, filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) return;
    try {
      await documentService.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      alert('Failed to delete document: ' + (err.response?.data?.detail || err.message));
    }
  };

  const filteredDocs = documents.filter((d) =>
    d.filename.toLowerCase().includes(search.toLowerCase())
  );

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

        {/* Search Bar */}
        <div className="glass-panel" style={{ padding: '1.2rem', marginBottom: '1.8rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ fontSize: '1.2rem' }}>🔍</span>
          <input
            type="text"
            className="input-glass"
            placeholder="Search documents by filename or keyword..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ border: 'none', background: 'transparent', padding: '0.4rem 0.5rem' }}
          />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
            {filteredDocs.length} of {documents.length} records
          </span>
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
                        <td style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>
                          {doc.filename}
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
                              onClick={() => navigate('/chat')}
                              className="btn-secondary"
                              style={{ padding: '0.35rem 0.8rem', fontSize: '0.8rem' }}
                            >
                              💬 Query
                            </button>
                            <button
                              onClick={() => handleDelete(doc.id, doc.filename)}
                              className="btn-secondary"
                              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', color: '#f87171' }}
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
      </main>
    </div>
  );
};

export default HistoryPage;

