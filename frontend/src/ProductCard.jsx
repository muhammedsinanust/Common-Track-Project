import React, { useState } from 'react';
import { raffleAPI } from './api';
import CountdownTimer from './CountdownTimer';

const ProductCard = ({ product, isAuthenticated, userRole }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedSize, setSelectedSize] = useState('');
  const [dropLive, setDropLive] = useState(false);

  const handleEnterRaffle = async () => {
    if (!selectedSize) {
      setError('Please select a shoe size');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await raffleAPI.enterRaffle(selectedSize);
      setSuccess(`✓ Raffle entry submitted! Entry ID: ${response.data.entry_id}`);
      setSelectedSize('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to enter raffle');
    } finally {
      setLoading(false);
    }
  };

  const sizes = ['6', '7', '8', '9', '10', '11', '12', '13', '14', '15'];
  const isDropScheduled = product.drop_timestamp && !dropLive;
  const isDropLive = dropLive || !isDropScheduled;

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="mb-4 bg-gray-200 h-48 rounded flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Image: {product.name}</p>
        </div>
      </div>

      <h3 className="text-xl font-bold mb-2">{product.brand} {product.name}</h3>
      <p className="text-gray-600 mb-2">Size: {product.size}</p>
      {product.description && (
        <p className="text-sm text-gray-700 mb-3">{product.description}</p>
      )}

      <p className="text-2xl font-bold text-black mb-4">${product.price}</p>

      {isDropScheduled && (
        <div className="mb-4 p-3 bg-blue-50 rounded">
          <p className="text-sm text-gray-600 mb-2">Drop in:</p>
          <CountdownTimer
            targetDate={product.drop_timestamp}
            onComplete={() => setDropLive(true)}
          />
        </div>
      )}

      {isAuthenticated ? (
        <>
          <div className="mb-3">
            <label className="block text-sm font-semibold mb-2">Select Size</label>
            <select
              value={selectedSize}
              onChange={(e) => setSelectedSize(e.target.value)}
              className="input-field"
            >
              <option value="">Choose a size...</option>
              {sizes.map((size) => (
                <option key={size} value={size}>
                  Size {size}
                </option>
              ))}
            </select>
          </div>

          {error && <div className="text-red-600 text-sm mb-2">{error}</div>}
          {success && <div className="text-green-600 text-sm mb-2">{success}</div>}

          <button
            onClick={handleEnterRaffle}
            disabled={loading || !isDropLive}
            className="btn-primary w-full"
          >
            {loading ? 'Submitting...' : 'Enter Raffle'}
          </button>

          <div className="mt-2 text-sm text-gray-600">
            Stock: {product.stock} available
          </div>
        </>
      ) : (
        <p className="text-center text-gray-600 text-sm">
          Please log in to enter the raffle
        </p>
      )}
    </div>
  );
};

export default ProductCard;
