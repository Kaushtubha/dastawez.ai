import React from 'react';
import Navbar from '../components/Navbar';
import ChatSection from '../components/ChatSection';
import MatrixBackground from '../components/MatrixBackground';

const ChatPage = () => {
  return (
    <div>
      <Navbar />
      <MatrixBackground opacity={0.16} color="purple" />
      <div className="animated-grid" />
      <div className="orb orb-primary" />
      <div className="orb orb-secondary" />

      <main className="main-content">
        <div style={{ marginBottom: '1.8rem' }}>
          <span className="badge badge-purple" style={{ marginBottom: '0.6rem' }}>Conversational Intelligence</span>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
            Contextual <span className="gradient-text">Document Assistant</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem', marginTop: '0.3rem' }}>
            Ask direct questions against your contracts, books, or technical manuals with guaranteed citations
          </p>
        </div>

        <ChatSection />
      </main>
    </div>
  );
};

export default ChatPage;

