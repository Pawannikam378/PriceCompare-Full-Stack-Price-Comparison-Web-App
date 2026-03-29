/**
 * api.js
 * -------
 * Centralised Axios API service layer.
 * All backend communication goes through these functions.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Response interceptor for global error logging
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[API Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Search for a product across all marketplaces (uses real DummyJSON API).
 * @param {string} query - Product name
 * @returns {Promise<SearchResponse>}
 */
export const searchProducts = async (query) => {
  const { data } = await api.get('/search', { params: { query } });
  return data;
};

/**
 * Fetch price history for a product.
 * @param {string} product - Product name
 * @returns {Promise<HistoryResponse>}
 */
export const fetchPriceHistory = async (product) => {
  const { data } = await api.get('/history', { params: { product } });
  return data;
};

/**
 * Fetch AI price prediction for a product.
 * @param {string} product - Product name
 * @returns {Promise<PredictionResponse>}
 */
export const fetchPrediction = async (product) => {
  const { data } = await api.get('/predict', { params: { product } });
  return data;
};
