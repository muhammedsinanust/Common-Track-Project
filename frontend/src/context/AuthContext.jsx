import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('sd_token'));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('sd_user');
    return stored ? JSON.parse(stored) : null;
  });

  const login = (jwt, userData) => {
    localStorage.setItem('sd_token', jwt);
    localStorage.setItem('sd_user', JSON.stringify(userData));
    setToken(jwt);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('sd_token');
    localStorage.removeItem('sd_user');
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
