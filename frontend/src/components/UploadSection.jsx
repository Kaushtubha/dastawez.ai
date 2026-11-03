import React, { useState, useRef } from 'react';
import { documentService } from '../services/historyService';

const UploadSection = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      setError(`Format .${ext} is not supported. Please upload PDF, DOCX, or TXT.`);
      return;
    }

    setError('');
    setSuccessMsg('');
    setUploading(true);
    setProgress(10);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const result = await documentService.uploadDocument(formData, (p) => setProgress(p));
      setProgress(100);
      setSuccessMsg(`Document "${file.name}" analyzed successfully!`);
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Document processing failed. Please try again.');
    } finally {
      setUploading(false);
      setTimeout(() => setProgress(0), 2000);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Upload & Process Document</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
            Extract elements, spatial coordinates, and vectorize into semantic chunks
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span className="badge badge-purple">PDF</span>
          <span className="badge badge-pink">DOCX</span>
          <span className="badge badge-cyan">TXT</span>
        </div>
      </div>

      <div
        className={`dropzone ${isDragging ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />

        <div style={{ fontSize: '2.8rem', marginBottom: '0.8rem' }}>
          {uploading ? '⚙️' : '📤'}
        </div>

        {uploading ? (
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent-pink)' }}>
              Analyzing Document Structure... ({progress}%)
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.4rem' }}>
              Extracting titles, narrative text, tables, and generating vector embeddings
            </p>
            <div style={{
              width: '100%',
              maxWidth: '350px',
              height: '6px',
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '999px',
              margin: '1.2rem auto 0',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${progress}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #667eea, #f093fb)',
                borderRadius: '999px',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>
        ) : (
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>
              Drag & Drop your document here, or <span className="gradient-text" style={{ cursor: 'pointer' }}>browse files</span>
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.4rem' }}>
              Maximum file size: 50 MB • Full layout awareness & confidence scoring
            </p>
          </div>
        )}
      </div>

      {error && (
        <div style={{
          marginTop: '1rem',
          padding: '0.85rem 1.2rem',
          borderRadius: '12px',
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#fca5a5',
          fontSize: '0.9rem'
        }}>
          ⚠️ {error}
        </div>
      )}

      {successMsg && (
        <div style={{
          marginTop: '1rem',
          padding: '0.85rem 1.2rem',
          borderRadius: '12px',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#6ee7b7',
          fontSize: '0.9rem'
        }}>
          ✓ {successMsg}
        </div>
      )}
    </div>
  );
};

export default UploadSection;

