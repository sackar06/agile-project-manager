import { apiRequest } from './api';

export const storyService = {
  async getStoriesByProject(projectId) {
    const res = await apiRequest(`/projects/${projectId}/stories`);
    if (res.success && res.data) {
      return {
        ...res,
        data: Array.isArray(res.data) ? res.data : (res.data.items || []),
      };
    }
    return res;
  },

  async createStory(projectId, storyData) {
    return await apiRequest(`/projects/${projectId}/stories`, {
      method: 'POST',
      body: {
        ...storyData,
        project_id: parseInt(projectId, 10),
      },
    });
  },

  async updateStory(storyId, storyData) {
    return await apiRequest(`/stories/${storyId}`, {
      method: 'PUT',
      body: storyData,
    });
  },

  async deleteStory(storyId) {
    return await apiRequest(`/stories/${storyId}`, {
      method: 'DELETE',
    });
  },
};
