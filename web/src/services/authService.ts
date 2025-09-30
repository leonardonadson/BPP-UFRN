import { api } from './api';
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types/auth';

const TOKEN_KEY = 'access_token';

const setAuthHeader = (token: string | null): void => {
  // @ts-ignore
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', credentials);
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setAuthHeader(data.access_token); 
    return data;
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/register', userData);
    return data;
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await api.get<User>('/users/me');
    return data;
  },

  async getDashboard() {
    const { data } = await api.get('/users/dashboard');
    return data;
  },

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    setAuthHeader(null); 
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem(TOKEN_KEY);
  },
};

const initialToken = localStorage.getItem(TOKEN_KEY);
if (initialToken) {
  setAuthHeader(initialToken);
}
