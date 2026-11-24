import { createContext, useState, useEffect, useContext } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token and fetch user on initial load
  useEffect(() => {
    const token = localStorage.getItem('hiremind_token');
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error("Failed to authenticate user", error);
      localStorage.removeItem('hiremind_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    localStorage.setItem('hiremind_token', response.data.access_token);
    await fetchUser();
  };

  const register = async (userData) => {
    await api.post('/auth/register', userData);
    // Auto-login after successful registration
    await login(userData.email, userData.password);
  };

  const logout = () => {
    localStorage.removeItem('hiremind_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, fetchUser }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
