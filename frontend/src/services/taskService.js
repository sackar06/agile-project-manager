import { apiRequest } from './api';

export const taskService = {
  async getTasksByStory(storyId) {
    const res = await apiRequest(`/stories/${storyId}/tasks`);
    if (res.success && res.data) {
      return {
        ...res,
        data: Array.isArray(res.data) ? res.data : (res.data.items || []),
      };
    }
    return res;
  },

  async createTask(storyId, taskData) {
    return await apiRequest(`/stories/${storyId}/tasks`, {
      method: 'POST',
      body: {
        ...taskData,
        user_story_id: parseInt(storyId, 10),
      },
    });
  },

  async updateTask(taskId, taskData) {
    return await apiRequest(`/tasks/${taskId}`, {
      method: 'PUT',
      body: taskData,
    });
  },

  async deleteTask(taskId) {
    return await apiRequest(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  },
};
