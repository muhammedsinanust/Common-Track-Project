import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser, getProfile } from '../api';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { data } = await loginUser(form);
      const token = data.access_token;

      // Fetch user profile
      const profileRes = await getProfile(token);
      login(token, profileRes.data);

      navigate('/drops');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 animated-bg">
      {/* Background orbs */}
      <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-accent-violet/10 rounded-full blur-3xl animate-pulse-slow" />
      <div className="absolute bottom-1/3 left-1/3 w-80 h-80 bg-brand-500/10 rounded-full blur-3xl animate-pulse-slow" />

      <div className="relative w-full max-w-md animate-slide-up">
        <div className="glass rounded-3xl p-8 shadow-glow-lg">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl
                            bg-gradient-to-br from-accent-violet to-brand-500 mb-4 shadow-glow">
              <span className="text-2xl">🔐</span>
            </div>
            <h1 className="font-display text-2xl font-bold text-surface-50">Welcome Back</h1>
            <p className="text-surface-200/60 text-sm mt-1">Sign in to enter the next drop</p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-accent-coral/10 border border-accent-coral/20 text-accent-coral text-sm text-center animate-fade-in">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="login-username" className="block text-xs font-medium text-surface-200/50 mb-1.5 uppercase tracking-wider">
                Username
              </label>
              <input
                id="login-username"
                type="text"
                name="username"
                value={form.username}
                onChange={handleChange}
                required
                placeholder="sneakerhead42"
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="login-password" className="block text-xs font-medium text-surface-200/50 mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                required
                placeholder="••••••••"
                className="input-field"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
                  </svg>
                  Signing in…
                </span>
              ) : 'Sign In'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-surface-200/40">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
