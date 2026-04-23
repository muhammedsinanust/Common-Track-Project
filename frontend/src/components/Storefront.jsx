import { useState, useEffect } from 'react';
import { getProducts } from '../api';
import { Link } from 'react-router-dom';

export default function Storefront() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProducts()
      .then((res) => setProducts(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen pt-24 pb-16 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16 animate-slide-up">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-xs font-medium text-brand-400 mb-4">
            <span className="w-2 h-2 rounded-full bg-accent-lime animate-pulse" />
            NOW LIVE
          </div>
          <h1 className="font-display text-5xl sm:text-6xl font-black tracking-tight mb-4">
            <span className="text-surface-50">The Freshest </span>
            <span className="gradient-text">Kicks</span>
          </h1>
          <p className="text-surface-200/50 text-lg max-w-2xl mx-auto">
            Explore our curated collection of exclusive sneakers. Limited drops, unlimited style.
          </p>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3 text-surface-200/50">
              <svg className="animate-spin h-5 w-5 text-brand-500" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" />
              </svg>
              Loading inventory…
            </div>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-20 animate-fade-in">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl glass mb-6">
              <span className="text-4xl">👟</span>
            </div>
            <h2 className="font-display text-xl font-bold text-surface-50 mb-2">No Products Yet</h2>
            <p className="text-surface-200/40 mb-6">
              The store is being stocked. Check back soon or hit the Fresh Drops page!
            </p>
            <Link to="/drops" className="btn-primary inline-flex items-center gap-2">
              🔥 View Fresh Drops
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product, i) => (
              <div
                key={product._id || i}
                className="card group animate-slide-up"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                {/* Image area */}
                <div className="relative h-52 rounded-xl bg-surface-900/50 mb-4 overflow-hidden flex items-center justify-center">
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="object-contain h-full w-full p-4 group-hover:scale-110 transition-transform duration-500"
                    />
                  ) : (
                    <span className="text-6xl group-hover:animate-float">👟</span>
                  )}
                  {/* Brand badge */}
                  <div className="absolute top-3 left-3 px-2.5 py-1 rounded-lg glass-light text-xs font-semibold text-brand-400 uppercase tracking-wider">
                    {product.brand}
                  </div>
                </div>

                {/* Details */}
                <h3 className="font-display font-bold text-lg text-surface-50 mb-1 group-hover:text-brand-400 transition-colors">
                  {product.name}
                </h3>
                <p className="text-surface-200/40 text-sm mb-3 line-clamp-2">
                  {product.description || 'Premium limited edition sneaker.'}
                </p>

                {/* Footer */}
                <div className="flex items-center justify-between">
                  <span className="text-xl font-black gradient-text">
                    ${product.price?.toFixed(2)}
                  </span>
                  <div className="flex gap-1">
                    {(product.sizes || []).slice(0, 4).map((s) => (
                      <span key={s.size} className="px-2 py-0.5 rounded-md bg-surface-900/50 text-xs text-surface-200/60">
                        {s.size}
                      </span>
                    ))}
                    {(product.sizes || []).length > 4 && (
                      <span className="px-2 py-0.5 rounded-md bg-surface-900/50 text-xs text-surface-200/40">
                        +{product.sizes.length - 4}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
