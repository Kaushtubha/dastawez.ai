import React from 'react';

export const MetricSkeleton = () => (
  <div className="glass-card" style={{ minHeight: '110px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
    <div className="skeleton-line" style={{ width: '40%', height: '14px' }} />
    <div className="skeleton-line" style={{ width: '60%', height: '32px' }} />
    <div className="skeleton-line" style={{ width: '50%', height: '12px' }} />
  </div>
);

export const ChartSkeleton = () => (
  <div className="glass-card" style={{ height: '320px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
    <div className="skeleton-line" style={{ width: '50%', height: '20px' }} />
    <div className="skeleton-box" style={{ flex: 1, borderRadius: '12px' }} />
  </div>
);

export const TableRowSkeleton = ({ columns = 7 }) => (
  <tr>
    {Array.from({ length: columns }).map((_, i) => (
      <td key={i} style={{ padding: '1.2rem 1.5rem' }}>
        <div className="skeleton-line" style={{ width: i === 1 ? '70%' : '50%', height: '16px' }} />
      </td>
    ))}
  </tr>
);
