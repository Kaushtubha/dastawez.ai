import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const useKeyboardShortcuts = (customHandlers = {}) => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't trigger navigation shortcuts if the user is typing in an input or textarea
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName);

      // Escape key always closes modals/popups
      if (e.key === 'Escape') {
        window.dispatchEvent(new CustomEvent('close-modals'));
        return;
      }

      // '?' (Shift + /) opens shortcut helper modal when not typing
      if (!isInput && e.key === '?' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('toggle-shortcuts-modal'));
        return;
      }

      // Alt/Ctrl hotkey navigation
      const modKey = e.altKey || (e.ctrlKey && !e.shiftKey);
      if (modKey) {
        const key = e.key.toLowerCase();
        if (key === 'd') {
          e.preventDefault();
          navigate('/dashboard');
        } else if (key === 'h') {
          e.preventDefault();
          navigate('/history');
        } else if (key === 'q') {
          e.preventDefault();
          navigate('/chat');
        } else if (key === 'p') {
          e.preventDefault();
          navigate('/profile');
        } else if (key === '/') {
          e.preventDefault();
          window.dispatchEvent(new CustomEvent('toggle-shortcuts-modal'));
        }
      }

      // Custom passed handlers
      if (customHandlers[e.key]) {
        customHandlers[e.key](e);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate, customHandlers]);
};

export default useKeyboardShortcuts;
