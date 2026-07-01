import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: BASE,
  headers: { 'x-api-key': 'sk-vansh-abc123' },
});

export const checkHealth = () =>
  client.get('/health').then((r) => r.data);

export const fetchStats = () =>
  client.get('/stats').then((r) => r.data);

export default client;
