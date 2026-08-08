import { apiRequest } from './api';

export const projectService = {
  async getAllProjects() {
    const res = await apiRequest('/projects');
    if (res.success && res.data) {
      return {
        ...res,
        data: Array.isArray(res.data) ? res.data : (res.data.items || []),
      };
    }
    return res;
  },

  async getProjectById(projectId) {
    return await apiRequest(`/projects/${projectId}`);
  },

  async createProject(projectData) {
    return await apiRequest('/projects', {
      method: 'POST',
      body: projectData,
    });
  },

  async updateProject(projectId, projectData) {
    return await apiRequest(`/projects/${projectId}`, {
      method: 'PUT',
      body: projectData,
    });
  },

  async deleteProject(projectId) {
    return await apiRequest(`/projects/${projectId}`, {
      method: 'DELETE',
    });
  },
};
