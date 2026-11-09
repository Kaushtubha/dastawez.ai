import React, { useState, useEffect, useRef } from 'react';
import { documentService } from '../services/historyService';
import { useToast } from '../context/ToastContext';

const renderInlineMarkdown = (text) => {
  const parts = [];
  const regex = /(`[^`]+`|\*\*[^*]+\*\*)/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code
          key={match.index}
          style={{
            background: 'rgba(255, 255, 255, 0.1)',
            padding: '0.15rem 0.4rem',
            borderRadius: '4px',
            fontFamily: 'var(--font-mono, monospace)',
            fontSize: '0.85em',
            color: '#a78bfa'
          }}
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={match.index} style={{ fontWeight: 700, color: '#f3f4f6' }}>
          {token.slice(2, -2)}
        </strong>
      );
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }
  return parts.length > 0 ? parts : text;
};

const FormattedMessage = ({ content, role, onCopyCode }) => {
  if (role === 'user') {
    return <span>{content}</span>;
  }

  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  const segments = [];
  let lastIdx = 0;
  let match;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    if (match.index > lastIdx) {
      segments.push({ type: 'text', value: content.substring(lastIdx, match.index) });
    }
    segments.push({
      type: 'code',
      lang: match[1] || 'text',
      code: match[2].trimEnd()
    });
    lastIdx = codeBlockRegex.lastIndex;
  }
  if (lastIdx < content.length) {
    segments.push({ type: 'text', value: content.substring(lastIdx) });
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      {segments.map((seg, sIdx) => {
        if (seg.type === 'code') {
          return (
            <div
              key={sIdx}
              style={{
                borderRadius: '8px',
                background: 'rgba(10, 10, 20, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                overflow: 'hidden',
                margin: '0.4rem 0'
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.35rem 0.8rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  fontSize: '0.72rem',
                  color: 'var(--text-dim)',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
                }}
              >
                <span style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>{seg.lang}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onCopyCode) onCopyCode(seg.code);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    fontSize: '0.72rem'
                  }}
                >
                  📋 Copy Code
                </button>
              </div>
              <pre
                style={{
                  margin: 0,
                  padding: '0.8rem 1rem',
                  overflowX: 'auto',
                  fontFamily: 'var(--font-mono, monospace)',
                  fontSize: '0.84rem',
                  lineHeight: 1.5,
                  color: '#e2e8f0'
                }}
              >
                <code>{seg.code}</code>
              </pre>
            </div>
          );
        }

        const lines = seg.value.split('\n');
        return (
          <div key={sIdx} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {lines.map((line, lIdx) => {
              const trimmed = line.trim();
              if (!trimmed) {
                return <div key={lIdx} style={{ height: '0.4rem' }} />;
              }

              if (trimmed.startsWith('### ')) {
                return (
                  <h4 key={lIdx} style={{ margin: '0.4rem 0 0.2rem', fontSize: '1rem', color: '#f3f4f6' }}>
                    {renderInlineMarkdown(trimmed.replace('### ', ''))}
                  </h4>
                );
              }
              if (trimmed.startsWith('## ')) {
                return (
                  <h3 key={lIdx} style={{ margin: '0.6rem 0 0.2rem', fontSize: '1.08rem', color: '#f3f4f6' }}>
                    {renderInlineMarkdown(trimmed.replace('## ', ''))}
                  </h3>
                );
              }
              if (trimmed.startsWith('# ')) {
                return (
                  <h2 key={lIdx} style={{ margin: '0.8rem 0 0.3rem', fontSize: '1.2rem', color: '#f3f4f6' }}>
                    {renderInlineMarkdown(trimmed.replace('# ', ''))}
                  </h2>
                );
              }

              if (trimmed.startsWith('• ') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                const bulletText = trimmed.replace(/^[•\-*]\s+/, '');
                return (
                  <div key={lIdx} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', marginLeft: '0.3rem' }}>
                    <span style={{ color: 'var(--primary, #818cf8)', fontSize: '0.8rem', marginTop: '0.2rem' }}>●</span>
                    <span style={{ flex: 1 }}>{renderInlineMarkdown(bulletText)}</span>
                  </div>
                );
              }

              return (
                <div key={lIdx} style={{ lineHeight: 1.6 }}>
                  {renderInlineMarkdown(line)}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

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
  const [activeCitation, setActiveCitation] = useState(null);
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

  const handleExportChat = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(messages, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `dastawez_chat_history_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    if (showToast) {
      showToast('Exported conversation to JSON!', 'info', 2000);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'init-1',
        role: 'assistant',
        content: 'Conversation cleared. You can start a new query below.',
        confidence: 1.0,
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
    if (showToast) {
      showToast('Chat history cleared', 'info', 1500);
    }
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
    let tier = 'High Precision';

    if (pct < 60) {
      color = '#f59e0b';
      bg = 'rgba(245, 158, 11, 0.15)';
      tier = 'Moderate Match';
    } else if (pct < 80) {
      color = '#38bdf8';
      bg = 'rgba(56, 189, 248, 0.15)';
      tier = 'Strong Alignment';
    }

    return (
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.4rem',
        padding: '0.2rem 0.65rem',
        borderRadius: '999px',
        background: bg,
        color: color,
        fontSize: '0.75rem',
        fontWeight: 600
      }}>
        <span>🎯 {pct}% • {tier}</span>
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
        background: 'rgba(15, 12, 41, 0.3)',
        flexWrap: 'wrap',
        gap: '0.8rem'
      }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Intelligent Document Q&A</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Context-grounded natural language queries with verified source citations
          </p>
        </div>

        {/* Toolbar & Target Scope */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>Scope:</label>
            <select
              className="input-glass"
              style={{ padding: '0.45rem 1rem', fontSize: '0.85rem', width: 'auto', minWidth: '180px' }}
              value={selectedDocId || ''}
              onChange={(e) => setSelectedDocId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">All Documents</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', gap: '0.4rem' }}>
            <button
              onClick={handleExportChat}
              className="btn-secondary"
              style={{ padding: '0.45rem 0.8rem', fontSize: '0.8rem' }}
              title="Download conversation JSON"
            >
              📥 Export
            </button>
            <button
              onClick={handleClearChat}
              className="btn-secondary"
              style={{ padding: '0.45rem 0.8rem', fontSize: '0.8rem', color: '#f87171' }}
              title="Clear message thread"
            >
              🧹 Clear
            </button>
          </div>
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
                whiteSpace: m.role === 'user' ? 'pre-line' : 'normal',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)'
              }}
            >
              <FormattedMessage
                content={m.content}
                role={m.role}
                onCopyCode={(code) => {
                  navigator.clipboard.writeText(code);
                  if (showToast) showToast('Code snippet copied to clipboard!', 'success', 2000);
                }}
              />
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
                {m.sources?.map((s, sIdx) => {
                  const citationKey = `${m.id}-${sIdx}`;
                  const isActive = activeCitation?.id === citationKey;
                  return (
                    <span
                      key={sIdx}
                      onClick={() => setActiveCitation(isActive ? null : { id: citationKey, ...s })}
                      title="Click to view excerpt citation"
                      style={{
                        background: isActive ? 'rgba(124, 58, 237, 0.3)' : 'rgba(255, 255, 255, 0.05)',
                        border: isActive ? '1px solid var(--primary-color)' : '1px solid rgba(255, 255, 255, 0.1)',
                        padding: '0.2rem 0.55rem',
                        borderRadius: '6px',
                        fontSize: '0.72rem',
                        color: isActive ? '#fff' : '#cbd5e1',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      📄 Page {s.page_number} ({s.element_type}) {isActive ? '▲' : '▼'}
                    </span>
                  );
                })}
              </div>
            )}

            {/* Active Citation Excerpt Card Drawer */}
            {activeCitation && activeCitation.id.startsWith(`${m.id}-`) && (
              <div
                style={{
                  marginTop: '0.4rem',
                  padding: '0.8rem 1rem',
                  borderRadius: '10px',
                  background: 'rgba(20, 16, 42, 0.95)',
                  border: '1px solid var(--border-glass-glow)',
                  fontSize: '0.82rem',
                  color: 'var(--text-main)',
                  animation: 'fadeIn 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem', color: 'var(--accent-pink)', fontSize: '0.75rem', fontWeight: 600 }}>
                  <span>Verified Excerpt • Page {activeCitation.page_number} • Relevance: {Math.round((activeCitation.score || 0.8) * 100)}%</span>
                  <button
                    onClick={() => setActiveCitation(null)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', fontSize: '0.75rem' }}
                  >
                    ✕
                  </button>
                </div>
                <div style={{ fontStyle: 'italic', lineHeight: 1.5, color: 'var(--text-muted)' }}>
                  "{activeCitation.excerpt || 'Context excerpt attached to source record.'}"
                </div>
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
