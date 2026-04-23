import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (email, username, password) =>
    api.post('/auth/register', { email, username, password }),
  
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  
  getProfile: () =>
    api.get('/auth/profile'),
};

// Product API
export const productAPI = {
  getProducts: (skip = 0, limit = 100) =>
    api.get('/products', { params: { skip, limit } }),
  
  getProduct: (productId) =>
    api.get(`/products/${productId}`),
  
  createProduct: (productData) =>
    api.post('/products', productData),
  
  updateProduct: (productId, productData) =>
    api.put(`/products/${productId}`, productData),
  
  deleteProduct: (productId) =>
    api.delete(`/products/${productId}`),
};

// Raffle API
export const raffleAPI = {
  enterRaffle: (shoeSize) =>
    api.post('/raffle/enter-raffle', { shoe_size: shoeSize }),
  
  getRaffleStats: () =>
    api.get('/raffle/raffle-stats'),
};

export default api;
