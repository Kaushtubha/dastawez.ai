import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor to inject JWT Bearer Token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('dastawez_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for centralized error normalizing & auth cleanup
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear expired credentials
      localStorage.removeItem('dastawez_token');
      localStorage.removeItem('dastawez_user');
    }

    if (error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'))) {
      error.normalizedMessage = 'The request timed out after 30s. Please verify your connection or server status.';
    } else if (!error.response) {
      error.normalizedMessage = 'Network connection unavailable. Please check your internet connection.';
    } else {
      error.normalizedMessage = error.response.data?.detail || error.response.data?.message || error.message || 'An unexpected error occurred.';
    }

    return Promise.reject(error);
  }
);

export default api;

