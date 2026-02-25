import React, { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { TaskList } from './TaskList';
import { CreateTaskModal } from './CreateTaskModal';
import { EditTaskModal } from './EditTaskModal';
import { UserStats } from './UserStats';
import { SubjectsManager } from './SubjectsManager';
import { DeleteConfirmationModal } from '@/components/dashboard/DeleteConfirmationModal';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import type { Task } from '@/types/task';
import type { User, UserBadge } from '@/types/user';
import { taskService } from '@/services/taskService';
import { userService } from '@/services/userService';
import { Plus, LogOut } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [userStats, setUserStats] = useState<User | null>(null);
  const [userBadges, setUserBadges] = useState<UserBadge[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const [taskToDeleteId, setTaskToDeleteId] = useState<number | null>(null);
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);

  const loadData = async () => {
    try {
      // O userService agora puxa de /users/dashboard, 
      // então tasks também já vêm dali. Mas mantemos chamada separada
      // para facilitar se necessário. Vamos pegar os dados do dashboard.
      const dashboardData = await userService.getUserData();

      const formattedTasks = dashboardData.tasks.map((task: any) => ({
        ...task,
        completed: task.is_completed
      }));

      setTasks(formattedTasks);
      setUserStats(dashboardData.user);
      setUserBadges(dashboardData.badges);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTaskComplete = async (taskId: number) => {
    try {
      await taskService.completeTask(taskId);
      await loadData();
    } catch (error) {
      console.error('Erro ao completar tarefa:', error);
    }
  };

  const handleTaskCreated = () => {
    loadData();
    setIsCreateModalOpen(false);
  };

  const handleDeleteTaskRequest = (taskId: number) => {
    setTaskToDeleteId(taskId);
  };

  const handleTaskDelete = async (taskId: number) => {
    try {
      await taskService.deleteTask(taskId);
      await loadData();
      setTaskToDeleteId(null);
    } catch (error) {
      console.error('Erro ao excluir tarefa:', error);
      setTaskToDeleteId(null);
    }
  };

  const handleTaskEdit = (task: Task) => {
    setTaskToEdit(task);
  };

  const handleTaskUpdated = () => {
    loadData();
    setTaskToEdit(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors">
        <div className="text-lg text-gray-700 dark:text-gray-300">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">StudyStreak</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">Olá, {user?.email}!</p>
            </div>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-md text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 dark:shadow-neon dark:hover:shadow-neon-hover transition-all duration-300"
              >
                <Plus className="w-4 h-4 mr-2" />
                Nova Tarefa
              </button>
              <button
                onClick={logout}
                className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition duration-150"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1 space-y-6">
            {userStats && <UserStats user={userStats} tasks={tasks} badges={userBadges} />}
            <SubjectsManager onSubjectsChange={loadData} />
          </div>

          <div className="lg:col-span-3">
            <TaskList
              tasks={tasks}
              onTaskComplete={handleTaskComplete}
              onTaskDelete={handleDeleteTaskRequest}
              onTaskEdit={handleTaskEdit}
            />
          </div>
        </div>
      </main>

      {isCreateModalOpen && (
        <CreateTaskModal
          onClose={() => setIsCreateModalOpen(false)}
          onTaskCreated={handleTaskCreated}
        />
      )}

      {taskToEdit !== null && (
        <EditTaskModal
          task={taskToEdit}
          onClose={() => setTaskToEdit(null)}
          onTaskUpdated={handleTaskUpdated}
        />
      )}

      {taskToDeleteId !== null && (
        <DeleteConfirmationModal
          taskId={taskToDeleteId}
          onConfirm={handleTaskDelete}
          onClose={() => setTaskToDeleteId(null)}
        />
      )}
    </div>
  );
};