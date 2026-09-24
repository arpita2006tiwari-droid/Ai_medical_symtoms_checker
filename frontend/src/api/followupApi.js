import api from './axios';

export const followupApi = {
  startFollowup: async (symptoms) => {
    const response = await api.post('/api/follow-up/start', { symptoms });
    return response.data;
  },

  answerFollowup: async (state, question_id, answer) => {
    const response = await api.post('/api/follow-up/answer', {
      state,
      question_id,
      answer
    });
    return response.data;
  }
};
