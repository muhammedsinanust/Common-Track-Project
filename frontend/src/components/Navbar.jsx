import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-brand-500 to-accent-lime flex items-center justify-center
                            group-hover:shadow-glow transition-all duration-300">
              <span className="text-lg">👟</span>
            </div>
            <span className="font-display font-bold text-lg tracking-tight">
              <span className="text-surface-50">Sneaker</span>
              <span className="gradient-text">Drop</span>
            </span>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-2">
            <Link
              to="/"
              className="px-4 py-2 rounded-lg text-sm font-medium text-surface-200 hover:text-surface-50
                         hover:bg-surface-700/50 transition-all duration-200"
            >
              Storefront
            </Link>
            <Link
              to="/drops"
              className="px-4 py-2 rounded-lg text-sm font-medium text-surface-200 hover:text-surface-50
                         hover:bg-surface-700/50 transition-all duration-200"
            >
              🔥 Fresh Drops
            </Link>

            {isAuthenticated ? (
              <div className="flex items-center gap-3 ml-2">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass-light">
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-brand-500 to-accent-violet
                                  flex items-center justify-center text-xs font-bold">
                    {user?.username?.[0]?.toUpperCase() || '?'}
                  </div>
                  <span className="text-sm font-medium text-surface-200">
                    {user?.username}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-lg text-sm font-medium text-accent-coral/80 hover:text-accent-coral
                             hover:bg-accent-coral/10 transition-all duration-200"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 ml-2">
                <Link to="/login" className="btn-secondary !py-2 !px-4 text-sm">
                  Sign In
                </Link>
                <Link to="/register" className="btn-primary !py-2 !px-4 text-sm">
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
