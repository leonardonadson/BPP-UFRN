export interface Task {
  id: number;
  title: string;
  description?: string;
  subject: string;
  weight: number;
  due_date: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskFilters {
  skip?: number;
  limit?: number;
  subject?: string;
  completed?: boolean;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  subject: string;
  weight: number;
  due_date: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  subject?: string;
  weight?: number;
  due_date?: string;
}

export interface CompleteTaskResponse {
  task: Task;
  points_earned: number;
  streak_updated: boolean;
  badges_earned: Badge[];
}

export interface Badge {
  id: number;
  name: string;
  description: string;
  icon: string;
  earned_at: string;
}
