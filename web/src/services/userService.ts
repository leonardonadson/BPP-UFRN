import { api } from './api';
import type { UserDashboard } from '@/types/user';

export const userService = {
  getUserData: async (): Promise<UserDashboard> => {
    const response = await api.get('/users/dashboard');
    return response.data;
  }
};