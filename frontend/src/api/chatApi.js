import api from './axios';

export const chatApi = {
  sendMessage: async (message, conversation_id = null) => {
    const payload = { message };
    if (conversation_id) {
      payload.conversation_id = conversation_id;
    }
    const response = await api.post('/api/chat', payload);
    return response.data;
  }
};
