import React, { useState, useEffect, useRef } from 'react';
import { documentService } from '../services/historyService';
import { useToast } from '../context/ToastContext';

const ChatSection = ({ initialDocId = null }) => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(initialDocId);
  const [messages, setMessages] = useState([
    {
      id: 'init-1',
      role: 'assistant',
      content: 'Hello! I am your Dastawez.ai document intelligence assistant. Ask me anything about your uploaded documents or choose a document above to ground my answers.',
      confidence: 1.0,
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);
  const { showToast } = useToast();

  useEffect(() => {
    documentService.getDocuments()
      .then((data) => {
        setDocuments(data.documents || []);
        if (!selectedDocId && data.documents?.length > 0) {
          setSelectedDocId(data.documents[0].id);
        }
      })
      .catch((e) => console.error('Failed to load documents for chat', e));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    if (showToast) {
      showToast('Copied answer to clipboard!', 'success', 2000);
    }
    setTimeout(() => setCopiedId(null), 2500);
  };

  const handleSend = async (queryText = inputQuery) => {
    const q = queryText.trim();
    if (!q || loading) return;

    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setInputQuery('');
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await documentService.askQuestion(q, selectedDocId);
      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        confidence: response.confidence,
        sources: response.sources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'An error occurred while analyzing the document context. Please verify that documents are uploaded.',
          confidence: 0.1,
          sources: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadge = (confidence) => {
    const pct = Math.round(confidence * 100);
    let color = '#34d399';
    let bg = 'rgba(52, 211, 153, 0.15)';
    if (pct < 60) {
      color = '#f59e0b';
      bg = 'rgba(245, 158, 11, 0.15)';
    } else if (pct < 80) {
      color = '#38bdf8';
      bg = 'rgba(56, 189, 248, 0.15)';
    }

    return (
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.4rem',
        padding: '0.2rem 0.6rem',
        borderRadius: '999px',
        background: bg,
        color: color,
        fontSize: '0.75rem',
        fontWeight: 600
      }}>
        <span>🎯 {pct}% Confidence</span>
      </div>
    );
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '680px', overflow: 'hidden' }}>
      {/* Chat Header */}
      <div style={{
        padding: '1.2rem 1.8rem',
        borderBottom: '1px solid var(--border-glass)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(15, 12, 41, 0.3)'
      }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Intelligent Document Q&A</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Context-grounded natural language queries with verified source citations
          </p>
        </div>

        {/* Target Document Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>Scope:</label>
          <select
            className="input-glass"
            style={{ padding: '0.45rem 1rem', fontSize: '0.85rem', width: 'auto', minWidth: '220px' }}
            value={selectedDocId || ''}
            onChange={(e) => setSelectedDocId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">All Documents in Archive</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.filename}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Suggested Quick Prompts */}
      <div style={{
        padding: '0.6rem 1.8rem',
        background: 'rgba(255, 255, 255, 0.02)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
        display: 'flex',
        gap: '0.6rem',
        overflowX: 'auto'
      }}>
        <button
          onClick={() => handleSend('What is this document about? Provide a summary.')}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.8rem', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
        >
          💡 Summarize Document
        </button>
        <button
          onClick={() => handleSend('What are the key elements and structural sections?')}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.8rem', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
        >
          🔍 Key Elements
        </button>
        <button
          onClick={() => handleSend('List all major topics, tables, or requirements mentioned.')}
          className="btn-secondary"
          style={{ padding: '0.35rem 0.8rem', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
        >
          📑 Topics & Tables
        </button>
      </div>

      {/* Messages Thread */}
      <div style={{ flex: 1, padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        {messages.map((m) => (
          <div
            key={m.id || m.content.substring(0, 10)}
            style={{
              alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '82%',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.4rem',
              position: 'relative'
            }}
          >
            <div
              style={{
                padding: '1rem 1.4rem',
                borderRadius: m.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                background: m.role === 'user'
                  ? 'linear-gradient(135deg, #667eea, #764ba2)'
                  : 'rgba(30, 27, 68, 0.7)',
                border: m.role === 'user' ? 'none' : '1px solid var(--border-glass)',
                color: 'white',
                lineHeight: 1.6,
                fontSize: '0.95rem',
                whiteSpace: 'pre-line',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)'
              }}
            >
              {m.content}
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: m.role === 'user' ? 'flex-end' : 'flex-between',
              gap: '0.8rem',
              fontSize: '0.75rem',
              color: 'var(--text-dim)',
              padding: '0 0.4rem'
            }}>
              <span>{m.timestamp}</span>

              {m.role === 'assistant' && (
                <button
                  onClick={() => handleCopy(m.content, m.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: copiedId === m.id ? '#34d399' : 'var(--text-muted)',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                  title="Copy response text"
                >
                  {copiedId === m.id ? '✓ Copied' : '📋 Copy'}
                </button>
              )}
            </div>

            {m.role === 'assistant' && (
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.6rem', marginTop: '0.2rem' }}>
                {getConfidenceBadge(m.confidence)}

                {/* Source citations */}
                {m.sources?.map((s, sIdx) => (
                  <span
                    key={sIdx}
                    title={s.excerpt}
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      padding: '0.2rem 0.55rem',
                      borderRadius: '6px',
                      fontSize: '0.72rem',
                      color: '#cbd5e1',
                      cursor: 'pointer'
                    }}
                  >
                    📄 Page {s.page_number} ({s.element_type})
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            <span style={{ animation: 'spin 1s infinite linear' }}>⚙️</span> Synthesizing contextual answer...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Field Area */}
      <div style={{ padding: '1.2rem', borderTop: '1px solid var(--border-glass)', background: 'rgba(15, 12, 41, 0.4)' }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          style={{ display: 'flex', gap: '0.8rem' }}
        >
          <input
            type="text"
            className="input-glass"
            placeholder="Ask a question about the document content..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !inputQuery.trim()}
            style={{ minWidth: '110px' }}
          >
            {loading ? 'Asking...' : 'Ask AI →'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatSection;
