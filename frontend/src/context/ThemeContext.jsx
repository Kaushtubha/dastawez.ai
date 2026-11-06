import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const THEMES = {
  purple: {
    id: 'purple',
    name: 'Cosmic Purple',
    icon: '🔮',
    primary: '#667eea',
    accentPink: '#f093fb',
    accentCyan: '#00f2fe'
  },
  cyan: {
    id: 'cyan',
    name: 'Cyber Cyan',
    icon: '💎',
    primary: '#06b6d4',
    accentPink: '#38bdf8',
    accentCyan: '#22d3ee'
  },
  emerald: {
    id: 'emerald',
    name: 'Matrix Emerald',
    icon: '🌿',
    primary: '#10b981',
    accentPink: '#34d399',
    accentCyan: '#6ee7b7'
  }
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('dastawez_theme') || 'purple';
  });

  useEffect(() => {
    localStorage.setItem('dastawez_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    const selected = THEMES[theme] || THEMES.purple;
    document.documentElement.style.setProperty('--primary', selected.primary);
    document.documentElement.style.setProperty('--accent-pink', selected.accentPink);
    document.documentElement.style.setProperty('--accent-cyan', selected.accentCyan);
  }, [theme]);

  const toggleTheme = () => {
    const keys = Object.keys(THEMES);
    const nextIdx = (keys.indexOf(theme) + 1) % keys.length;
    setTheme(keys[nextIdx]);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, currentThemeConfig: THEMES[theme] }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
export default ThemeContext;
