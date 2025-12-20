import axios from 'axios';
import type { Card, CardCreate } from '../types/card';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const cardApi = {
  // Get all cards
  getAllCards: async (): Promise<Card[]> => {
    const response = await api.get('/cards');
    return response.data;
  },

  // Get single card
  getCard: async (id: number): Promise<Card> => {
    const response = await api.get(`/cards/${id}`);
    return response.data;
  },

  // Create card manually
  createCard: async (card: CardCreate): Promise<Card> => {
    const response = await api.post('/cards', card);
    return response.data;
  },

  // Scan card image
  scanCard: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/cards/scan', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000, // 30 second timeout for Vision API processing
    });
    return response.data;
  },

  // Get card price
  getCardPrice: async (id: number) => {
    const response = await api.get(`/cards/${id}/price`);
    return response.data;
  },
};

export default api;
