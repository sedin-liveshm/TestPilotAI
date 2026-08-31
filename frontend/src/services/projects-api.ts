import { Project } from '@/types/domain';
import { apiClient } from './api-client';

export const projectsApi = {
  getProjects: () => {
    return apiClient.get<Project[]>('/projects');
  },
  
  getProject: (id: string) => {
    return apiClient.get<Project>(`/projects/${id}`);
  },

  createProject: (data: Partial<Project>) => {
    return apiClient.post<Project>('/projects', data);
  },

  updateProject: (id: string, data: Partial<Project>) => {
    return apiClient.patch<Project>(`/projects/${id}`, data);
  },

  deleteProject: (id: string) => {
    return apiClient.delete<void>(`/projects/${id}`);
  }
};
