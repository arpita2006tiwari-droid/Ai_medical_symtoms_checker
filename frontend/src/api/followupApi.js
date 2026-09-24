import api from './axios';

export const followupApi = {
  startFollowup: async (symptoms) => {
    const response = await api.post('/api/follow-up/start', { symptoms });
    return response.data;
  },

  answerFollowup: async (session_id, answer, answer_type) => {
    const response = await api.post('/api/follow-up/answer', {
      session_id,
      answer,
      answer_type
    });
    return response.data;
  }
};
