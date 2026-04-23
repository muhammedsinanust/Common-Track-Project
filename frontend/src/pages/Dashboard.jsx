import React, { useState, useEffect } from 'react';
import { productAPI } from '../api';

const Dashboard = ({ userRole }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    brand: '',
    size: '',
    price: '',
    stock: '',
    drop_timestamp: '',
    description: '',
  });

  useEffect(() => {
    if (userRole === 'admin') {
      fetchProducts();
    }
  }, [userRole]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await productAPI.getProducts();
      setProducts(response.data.products);
    } catch (err) {
      setError('Failed to fetch products');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    setError('');

    try {
      await productAPI.createProduct({
        ...formData,
        price: parseFloat(formData.price),
        stock: parseInt(formData.stock),
      });

      setFormData({
        name: '',
        brand: '',
        size: '',
        price: '',
        stock: '',
        drop_timestamp: '',
        description: '',
      });

      fetchProducts();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create product');
    }
  };

  if (userRole !== 'admin') {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card text-center">
          <h2 className="text-2xl font-bold text-red-600">Access Denied</h2>
          <p>You do not have admin privileges to access this dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Create Product Form */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Create New Sneaker Drop</h2>

          <form onSubmit={handleCreateProduct} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Product Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Brand</label>
              <input
                type="text"
                name="brand"
                value={formData.brand}
                onChange={handleInputChange}
                className="input-field"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Size</label>
                <input
                  type="text"
                  name="size"
                  value={formData.size}
                  onChange={handleInputChange}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Price</label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleInputChange}
                  step="0.01"
                  className="input-field"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Stock</label>
              <input
                type="number"
                name="stock"
                value={formData.stock}
                onChange={handleInputChange}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Drop Timestamp</label>
              <input
                type="datetime-local"
                name="drop_timestamp"
                value={formData.drop_timestamp}
                onChange={handleInputChange}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="input-field"
                rows="3"
              />
            </div>

            {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded">{error}</div>}

            <button type="submit" className="btn-primary w-full">
              Create Product
            </button>
          </form>
        </div>

        {/* Products List */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Current Products</h2>

          {loading ? (
            <p>Loading products...</p>
          ) : (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {products.length > 0 ? (
                products.map((product) => (
                  <div key={product.id} className="border-l-4 border-black pl-4 py-2">
                    <h3 className="font-bold">{product.brand} {product.name}</h3>
                    <p className="text-sm text-gray-600">Size: {product.size}</p>
                    <p className="text-sm">Price: ${product.price}</p>
                    <p className="text-sm">Stock: {product.stock}</p>
                  </div>
                ))
              ) : (
                <p className="text-gray-600">No products yet</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
