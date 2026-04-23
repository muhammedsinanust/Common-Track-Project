import { useState, useEffect, useRef } from 'react';
import { getDrops, enterRaffle } from '../api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const SHOE_SIZES = ['7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12', '13'];

function CountdownTimer({ targetDate, onExpired }) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });
  const [expired, setExpired] = useState(false);

  useEffect(() => {
    const target = new Date(targetDate).getTime();

    const tick = () => {
      const now = Date.now();
      const diff = target - now;

      if (diff <= 0) {
        setExpired(true);
        onExpired?.();
        return;
      }

      setTimeLeft({
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((diff / (1000 * 60)) % 60),
        seconds: Math.floor((diff / 1000) % 60),
      });
    };

    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [targetDate, onExpired]);

  if (expired) {
    return (
      <div className="flex items-center gap-2 text-accent-lime font-bold text-lg animate-pulse">
        <span className="w-3 h-3 rounded-full bg-accent-lime animate-ping" />
        DROP IS LIVE!
      </div>
    );
  }

  const units = [
    { label: 'DAYS', value: timeLeft.days },
    { label: 'HRS', value: timeLeft.hours },
    { label: 'MIN', value: timeLeft.minutes },
    { label: 'SEC', value: timeLeft.seconds },
  ];

  return (
    <div className="flex gap-3">
      {units.map((unit) => (
        <div key={unit.label} className="flex flex-col items-center">
          <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl glass flex items-center justify-center
                          border border-brand-500/10 shadow-glow">
            <span className="font-display text-2xl sm:text-3xl font-black text-surface-50">
              {String(unit.value).padStart(2, '0')}
            </span>
          </div>
          <span className="text-[10px] font-semibold text-surface-200/30 mt-1.5 tracking-widest">
            {unit.label}
          </span>
        </div>
      ))}
    </div>
  );
}

