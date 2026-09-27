import api from './axios';

export const painAssessmentApi = {
  create: async (data) => {
    const response = await api.post('/api/pain-assessments', data);
    return response.data;
  },

  update: async (id, data) => {
    const response = await api.put(`/api/pain-assessments/${id}`, data);
    return response.data;
  },

  getAll: async () => {
    const response = await api.get('/api/pain-assessments');
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/api/pain-assessments/${id}`);
    return response.data;
  }
};
