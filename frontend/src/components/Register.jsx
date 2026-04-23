import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../api';

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
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
      await registerUser(form);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 animated-bg">
      {/* Background orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl animate-pulse-slow" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-violet/10 rounded-full blur-3xl animate-pulse-slow" />

      <div className="relative w-full max-w-md animate-slide-up">
        {/* Card */}
        <div className="glass rounded-3xl p-8 shadow-glow-lg">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl
                            bg-gradient-to-br from-brand-500 to-accent-lime mb-4 shadow-glow">
              <span className="text-2xl">🚀</span>
            </div>
            <h1 className="font-display text-2xl font-bold text-surface-50">Create Account</h1>
            <p className="text-surface-200/60 text-sm mt-1">Join the drop and cop exclusive kicks</p>
          </div>

          {/* Success */}
          {success && (
            <div className="mb-6 p-4 rounded-xl bg-accent-lime/10 border border-accent-lime/20 text-accent-lime text-sm text-center animate-fade-in">
              ✅ Account created! Redirecting to login…
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-accent-coral/10 border border-accent-coral/20 text-accent-coral text-sm text-center animate-fade-in">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="reg-username" className="block text-xs font-medium text-surface-200/50 mb-1.5 uppercase tracking-wider">
                Username
              </label>
              <input
                id="reg-username"
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
              <label htmlFor="reg-email" className="block text-xs font-medium text-surface-200/50 mb-1.5 uppercase tracking-wider">
                Email
              </label>
              <input
                id="reg-email"
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="you@example.com"
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="reg-password" className="block text-xs font-medium text-surface-200/50 mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <input
                id="reg-password"
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                required
                minLength={6}
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
                  Creating…
                </span>
              ) : 'Create Account'}
            </button>
          </form>

          {/* Footer link */}
          <p className="mt-6 text-center text-sm text-surface-200/40">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
