import api from './axios';

export const imageApi = {
  uploadImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/images/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getImages: async () => {
    const response = await api.get('/api/images/');
    return response.data;
  },

  deleteImage: async (id) => {
    const response = await api.delete(`/api/images/${id}`);
    return response.data;
  },

  analyzeImage: async (id) => {
    const response = await api.post(`/api/images/${id}/analyze`);
    return response.data;
  }
};
