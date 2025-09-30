import { api } from './api';
import type { Task, CreateTaskRequest, TaskFilters, CompleteTaskResponse } from '@/types/task';

export const taskService = {
  async createTask(taskData: CreateTaskRequest): Promise<Task> {
    try {
      const { data } = await api.post<Task>('/tasks/', taskData);
      return data;
    } catch (error: any) {
      throw error; 
    }
  },

  async getTasks(filters?: TaskFilters): Promise<Task[]> {
    try {
      const { data } = await api.get<Task[]>('/tasks/', { params: filters });
      return data;
    } catch (error: any) {
      throw error;
    }
  },

  async getTask(taskId: number): Promise<Task> {
    try {
      const { data } = await api.get<Task>(`/tasks/${taskId}`);
      return data;
    } catch (error: any) {
      throw error;
    }
  },

  async completeTask(taskId: number): Promise<CompleteTaskResponse> {
    try {
      const { data } = await api.patch<CompleteTaskResponse>(`/tasks/${taskId}/complete`, {});
      return data;
    } catch (error: any) {
      throw error;
    }
  },

  async deleteTask(taskId: number): Promise<void> {
    try {
      await api.delete(`/tasks/${taskId}`);
    } catch (error: any) {
      throw error;
    }
  },

  async getSubjects(): Promise<string[]> {
    try {
      const { data } = await api.get<string[]>('/tasks/subjects/list');
      return data;
    } catch (error: any) {
      throw error;
    }
  },
};