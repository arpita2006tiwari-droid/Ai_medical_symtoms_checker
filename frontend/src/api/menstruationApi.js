import api from './axios';

export const menstruationApi = {
  getPreferences: async () => {
    const response = await api.get('/api/menstruation/preferences');
    return response.data;
  },

  updatePreferences: async (data) => {
    const response = await api.put('/api/menstruation/preferences', data);
    return response.data;
  },

  createCycle: async (data) => {
    const response = await api.post('/api/menstruation/cycles', data);
    return response.data;
  },

  updateCycle: async (id, data) => {
    const response = await api.put(`/api/menstruation/cycles/${id}`, data);
    return response.data;
  },

  getCycles: async () => {
    const response = await api.get('/api/menstruation/cycles');
    return response.data;
  },

  deleteCycle: async (id) => {
    const response = await api.delete(`/api/menstruation/cycles/${id}`);
    return response.data;
  },

  deleteAllCycles: async () => {
    const response = await api.delete('/api/menstruation/cycles');
    return response.data;
  }
};
