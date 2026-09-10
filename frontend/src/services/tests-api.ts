import { Test } from '@/types/domain';
import { TestIR } from '@/types/test-ir';
import { apiClient } from './api-client';

export interface UpdateTestData {
  name?: string;
  description?: string;
  test_ir?: Partial<TestIR>;
}

export interface CreateTestData {
  name: string;
  description?: string;
  test_ir: Partial<TestIR>;
}

export const testsApi = {
  getTests: (projectId: string, params?: { page?: number; page_size?: number; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', String(params.page));
    if (params?.page_size) query.set('page_size', String(params.page_size));
    if (params?.search) query.set('search', params.search);
    const qs = query.toString();
    return apiClient.get<Test[]>(`/projects/${projectId}/tests${qs ? `?${qs}` : ''}`);
  },
  
  getTest: (id: string) => {
    return apiClient.get<Test>(`/tests/${id}`);
  },

  updateTest: (id: string, data: UpdateTestData) => {
    return apiClient.patch<Test>(`/tests/${id}`, data);
  },

  createTest: (projectId: string, data: CreateTestData) => {
    return apiClient.post<Test>(`/projects/${projectId}/tests`, data);
  },

  deleteTest: (id: string) => {
    return apiClient.delete<void>(`/tests/${id}`);
  },

  getTestIR: (testId: string) => {
    return apiClient.get<TestIR>(`/tests/${testId}/ir`);
  },

  updateTestIR: (testId: string, ir: Partial<TestIR>) => {
    return apiClient.put<TestIR>(`/tests/${testId}/ir`, ir);
  }
};

