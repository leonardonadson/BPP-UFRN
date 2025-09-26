import { api } from './api';
import type { Task, CreateTaskRequest, TaskFilters, CompleteTaskResponse } from '@/types/task';

export const taskService = {
  async createTask(taskData: CreateTaskRequest): Promise<Task> {
    const { data } = await api.post<Task>('/tasks/', taskData);
    return data;
  },

  async getTasks(filters?: TaskFilters): Promise<Task[]> {
    const { data } = await api.get<Task[]>('/tasks/', { params: filters });
    return data;
  },

  async getTask(taskId: number): Promise<Task> {
    const { data } = await api.get<Task>(`/tasks/${taskId}`);
    return data;
  },

  async completeTask(taskId: number): Promise<CompleteTaskResponse> {
    const { data } = await api.patch<CompleteTaskResponse>(`/tasks/${taskId}/complete`);
    return data;
  },

  async deleteTask(taskId: number): Promise<void> {
    await api.delete(`/tasks/${taskId}`);
  },

  async getSubjects(): Promise<string[]> {
    const { data } = await api.get<string[]>('/tasks/subjects/list');
    return data;
  },
};
