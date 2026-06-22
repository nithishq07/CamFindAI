import axios from 'axios';
import type { Person, Alert } from '../types/api';

export const API_BASE_URL = 'http://localhost:8000/api';
export const WS_BASE_URL = 'ws://localhost:8000/ws';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface PaginatedResponse<T> {
  total: number;
  skip: number;
  limit: number;
  items: T[];
}

export const fetchIdentities = async (): Promise<Person[]> => {
  const response = await apiClient.get<PaginatedResponse<Person>>('/identities');
  return response.data.items;
};

export const fetchAlerts = async (): Promise<Alert[]> => {
  const response = await apiClient.get<PaginatedResponse<Alert>>('/alerts');
  return response.data.items;
};
