import axios from 'axios';

/**
 * API client.
 *
 * In Docker-compose mode, nginx reverse-proxies /api/* to the correct service,
 * so base URLs are empty (same origin). For standalone/native mode you can
 * override via VITE_*_URL env vars at build time.
 */

const AUTH_URL    = import.meta.env.VITE_AUTH_URL    || '';
const PRODUCT_URL = import.meta.env.VITE_PRODUCT_URL || '';
const RAFFLE_URL  = import.meta.env.VITE_RAFFLE_URL  || '';

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
