import axios from 'axios';

/**
 * API client configured via environment variables.
 *
 * In production (Docker), these are set at build time or via nginx proxy.
 * In development, they default to localhost.
 */

const AUTH_URL    = import.meta.env.VITE_AUTH_URL    || 'http://localhost:8001';
const PRODUCT_URL = import.meta.env.VITE_PRODUCT_URL || 'http://localhost:8002';
const RAFFLE_URL  = import.meta.env.VITE_RAFFLE_URL  || 'http://localhost:8003';

// ── Auth Service ────────────────────────────────────────────────────────────

export const authAPI = axios.create({ baseURL: AUTH_URL });

export const registerUser = (data) =>
  authAPI.post('/api/auth/register', data);

export const loginUser = (data) =>
  authAPI.post('/api/auth/login', data);

export const getProfile = (token) =>
  authAPI.get('/api/auth/profile', {
    headers: { Authorization: `Bearer ${token}` },
  });

// ── Product Service ─────────────────────────────────────────────────────────

export const productAPI = axios.create({ baseURL: PRODUCT_URL });

export const getProducts = () =>
  productAPI.get('/api/products/products');

export const getDrops = () =>
  productAPI.get('/api/products/drops');

// ── Raffle Service ──────────────────────────────────────────────────────────

export const raffleAPI = axios.create({ baseURL: RAFFLE_URL });

export const enterRaffle = (token, shoeSize) =>
  raffleAPI.post(
    '/api/raffle/enter-raffle',
    { shoe_size: shoeSize },
    { headers: { Authorization: `Bearer ${token}` } }
  );
