import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import UploadSection from '../components/UploadSection';
import AnalysisSection from '../components/AnalysisSection';
import MatrixBackground from '../components/MatrixBackground';
import { documentService } from '../services/historyService';

const DashboardPage = () => {
  const [activeDocument, setActiveDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadLatestDocument();
  }, []);

  const loadLatestDocument = async () => {
    setLoading(true);
    try {
      const data = await documentService.getDocuments();
      if (data.documents && data.documents.length > 0) {
        setActiveDocument(data.documents[0]);
      }
    } catch (e) {
      console.error('Failed to load documents', e);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (uploadResult) => {
    // When upload finishes, reload or set active document
    documentService.getDocumentDetails(uploadResult.document_id)
      .then((doc) => setActiveDocument(doc))
      .catch(() => loadLatestDocument());
  };

  return (
    <div>
      <Navbar />
      <MatrixBackground opacity={0.16} color="purple" />
      <div className="animated-grid" />
      <div className="orb orb-primary" />
      <div className="orb orb-secondary" />

      <main className="main-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
          <div>
            <span className="badge badge-purple" style={{ marginBottom: '0.6rem' }}>Dashboard Overview</span>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
              Document <span className="gradient-text">Intelligence Hub</span>
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginTop: '0.3rem' }}>
              Real-time structural element extraction, chunk distribution, and neural query interface
            </p>
          </div>

          <button
            onClick={() => navigate('/chat')}
            className="btn-primary"
            style={{ padding: '0.8rem 1.6rem' }}
          >
            💬 Open AI Q&A Chat →
          </button>
        </div>

        {/* Upload Zone */}
        <UploadSection onUploadSuccess={handleUploadSuccess} />

        {/* Active Document Analysis */}
        <div style={{ marginTop: '2.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
            <div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
                {activeDocument ? `Active Document: ${activeDocument.filename}` : 'Active Document Analysis'}
              </h2>
              {activeDocument && (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Format: {activeDocument.file_type} • Size: {Math.round((activeDocument.file_size || 0) / 1024)} KB • Status: {activeDocument.status}
                </p>
              )}
            </div>

            <button
              onClick={() => navigate('/history')}
              className="btn-secondary"
              style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
            >
              View Document Archive ↗
            </button>
          </div>

          <AnalysisSection documentData={activeDocument} />
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;

