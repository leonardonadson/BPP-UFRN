import { api } from './api';

export const userService = {
  getUserData: async () => {
    const response = await api.get('/users/me');
    return response.data;
  }
};