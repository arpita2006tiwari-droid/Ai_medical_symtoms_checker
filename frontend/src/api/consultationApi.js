import axios from 'axios';

// Get base URL dynamically or fallback to 8000
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
};

export const consultationApi = {
  createPrep: async (data) => {
    const response = await axios.post(`${API_URL}/consultations`, data, { headers: getAuthHeaders() });
    return response.data;
  },

  getPreps: async () => {
    const response = await axios.get(`${API_URL}/consultations`, { headers: getAuthHeaders() });
    return response.data;
  },

  getPrep: async (id) => {
    const response = await axios.get(`${API_URL}/consultations/${id}`, { headers: getAuthHeaders() });
    return response.data;
  },

  updatePrep: async (id, data) => {
    const response = await axios.put(`${API_URL}/consultations/${id}`, data, { headers: getAuthHeaders() });
    return response.data;
  },

  deletePrep: async (id) => {
    const response = await axios.delete(`${API_URL}/consultations/${id}`, { headers: getAuthHeaders() });
    return response.data;
  }
};
