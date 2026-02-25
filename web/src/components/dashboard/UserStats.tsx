import React from 'react';
import type { User, UserBadge } from '@/types/user';
import type { Task } from '@/types/task';
import { Trophy, Target, Flame, CheckCircle, Star, Award, Zap, BookOpen, Crown } from 'lucide-react';

interface UserStatsProps {
  user: User | null;
  tasks: Task[];
  badges?: UserBadge[];
}

export const UserStats: React.FC<UserStatsProps> = ({ user, tasks, badges = [] }) => {
  const completedTasks = tasks.filter(task => task.is_completed).length;
  const pendingTasks = tasks.filter(task => !task.is_completed).length;
  const completionRate = tasks.length > 0 ? (completedTasks / tasks.length) * 100 : 0;

  const stats = [
    {
      name: 'Pontos',
      value: user?.total_points || 0,
      icon: Trophy,
      color: 'text-yellow-600 bg-yellow-50 dark:text-yellow-400 dark:bg-yellow-900/30',
    },
    {
      name: 'Streak',
      value: `${user?.current_streak || 0} dias`,
      icon: Flame,
      color: 'text-orange-600 bg-orange-50 dark:text-orange-400 dark:bg-orange-900/30',
    },
    {
      name: 'Concluídas',
      value: completedTasks,
      icon: CheckCircle,
      color: 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/30',
    },
    {
      name: 'Pendentes',
      value: pendingTasks,
      icon: Target,
      color: 'text-primary-600 bg-primary-50 dark:text-primary-400 dark:bg-primary-900/30',
    },
  ];

  // Helper function to map string names to Lucide icons
  const getBadgeIcon = (iconName: string) => {
    switch (iconName.toLowerCase()) {
      case 'star': return Star;
      case 'award': return Award;
      case 'flame': return Flame;
      case 'target': return Target;
      case 'book-open': return BookOpen;
      case 'crown': return Crown;
      case 'zap': return Zap;
      case 'trophy': return Trophy;
      default: return Award; // fallback
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-colors">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Suas Estatísticas
        </h3>

        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat) => (
            <div key={stat.name} className="text-center">
              <div className={`mx-auto w-12 h-12 rounded-lg flex items-center justify-center ${stat.color} mb-2 transition-colors`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stat.value}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {stat.name}
              </div>
            </div>
          ))}
        </div>
      </div>

      {badges.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-colors">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Award className="w-5 h-5 mr-2 text-indigo-500 dark:text-indigo-400" />
            Suas Conquistas
          </h3>
          <div className="grid grid-cols-3 gap-3">
            {badges.map((userBadge) => {
              const IconComponent = getBadgeIcon(userBadge.badge.icon);
              return (
                <div
                  key={userBadge.badge.id}
                  className="flex flex-col items-center p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg text-center border border-indigo-100 dark:border-indigo-800/50 transition-transform hover:scale-105"
                  title={`${userBadge.badge.name}\n${userBadge.badge.description}`}
                >
                  <IconComponent className="w-8 h-8 text-indigo-600 dark:text-indigo-400 mb-2" />
                  <span className="text-xs font-semibold text-indigo-900 dark:text-indigo-200 leading-tight">
                    {userBadge.badge.name}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-colors">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Taxa de Conclusão
        </h3>

        <div className="mb-2">
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Progresso</span>
            <span>{completionRate.toFixed(1)}%</span>
          </div>
        </div>

        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className="bg-primary-600 dark:bg-primary-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${completionRate}%` }}
          />
        </div>

        <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
          {completedTasks} de {tasks.length} tarefas concluídas
        </div>
      </div>
    </div>
  );
};