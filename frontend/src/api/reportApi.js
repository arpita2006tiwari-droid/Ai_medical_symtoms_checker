import api from './axios';

export const reportApi = {
  uploadReport: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/reports/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getReports: async () => {
    const response = await api.get('/api/reports/');
    return response.data;
  },

  deleteReport: async (id) => {
    const response = await api.delete(`/api/reports/${id}`);
    return response.data;
  },

  summarizeReport: async (id) => {
    const response = await api.post(`/api/reports/${id}/summarize`);
    return response.data;
  }
};
