import { ApiError, ApiErrorResponse, ApiResponse } from './api-types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Core API Client for fetching from the backend.
 * Normalizes HTTP requests and throws custom ApiError for failed statuses.
 */
async function fetchClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  // TODO: Add auth tokens here when authentication is implemented
  // const token = useAuthStore.getState().token;
  // if (token) headers.set('Authorization', `Bearer ${token}`);

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    if (response.status === 204) {
      return { data: {} as T };
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorData = data as ApiErrorResponse | null;
      throw new ApiError(
        response.status,
        errorData?.error?.message || response.statusText || 'An unexpected error occurred',
        errorData?.error?.code,
        errorData?.error?.details
      );
    }

    // Normalizing all standard responses into our ApiResponse wrapper format
    // This allows backend flexibility while maintaining a rigid frontend structure
    if (data && 'data' in data) {
      return data as ApiResponse<T>;
    }

    return { data: data as T };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Handle network errors (e.g. CORS, offline)
    throw new ApiError(0, error instanceof Error ? error.message : 'Network error');
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) => 
    fetchClient<T>(endpoint, { ...options, method: 'GET' }),
    
  post: <T>(endpoint: string, body: unknown, options?: RequestInit) =>
    fetchClient<T>(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) }),
    
  put: <T>(endpoint: string, body: unknown, options?: RequestInit) =>
    fetchClient<T>(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) }),
    
  patch: <T>(endpoint: string, body: unknown, options?: RequestInit) =>
    fetchClient<T>(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
    
  delete: <T>(endpoint: string, options?: RequestInit) =>
    fetchClient<T>(endpoint, { ...options, method: 'DELETE' }),
};
