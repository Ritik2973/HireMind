import axios from 'axios';

// Create a configured axios instance pointing to the FastAPI backend
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Request interceptor to automatically attach the JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('hiremind_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401 Unauthorized responses gracefully
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token is invalid or expired; clear it.
      localStorage.removeItem('hiremind_token');
    }
    return Promise.reject(error);
  }
);

export default api;
