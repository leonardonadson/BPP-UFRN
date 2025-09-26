import React from 'react';
import type { User } from '@/types/auth';
import type { Task } from '@/types/task';
import { Trophy, Target, Flame, CheckCircle } from 'lucide-react';

interface UserStatsProps {
  user: User | null;
  tasks: Task[];
}

export const UserStats: React.FC<UserStatsProps> = ({ user, tasks }) => {
  const completedTasks = tasks.filter(task => task.completed).length;
  const pendingTasks = tasks.filter(task => !task.completed).length;
  const completionRate = tasks.length > 0 ? (completedTasks / tasks.length) * 100 : 0;

  const stats = [
    {
      name: 'Pontos',
      value: user?.points || 0,
      icon: Trophy,
      color: 'text-yellow-600 bg-yellow-50',
    },
    {
      name: 'Streak',
      value: `${user?.streak_days || 0} dias`,
      icon: Flame,
      color: 'text-orange-600 bg-orange-50',
    },
    {
      name: 'Concluídas',
      value: completedTasks,
      icon: CheckCircle,
      color: 'text-green-600 bg-green-50',
    },
    {
      name: 'Pendentes',
      value: pendingTasks,
      icon: Target,
      color: 'text-blue-600 bg-blue-50',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Suas Estatísticas
        </h3>
        
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat) => (
            <div key={stat.name} className="text-center">
              <div className={`mx-auto w-12 h-12 rounded-lg flex items-center justify-center ${stat.color} mb-2`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600">
                {stat.name}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Taxa de Conclusão
        </h3>
        
        <div className="mb-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progresso</span>
            <span>{completionRate.toFixed(1)}%</span>
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${completionRate}%` }}
          />
        </div>
        
        <div className="mt-4 text-center text-sm text-gray-600">
          {completedTasks} de {tasks.length} tarefas concluídas
        </div>
      </div>
    </div>
  );
};
