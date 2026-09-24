import api from './axios';

export const analysisApi = {
  extractSymptoms: async (text) => {
    const response = await api.post('/api/extract-symptoms', { text });
    return response.data;
  },

  predict: async (symptoms) => {
    const response = await api.post('/api/predict', { symptoms });
    return response.data;
  },

  analyzeText: async (text) => {
    const response = await api.post('/api/analyze', { text });
    return response.data;
  }
};
