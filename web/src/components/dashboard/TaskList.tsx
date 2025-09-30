import React, { useState } from 'react';
import type { Task } from '@/types/task';
import { format, isAfter, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { CheckCircle, Circle, Clock, Trash2, BookOpen } from 'lucide-react';
import clsx from 'clsx';

interface TaskListProps {
  tasks: Task[];
  onTaskComplete: (taskId: number) => Promise<void>;
  onTaskDelete: (taskId: number) => void;
}

export const TaskList: React.FC<TaskListProps> = ({ 
  tasks, 
  onTaskComplete, 
  onTaskDelete 
}) => {
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');

  const filteredTasks = tasks.filter(task => {
    if (filter === 'pending') return !task.is_completed;
    if (filter === 'completed') return task.is_completed;
    return true;
  });

  const sortedTasks = filteredTasks.sort((a, b) => {
    if (a.is_completed !== b.is_completed) {
      return a.is_completed ? 1 : -1;
    }
    return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
  });

  const handleDelete = (taskId: number) => {
    onTaskDelete(taskId); 
  };

  const isOverdue = (dueDate: string) => {
    return isAfter(new Date(), parseISO(dueDate));
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Minhas Tarefas</h2>
          <div className="flex space-x-2">
            {(['all', 'pending', 'completed'] as const).map((filterOption) => (
              <button
                key={filterOption}
                onClick={() => setFilter(filterOption)}
                className={clsx(
                  'px-3 py-1 rounded-md text-sm font-medium transition-colors duration-150',
                  filter === filterOption
                    ? 'bg-blue-100 text-blue-700 font-bold'
                    : 'text-gray-500 hover:bg-gray-100'
                )}
              >
                {filterOption === 'all' && 'Todas'}
                {filterOption === 'pending' && 'Pendentes'}
                {filterOption === 'completed' && 'Concluídas'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {sortedTasks.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p>Nenhuma tarefa encontrada</p>
          </div>
        ) : (
          sortedTasks.map((task) => (
            <div
              key={task.id}
              className={clsx(
                'p-6 hover:bg-gray-50 transition-colors',
                task.is_completed && 'opacity-60'
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <button
                    onClick={() => !task.is_completed && onTaskComplete(task.id)}
                    disabled={task.is_completed}
                    className={clsx(
                      'mt-1 flex-shrink-0',
                      task.is_completed 
                        ? 'text-green-500' 
                        : 'text-gray-400 hover:text-green-500'
                    )}
                  >
                    {task.is_completed ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Circle className="w-5 h-5" />
                    )}
                  </button>

                  <div className="flex-1 min-w-0">
                    <h3 className={clsx(
                      'text-base font-medium',
                      task.is_completed ? 'line-through text-gray-500' : 'text-gray-900'
                    )}>
                      {task.title}
                    </h3>
                    
                    {task.description && (
                      <p className="mt-1 text-sm text-gray-600">
                        {task.description}
                      </p>
                    )}

                    <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                      <span className="inline-flex items-center px-2 py-1 rounded-full bg-gray-100 text-xs font-medium">
                        {task.subject}
                      </span>
                      
                      <span className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        <span className={clsx(
                          !task.is_completed && isOverdue(task.due_date) && 'text-red-600 font-semibold'
                        )}>
                          {format(parseISO(task.due_date), 'dd/MM/yyyy HH:mm', { locale: ptBR })}
                        </span>
                      </span>

                      <span className="font-medium">
                        Peso: {task.weight}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(task.id)}
                  className="ml-4 p-1 text-gray-400 hover:text-red-500 transition-colors rounded-full hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
