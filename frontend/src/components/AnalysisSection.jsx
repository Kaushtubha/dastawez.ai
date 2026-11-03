import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AnalysisSection = ({ documentData }) => {
  if (!documentData) {
    return (
      <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No document selected for analysis. Please upload or choose a document from History.</p>
      </div>
    );
  }

  const analysis = documentData.metadata?.analysis || documentData.analysis || {};
  const elementTypes = analysis.element_types || {};
  const wordFreq = analysis.word_frequency || {};
  const keywords = analysis.top_keywords || [];

  const pieData = {
    labels: Object.keys(elementTypes),
    datasets: [
      {
        data: Object.values(elementTypes),
        backgroundColor: [
          'rgba(102, 126, 234, 0.85)',
          'rgba(240, 147, 251, 0.85)',
          'rgba(79, 172, 254, 0.85)',
          'rgba(0, 242, 254, 0.85)'
        ],
        borderColor: 'rgba(15, 12, 41, 0.8)',
        borderWidth: 2
      }
    ]
  };

  const barData = {
    labels: Object.keys(wordFreq).slice(0, 8),
    datasets: [
      {
        label: 'Occurrences',
        data: Object.values(wordFreq).slice(0, 8),
        backgroundColor: 'rgba(167, 139, 250, 0.8)',
        borderColor: '#a78bfa',
        borderWidth: 1,
        borderRadius: 8
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#cbd5e1',
          font: { family: 'Inter', size: 12 }
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      y: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#cbd5e1',
          font: { family: 'Inter', size: 12 },
          padding: 15
        }
      }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2rem' }}>
      {/* Metric Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        <div className="glass-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Total Elements
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginTop: '0.4rem', color: '#a78bfa' }}>
            {analysis.total_elements || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
            Titles, Tables, Lists & Text
          </div>
        </div>

        <div className="glass-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Total Pages
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginTop: '0.4rem', color: '#f472b6' }}>
            {analysis.total_pages || 1}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
            Analyzed & indexed
          </div>
        </div>

        <div className="glass-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Vector Chunks
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginTop: '0.4rem', color: '#38bdf8' }}>
            {documentData.metadata?.chunks_added || documentData.chunks_count || analysis.total_chunks || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
            RAG retrieval units
          </div>
        </div>

        <div className="glass-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Avg Text / Element
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, marginTop: '0.4rem', color: '#34d399' }}>
            {analysis.average_text_length_per_element || 0}
            <span style={{ fontSize: '1rem', fontWeight: 500, color: 'var(--text-dim)' }}> chars</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
            Density ratio
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
        gap: '1.5rem'
      }}>
        {/* Pie Chart */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>
            📊 Structural Element Distribution
          </h3>
          <div style={{ height: '260px', position: 'relative' }}>
            {Object.keys(elementTypes).length > 0 ? (
              <Pie data={pieData} options={pieOptions} />
            ) : (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', paddingTop: '5rem' }}>No element breakdown available</p>
            )}
          </div>
        </div>

        {/* Bar Chart */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>
            📈 Keyword Frequency (TF-IDF)
          </h3>
          <div style={{ height: '260px', position: 'relative' }}>
            {Object.keys(wordFreq).length > 0 ? (
              <Bar data={barData} options={chartOptions} />
            ) : (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', paddingTop: '5rem' }}>No keywords extracted</p>
            )}
          </div>
        </div>
      </div>

      {/* Top Keywords Tags */}
      {keywords.length > 0 && (
        <div className="glass-card">
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
            Salient Key Phrases & Entities
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {keywords.map((kw, i) => (
              <span
                key={i}
                style={{
                  background: 'rgba(102, 126, 234, 0.15)',
                  border: '1px solid rgba(102, 126, 234, 0.3)',
                  padding: '0.35rem 0.85rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  color: '#e2e8f0'
                }}
              >
                #{kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisSection;

