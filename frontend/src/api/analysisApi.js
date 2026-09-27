import api from './axios';

export const analysisApi = {
  extractSymptoms: async (text) => {
    const response = await api.post('/api/extract-symptoms', { text });
    return response.data;
  },

  predict: async (symptoms, demographics = {}) => {
    const response = await api.post('/api/predict', { symptoms, ...demographics });
    return response.data;
  },

  analyzeText: async (text, demographics = {}) => {
    const response = await api.post('/api/analyze', { text, ...demographics });
    return response.data;
  },

  getModelMetadata: async () => {
    const response = await api.get('/api/model-metadata');
    return response.data;
  }
};
