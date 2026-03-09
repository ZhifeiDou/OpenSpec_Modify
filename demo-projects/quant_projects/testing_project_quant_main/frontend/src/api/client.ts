import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5 min for long-running operations like backtest
});

// --- Data ---
export const getDataStatus = () => api.get('/data/status').then(r => r.data);
export const updateData = (categories: string[], force = false) =>
  api.post('/data/update', { categories, force }).then(r => r.data);

// --- Universe ---
export const getUniverse = (subsector?: string) =>
  api.get('/universe', { params: subsector ? { subsector } : {} }).then(r => r.data);

// --- Factors ---
export const getFactors = () => api.get('/factors').then(r => r.data);
export const computeFactors = () => api.post('/factors/compute').then(r => r.data);

// --- Signals ---
export const getSignals = () => api.get('/signals').then(r => r.data);

// --- Risk ---
export const getRisk = () => api.get('/risk').then(r => r.data);

// --- Backtest ---
export const runBacktest = (startDate: string, endDate: string, initialCapital?: number) =>
  api.post('/backtest/run', { start_date: startDate, end_date: endDate, initial_capital: initialCapital }).then(r => r.data);
export const getLatestBacktest = () => api.get('/backtest/latest').then(r => r.data);

// --- Report ---
export const getReport = () => api.get('/report').then(r => r.data);

export default api;
