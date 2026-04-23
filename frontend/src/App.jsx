import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Storefront from './components/Storefront';
import FreshDrop from './components/FreshDrop';
import Register from './components/Register';
import Login from './components/Login';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-surface-950">
          <Navbar />
          <Routes>
            <Route path="/" element={<Storefront />} />
            <Route path="/drops" element={<FreshDrop />} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}
