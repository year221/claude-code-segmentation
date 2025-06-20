import axios from 'axios';
import type { SegmentationResult } from '../types';

const API_BASE_URL = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadImage = async (file: File): Promise<SegmentationResult> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const segmentFromUrl = async (imageUrl: string): Promise<SegmentationResult> => {
  const response = await api.post(`/segment-url?image_url=${encodeURIComponent(imageUrl)}`);
  
  return response.data;
};