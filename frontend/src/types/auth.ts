export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string; // JWT or session token
  refreshToken?: string;
  user: User;
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'unauthenticated';
