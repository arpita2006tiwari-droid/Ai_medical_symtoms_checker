import api from './axios';

export const historyApi = {
  getAnalyses: async (offset = 0, limit = 20) => {
    const response = await api.get(`/api/history?offset=${offset}&limit=${limit}`);
    return response.data;
  },

  getAnalysisById: async (id) => {
    const response = await api.get(`/api/history/${id}`);
    return response.data;
  },

  deleteAnalysis: async (id) => {
    const response = await api.delete(`/api/history/${id}`);
    return response.data;
  },

  getConversations: async (offset = 0, limit = 20) => {
    const response = await api.get(`/api/conversations?offset=${offset}&limit=${limit}`);
    return response.data;
  },

  getConversationById: async (id) => {
    const response = await api.get(`/api/conversations/${id}`);
    return response.data;
  },

  deleteConversation: async (id) => {
    const response = await api.delete(`/api/conversations/${id}`);
    return response.data;
  }
};
