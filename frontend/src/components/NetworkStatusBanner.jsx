import React, { useState, useEffect } from 'react';
import api from '../services/api';

const NetworkStatusBanner = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isServerReachable, setIsServerReachable] = useState(true);
  const [showRestored, setShowRestored] = useState(false);
  const [isChecking, setIsChecking] = useState(false);

  const checkServerHealth = async () => {
    setIsChecking(true);
    try {
      await api.get('/health', { timeout: 4000 });
      setIsServerReachable(true);
      if (!isOnline) {
        setIsOnline(true);
        triggerRestoredNotice();
      }
    } catch {
      setIsServerReachable(false);
    } finally {
      setIsChecking(false);
    }
  };

  const triggerRestoredNotice = () => {
    setShowRestored(true);
    setTimeout(() => {
      setShowRestored(false);
    }, 3500);
  };

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      checkServerHealth();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setIsServerReachable(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial silent check
    checkServerHealth();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const isDisconnected = !isOnline || !isServerReachable;

  if (!isDisconnected && !showRestored) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 99999,
        padding: '10px 18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        fontSize: '0.88rem',
        fontWeight: 500,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
        backdropFilter: 'blur(10px)',
        transition: 'all 0.3s ease',
        background: isDisconnected
          ? 'linear-gradient(90deg, rgba(239, 68, 68, 0.92), rgba(185, 28, 28, 0.95))'
          : 'linear-gradient(90deg, rgba(16, 185, 129, 0.92), rgba(5, 150, 105, 0.95))',
        color: '#ffffff'
      }}
    >
      <span>
        {isDisconnected
          ? '⚠️ Network Disconnected: Cannot reach Dastawez.ai backend API. Features may be limited.'
          : '✅ Connection restored. All document intelligence services active.'}
      </span>
      {isDisconnected && (
        <button
          onClick={checkServerHealth}
          disabled={isChecking}
          style={{
            background: 'rgba(255, 255, 255, 0.2)',
            border: '1px solid rgba(255, 255, 255, 0.4)',
            color: '#ffffff',
            padding: '4px 12px',
            borderRadius: '6px',
            cursor: isChecking ? 'wait' : 'pointer',
            fontSize: '0.8rem',
            fontWeight: 600,
            transition: 'background 0.2s'
          }}
        >
          {isChecking ? 'Checking...' : 'Retry Connection'}
        </button>
      )}
    </div>
  );
};

export default NetworkStatusBanner;