function DropCard({ drop }) {
  const { isAuthenticated, token } = useAuth();
  const [dropLive, setDropLive] = useState(false);
  const [selectedSize, setSelectedSize] = useState('');
  const [status, setStatus] = useState('idle'); // idle | submitting | success | error
  const [message, setMessage] = useState('');

  // Check if drop is already past
  useEffect(() => {
    if (new Date(drop.drop_date).getTime() <= Date.now()) {
      setDropLive(true);
    }
  }, [drop.drop_date]);

  const product = drop.product;

  const handleEnterRaffle = async () => {
    if (!selectedSize) {
      setMessage('Please select a shoe size');
      setStatus('error');
      return;
    }

    setStatus('submitting');
    setMessage('');

    try {
      const res = await enterRaffle(token, selectedSize);
      setStatus('success');
      setMessage(res.data.message || 'You\'re in the raffle! 🎉');
    } catch (err) {
      setStatus('error');
      setMessage(err.response?.data?.detail || 'Failed to enter raffle. Try again.');
    }
  };

  return (
    <div className="card !p-0 overflow-hidden animate-slide-up">
      {/* Top: LIVE badge */}
      <div className="relative px-6 pt-6 pb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-lg">🔥</span>
            <span className="font-display font-bold text-sm text-surface-50 uppercase tracking-wider">
              Fresh Drop
            </span>
          </div>
          {dropLive ? (
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent-lime/10 border border-accent-lime/20 text-accent-lime text-xs font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-lime animate-ping" />
              LIVE
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full glass-light text-surface-200/50 text-xs font-medium">
              UPCOMING
            </span>
          )}
        </div>
      </div>

      {/* Sneaker display */}
      <div className="relative h-64 bg-gradient-to-br from-surface-900 to-surface-950 flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-brand-500/5 to-transparent" />
        {product?.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="object-contain h-full w-full p-8 animate-float"
          />
        ) : (
          <span className="text-8xl animate-float select-none">👟</span>
        )}
        {/* Price badge */}
        {product?.price && (
          <div className="absolute bottom-4 right-4 px-4 py-2 rounded-xl glass text-lg font-black gradient-text">
            ${product.price.toFixed(2)}
          </div>
        )}
      </div>

      {/* Info section */}
      <div className="px-6 py-5 space-y-5">
        {/* Product name & brand */}
        <div>
          {product?.brand && (
            <span className="text-xs font-semibold text-brand-400 uppercase tracking-wider">
              {product.brand}
            </span>
          )}
          <h2 className="font-display text-2xl font-bold text-surface-50 mt-0.5">
            {product?.name || 'Mystery Sneaker'}
          </h2>
          {product?.description && (
            <p className="text-surface-200/40 text-sm mt-1">{product.description}</p>
          )}
        </div>

        {/* Countdown */}
        <div>
          <p className="text-xs font-semibold text-surface-200/30 uppercase tracking-wider mb-3">
            {dropLive ? 'Raffle is open' : 'Drops in'}
          </p>
          <CountdownTimer
            targetDate={drop.drop_date}
            onExpired={() => setDropLive(true)}
          />
        </div>

        {/* Raffle entry section */}
        {dropLive && (
          <div className="space-y-4 pt-2 border-t border-white/5 animate-fade-in">
            {!isAuthenticated ? (
              <div className="text-center py-4">
                <p className="text-surface-200/40 text-sm mb-3">Sign in to enter the raffle</p>
                <Link to="/login" className="btn-primary inline-block">
                  Sign In to Enter
                </Link>
              </div>
            ) : (
              <>
                {/* Size selector */}
                <div>
                  <p className="text-xs font-semibold text-surface-200/30 uppercase tracking-wider mb-2">
                    Select Your Size
                  </p>
                  <div className="grid grid-cols-6 gap-2">
                    {SHOE_SIZES.map((size) => (
                      <button
                        key={size}
                        onClick={() => { setSelectedSize(size); setStatus('idle'); setMessage(''); }}
                        className={`py-2 rounded-lg text-sm font-medium transition-all duration-200
                          ${selectedSize === size
                            ? 'bg-brand-500 text-white shadow-glow scale-105'
                            : 'glass-light text-surface-200/60 hover:text-surface-50 hover:bg-surface-700/50'
                          }`}
                      >
                        {size}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Enter button */}
                <button
                  onClick={handleEnterRaffle}
                  disabled={status === 'submitting' || status === 'success'}
                  className={`w-full py-4 rounded-2xl font-bold text-base tracking-wide transition-all duration-300
                    ${status === 'success'
                      ? 'bg-accent-lime/20 text-accent-lime border border-accent-lime/30 cursor-default'
                      : 'bg-gradient-to-r from-brand-500 via-accent-violet to-brand-600 hover:shadow-glow-lg active:scale-[0.98] shadow-glow disabled:opacity-50'
                    }`}
                >
                  {status === 'submitting' ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
                      </svg>
                      Entering Raffle…
                    </span>
                  ) : status === 'success' ? (
                    '✅ You\'re In!'
                  ) : (
                    '🎟️  Enter Raffle'
                  )}
                </button>

                {/* Status message */}
                {message && (
                  <p className={`text-sm text-center animate-fade-in ${
                    status === 'success' ? 'text-accent-lime' : 'text-accent-coral'
                  }`}>
                    {message}
                  </p>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function FreshDrop() {
  const [drops, setDrops] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDrops()
      .then((res) => setDrops(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen pt-24 pb-16 px-4 animated-bg">
      {/* Background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-brand-500/5 rounded-full blur-3xl" />
        <div className="absolute top-40 right-10 w-96 h-96 bg-accent-violet/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-accent-lime/3 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-slide-up">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-xs font-medium text-accent-coral mb-4">
            <span className="w-2 h-2 rounded-full bg-accent-coral animate-pulse" />
            LIMITED RELEASE
          </div>
          <h1 className="font-display text-5xl sm:text-6xl font-black tracking-tight mb-4">
            <span className="text-surface-50">Fresh </span>
            <span className="gradient-text">Drops</span>
          </h1>
          <p className="text-surface-200/50 text-lg max-w-xl mx-auto">
            Exclusive limited-edition releases. Enter the raffle when the countdown hits zero.
          </p>
        </div>

        {/* Drops list */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3 text-surface-200/50">
              <svg className="animate-spin h-5 w-5 text-brand-500" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
              </svg>
              Loading drops…
            </div>
          </div>
        ) : drops.length === 0 ? (
          <div className="text-center py-20 animate-fade-in">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl glass mb-6">
              <span className="text-4xl">🔥</span>
            </div>
            <h2 className="font-display text-xl font-bold text-surface-50 mb-2">No Drops Scheduled</h2>
            <p className="text-surface-200/40 max-w-md mx-auto">
              Fresh drops haven't been scheduled yet. Use the Product Service API to create products and schedule drops.
            </p>
            <div className="mt-6 p-4 rounded-xl glass text-left max-w-lg mx-auto">
              <p className="text-xs font-semibold text-surface-200/30 uppercase tracking-wider mb-2">Quick Start</p>
              <code className="text-xs text-brand-400 block leading-relaxed">
                1. POST /api/products/products → create a sneaker<br />
                2. POST /api/products/drops → schedule a drop with drop_date
              </code>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            {drops.map((drop, i) => (
              <DropCard key={drop._id || i} drop={drop} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
