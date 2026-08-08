import { apiRequest } from './api';

export const reportService = {
  async requestReport(projectId) {
    return await apiRequest(`/projects/${projectId}/reports`, {
      method: 'POST',
    });
  },

  async getReportStatus(jobId) {
    return await apiRequest(`/reports/${jobId}`);
  },
};
