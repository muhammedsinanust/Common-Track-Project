import axios from 'axios';

const AUTH_SERVICE_URL = process.env.REACT_APP_AUTH_SERVICE_URL || 'http://localhost:8001';
const PRODUCT_SERVICE_URL = process.env.REACT_APP_PRODUCT_SERVICE_URL || 'http://localhost:8002';
const RAFFLE_SERVICE_URL = process.env.REACT_APP_RAFFLE_SERVICE_URL || 'http://localhost:8003';

const createApi = (baseURL) => {
  const instance = axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  return instance;
};

export const authAPIClient = createApi(AUTH_SERVICE_URL);
export const productAPIClient = createApi(PRODUCT_SERVICE_URL);
export const raffleAPIClient = createApi(RAFFLE_SERVICE_URL);

// Auth API
export const authAPI = {
  register: (email, username, password) =>
    authAPIClient.post('/register', { email, username, password }),
  
  login: (email, password) =>
    authAPIClient.post('/login', { email, password }),
  
  getProfile: () =>
    authAPIClient.get('/profile'),
};

// Product API
export const productAPI = {
  getProducts: (skip = 0, limit = 100) =>
    productAPIClient.get('/products', { params: { skip, limit } }),
  
  getProduct: (productId) =>
    productAPIClient.get(`/products/${productId}`),
  
  createProduct: (productData) =>
    productAPIClient.post('/products', productData),
  
  updateProduct: (productId, productData) =>
    productAPIClient.put(`/products/${productId}`, productData),
  
  deleteProduct: (productId) =>
    productAPIClient.delete(`/products/${productId}`),
};

// Raffle API
export const raffleAPI = {
  enterRaffle: (shoeSize) =>
    raffleAPIClient.post('/enter-raffle', { shoe_size: shoeSize }),
  
  getRaffleStats: () =>
    raffleAPIClient.get('/raffle-stats'),
};

export default { authAPI, productAPI, raffleAPI };
