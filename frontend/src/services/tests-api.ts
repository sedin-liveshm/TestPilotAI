import { Test } from '@/types/domain';
import { TestIR } from '@/types/test-ir';
import { apiClient } from './api-client';

export const testsApi = {
  getTests: (projectId: string) => {
    return apiClient.get<Test[]>(`/projects/${projectId}/tests`);
  },
  
  getTest: (id: string) => {
    return apiClient.get<Test>(`/tests/${id}`);
  },

  getTestIR: (testId: string) => {
    return apiClient.get<TestIR>(`/tests/${testId}/ir`);
  },

  updateTestIR: (testId: string, ir: Partial<TestIR>) => {
    return apiClient.put<TestIR>(`/tests/${testId}/ir`, ir);
  }
};
