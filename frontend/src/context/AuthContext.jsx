import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('dastawez_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('dastawez_token'));
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await authService.login(email, password);
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('dastawez_token', data.access_token);
      localStorage.setItem('dastawez_user', JSON.stringify(data.user));
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid login credentials';
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password) => {
    setLoading(true);
    try {
      const data = await authService.register(username, email, password);
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('dastawez_token', data.access_token);
      localStorage.setItem('dastawez_user', JSON.stringify(data.user));
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed';
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await authService.logout();
    setToken(null);
    setUser(null);
    localStorage.removeItem('dastawez_token');
    localStorage.removeItem('dastawez_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

