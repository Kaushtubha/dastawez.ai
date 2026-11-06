import React, { useState, useRef, useEffect } from 'react';
import { documentService } from '../services/historyService';

const STAGES = [
  { id: 1, label: 'Payload Verification', desc: 'Hashing & validating MIME header' },
  { id: 2, label: 'Layout & OCR Parsing', desc: 'Extracting titles, narrative & bounding boxes' },
  { id: 3, label: 'Semantic Chunking', desc: 'Segmenting text into contextual windows' },
  { id: 4, label: 'Vector Index Sync', desc: 'Calculating embeddings & persisting to store' }
];

const UploadSection = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState(1);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!uploading) {
      setCurrentStage(1);
      return;
    }
    if (progress < 25) {
      setCurrentStage(1);
    } else if (progress < 55) {
      setCurrentStage(2);
    } else if (progress < 85) {
      setCurrentStage(3);
    } else {
      setCurrentStage(4);
    }
  }, [progress, uploading]);

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
    setProgress(15);

    // Progress tick simulator to make real backend ingestion feel alive
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev < 88) return prev + Math.floor(Math.random() * 8 + 3);
        return prev;
      });
    }, 450);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const result = await documentService.uploadDocument(formData, (p) => {
        if (p > 15) setProgress(Math.max(p, 20));
      });
      clearInterval(timer);
      setProgress(100);
      setCurrentStage(4);
      setSuccessMsg(`Document "${file.name}" ingested and vectorized successfully!`);
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      clearInterval(timer);
      setError(err.response?.data?.detail || 'Document processing failed. Please try again.');
    } finally {
      clearInterval(timer);
      setUploading(false);
      setTimeout(() => setProgress(0), 2500);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '0.8rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Upload & Process Document</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
            Multi-stage extraction with layout awareness, spatial coordinates, and vector indexing
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
        onClick={() => !uploading && fileInputRef.current?.click()}
        style={{ cursor: uploading ? 'wait' : 'pointer' }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          disabled={uploading}
        />

        <div style={{ fontSize: '2.8rem', marginBottom: '0.8rem' }}>
          {uploading ? '⚡' : '📤'}
        </div>

        {uploading ? (
          <div style={{ width: '100%', maxWidth: '640px', margin: '0 auto' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--accent-pink)' }}>
              Ingesting Document... ({Math.min(progress, 100)}%)
            </h3>

            {/* Ingestion Pipeline Stages Stepper */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '0.6rem',
                margin: '1.4rem 0 1rem',
                textAlign: 'left'
              }}
            >
              {STAGES.map((s) => {
                const isCompleted = currentStage > s.id;
                const isCurrent = currentStage === s.id;
                return (
                  <div
                    key={s.id}
                    style={{
                      padding: '0.6rem 0.8rem',
                      borderRadius: '8px',
                      background: isCurrent
                        ? 'rgba(124, 58, 237, 0.2)'
                        : isCompleted
                        ? 'rgba(16, 185, 129, 0.15)'
                        : 'rgba(255, 255, 255, 0.03)',
                      border: isCurrent
                        ? '1px solid var(--primary-color)'
                        : isCompleted
                        ? '1px solid rgba(16, 185, 129, 0.4)'
                        : '1px solid rgba(255, 255, 255, 0.06)',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', fontWeight: 600 }}>
                      <span>{isCompleted ? '✓' : isCurrent ? '⚙️' : '○'}</span>
                      <span style={{ color: isCurrent ? '#fff' : isCompleted ? '#34d399' : 'var(--text-dim)' }}>
                        {s.label}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.2rem', lineHeight: 1.2 }}>
                      {s.desc}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Animated Progress Bar */}
            <div style={{
              width: '100%',
              height: '6px',
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '999px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${Math.min(progress, 100)}%`,
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
