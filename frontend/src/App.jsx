import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';
import Login from './pages/Login';
import Register from './pages/Register';
import Storefront from './pages/Storefront';
import Dashboard from './pages/Dashboard';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userId, setUserId] = useState(null);
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const uid = localStorage.getItem('user_id');

    if (token && role && uid) {
      setIsAuthenticated(true);
      setUserRole(role);
      setUserId(uid);
    }
  }, []);

  const handleLogin = (uid, role) => {
    setUserId(uid);
    setUserRole(role);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
    setIsAuthenticated(false);
    setUserId(null);
    setUserRole(null);
  };

  return (
    <Router>
      <div className="min-h-screen bg-white">
        {/* Navigation */}
        <nav className="bg-black text-white shadow-lg">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <div className="text-2xl font-bold">👟 Sneaker Store</div>

            <div className="flex gap-4 items-center">
              {isAuthenticated ? (
                <>
                  <span className="text-sm text-gray-400">
                    {userRole === 'admin' ? '👑 Admin' : 'User'} • ID: {userId}
                  </span>
                  {userRole === 'admin' && (
                    <a href="/dashboard" className="hover:text-gray-300">
                      Dashboard
                    </a>
                  )}
                  <a href="/" className="hover:text-gray-300">
                    Store
                  </a>
                  <button
                    onClick={handleLogout}
                    className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <a href="/login" className="hover:text-gray-300">
                    Login
                  </a>
                  <a href="/register" className="hover:text-gray-300">
                    Register
                  </a>
                </>
              )}
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <Storefront
                isAuthenticated={isAuthenticated}
                userRole={userRole}
              />
            }
          />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <Dashboard userRole={userRole} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
        </Routes>

        {/* Footer */}
        <footer className="bg-gray-900 text-white text-center py-4 mt-12">
          <p>© 2024 Sneaker Store. Microservices powered by Docker.</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;
