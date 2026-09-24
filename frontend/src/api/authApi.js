import api from './axios';

export const authApi = {
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },
  
  register: async (email, password, full_name) => {
    const response = await api.post('/api/auth/register', { email, password, full_name });
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  }
};
