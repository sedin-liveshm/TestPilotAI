import { apiClient } from './api-client';
import { LoginRequest, LoginResponse, User } from '@/types/auth';

/**
 * Auth API wrapper.
 * Adjust the endpoint URLs to match your Supabase/FastAPI backend.
 */
export const authApi = {
  login: async (payload: LoginRequest): Promise<LoginResponse> => {
    const res = await apiClient.post<LoginResponse>('/auth/login', payload);
    return res.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post<void>('/auth/logout', {});
  },

  getCurrentUser: async (): Promise<User> => {
    const res = await apiClient.get<{ user: User }>('/auth/me');
    return res.data.user;
  },
};
