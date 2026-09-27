import api from './axios';

export const moodApi = {
  createCheckin: async (data) => {
    const response = await api.post('/api/mood/checkins', data);
    return response.data;
  },

  getCheckins: async () => {
    const response = await api.get('/api/mood/checkins');
    return response.data;
  },

  updateCheckin: async (id, data) => {
    const response = await api.put(`/api/mood/checkins/${id}`, data);
    return response.data;
  },

  deleteCheckin: async (id) => {
    const response = await api.delete(`/api/mood/checkins/${id}`);
    return response.data;
  }
};
