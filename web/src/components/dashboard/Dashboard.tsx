import React, { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { TaskList } from './TaskList';
import { CreateTaskModal } from './CreateTaskModal';
import { UserStats } from './UserStats';
import { DeleteConfirmationModal } from '@/components/dashboard/DeleteConfirmationModal';
import type { Task } from '@/types/task';
import type { User } from '@/types/user'; 
import { taskService } from '@/services/taskService';
import { userService } from '@/services/userService';
import { Plus, LogOut } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [userStats, setUserStats] = useState<User | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  const [taskToDeleteId, setTaskToDeleteId] = useState<number | null>(null); 

  const loadData = async () => {
    try {
      const [tasksData, userData] = await Promise.all([
        taskService.getTasks(),
        userService.getUserData()
      ]);
      
      const formattedTasks = tasksData.map((task: any) => ({
        ...task,
        completed: task.is_completed
      }));
      
      setTasks(formattedTasks);
      setUserStats(userData);
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

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg text-gray-700">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">StudyStreak</h1>
              <p className="text-sm text-gray-600">Olá, {user?.email}!</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition duration-150"
              >
                <Plus className="w-4 h-4 mr-2" />
                Nova Tarefa
              </button>
              <button
                onClick={logout}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition duration-150"
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
          <div className="lg:col-span-1">
            {userStats && <UserStats user={userStats} tasks={tasks} />}
          </div>
          
          <div className="lg:col-span-3">
            <TaskList 
              tasks={tasks} 
              onTaskComplete={handleTaskComplete}
              onTaskDelete={handleDeleteTaskRequest}
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