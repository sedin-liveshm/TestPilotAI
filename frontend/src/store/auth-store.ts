import { create } from 'zustand';
import { AuthStatus, LoginRequest, User } from '@/types/auth';
import { authApi } from '@/services/auth-api';

/**
 * Global authentication state store.
 *
 * - `status` tracks the lifecycle: idle → loading → authenticated / unauthenticated.
 * - `user` holds the authenticated user object when logged in.
 * - `error` stores the last authentication error message.
 *
 * The store also provides async actions for login, logout, and an initial session check.
 */
interface AuthState {
  user: User | null;
  token: string | null;
  status: AuthStatus;
  error: string | null;

  // actions
  login: (payload: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  checkSession: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null,
  status: 'idle',
  error: null,

  login: async (payload) => {
    set({ status: 'loading', error: null });
    try {
      const response = await authApi.login(payload);
      if (typeof window !== 'undefined' && response.accessToken) {
        localStorage.setItem('auth_token', response.accessToken);
      }
      set({ user: response.user, token: response.accessToken, status: 'authenticated' });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      set({ error: message, status: 'unauthenticated' });
    }
  },

  logout: async () => {
    set({ status: 'loading' });
    try {
      await authApi.logout();
    } catch {
      // ignore logout errors – we still want to clear state
    }
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
    set({ user: null, token: null, status: 'unauthenticated', error: null });
  },

  checkSession: async () => {
    set({ status: 'loading' });
    try {
      const user = await authApi.getCurrentUser();
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
      set({ user, token, status: 'authenticated' });
    } catch {
      set({ user: null, token: null, status: 'unauthenticated' });
    }
  },

  clearError: () => set({ error: null }),
}));

