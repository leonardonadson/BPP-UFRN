import React, { useState } from 'react';
import type { Task } from '@/types/task';
import { format, isAfter, parseISO, addDays, isBefore, isSameDay } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { CheckCircle, Circle, Clock, Trash2, Pencil, BookOpen, Filter } from 'lucide-react';
import clsx from 'clsx';

interface TaskListProps {
  tasks: Task[];
  onTaskComplete: (taskId: number) => Promise<void>;
  onTaskDelete: (taskId: number) => void;
  onTaskEdit: (task: Task) => void;
}

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onTaskComplete,
  onTaskDelete,
  onTaskEdit,
}) => {
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed' | 'upcoming'>('all');
  const [subjectFilter, setSubjectFilter] = useState<string>('all');

  // Collect unique subjects
  const allSubjects = Array.from(new Set(tasks.map(t => t.subject || 'Geral'))).sort();

  const filteredTasks = tasks.filter(task => {
    // 1. Subject Filter
    const taskSubject = task.subject || 'Geral';
    if (subjectFilter !== 'all' && taskSubject !== subjectFilter) {
      return false;
    }

    // 2. Status/Date Filter
    if (filter === 'pending') return !task.is_completed;
    if (filter === 'completed') return task.is_completed;
    if (filter === 'upcoming') {
      if (task.is_completed || !task.due_date) return false;
      const dueDate = parseISO(task.due_date);
      const limitDate = addDays(new Date(), 7);
      return (isBefore(dueDate, limitDate) || isSameDay(dueDate, limitDate)) && isAfter(dueDate, new Date(new Date().setHours(0, 0, 0, 0)));
    }
    return true; // 'all'
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

  const groupedTasks = sortedTasks.reduce((acc, task) => {
    const subject = task.subject || 'Geral';
    if (!acc[subject]) {
      acc[subject] = [];
    }
    acc[subject].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  // Ordena também as chaves das disciplinas em ordem alfabética, opcional,
  // mas deixa "Geral" para o final.
  const subjectGroups = Object.keys(groupedTasks).sort((a, b) => {
    if (a === 'Geral') return 1;
    if (b === 'Geral') return -1;
    return a.localeCompare(b);
  });

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            Minhas Tarefas
          </h2>

          <div className="flex flex-wrap items-center gap-4">
            {/* Subject Filter Dropdown */}
            <div className="flex items-center space-x-2 border-r border-gray-200 pr-4">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={subjectFilter}
                onChange={(e) => setSubjectFilter(e.target.value)}
                className="text-sm border-gray-300 rounded-md shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 text-gray-700 bg-gray-50 py-1"
              >
                <option value="all">Todas Disciplinas</option>
                {allSubjects.map(sub => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>

            {/* Status Tabs */}
            <div className="flex space-x-1 bg-gray-100/50 p-1 rounded-lg">
              {(['all', 'pending', 'upcoming', 'completed'] as const).map((filterOption) => (
                <button
                  key={filterOption}
                  onClick={() => setFilter(filterOption)}
                  className={clsx(
                    'px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ease-in-out',
                    filter === filterOption
                      ? 'bg-white text-indigo-700 shadow-sm ring-1 ring-gray-900/5'
                      : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200/50'
                  )}
                >
                  {filterOption === 'all' && 'Todas'}
                  {filterOption === 'pending' && 'Pendentes'}
                  {filterOption === 'upcoming' && 'Urgentes (7d)'}
                  {filterOption === 'completed' && 'Concluídas'}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col">
        {sortedTasks.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <BookOpen className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <p className="text-lg font-medium text-gray-900">Nenhuma tarefa encontrada</p>
            <p className="mt-1">Tente remover os filtros ou criar uma nova tarefa.</p>
          </div>
        ) : (
          subjectGroups.map(subject => (
            <div key={subject} className="mb-2">
              <div className="bg-gray-50 px-6 py-3 border-b border-y border-gray-200">
                <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider flex items-center">
                  <BookOpen className="w-4 h-4 mr-2 text-indigo-500" />
                  {subject}
                  <span className="ml-2 bg-indigo-100 text-indigo-700 text-xs py-0.5 px-2 rounded-full">
                    {groupedTasks[subject].length}
                  </span>
                </h3>
              </div>
              <div className="divide-y divide-gray-100">
                {groupedTasks[subject].map((task) => (
                  <div
                    key={task.id}
                    className={clsx(
                      'p-6 hover:bg-slate-50 transition-colors',
                      task.is_completed && 'opacity-60 bg-gray-50'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <button
                          onClick={() => !task.is_completed && onTaskComplete(task.id)}
                          disabled={task.is_completed}
                          className={clsx(
                            'mt-1 flex-shrink-0 transition-transform active:scale-95',
                            task.is_completed
                              ? 'text-green-500 cursor-default'
                              : 'text-gray-400 hover:text-indigo-600'
                          )}
                        >
                          {task.is_completed ? (
                            <CheckCircle className="w-6 h-6" />
                          ) : (
                            <Circle className="w-6 h-6" />
                          )}
                        </button>

                        <div className="flex-1 min-w-0">
                          <h3 className={clsx(
                            'text-base font-semibold',
                            task.is_completed ? 'line-through text-gray-500' : 'text-gray-900'
                          )}>
                            {task.title}
                          </h3>

                          {task.description && (
                            <p className="mt-1.5 text-sm text-gray-600 line-clamp-2">
                              {task.description}
                            </p>
                          )}

                          <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-gray-500">
                            <span className={clsx(
                              "flex items-center px-2 py-1 rounded-md border",
                              !task.is_completed && isOverdue(task.due_date)
                                ? 'border-red-200 bg-red-50 text-red-700 font-medium'
                                : 'border-gray-200 bg-white'
                            )}>
                              <Clock className={clsx(
                                "w-4 h-4 mr-1.5",
                                !task.is_completed && isOverdue(task.due_date) ? "text-red-500" : "text-gray-400"
                              )} />
                              {format(parseISO(task.due_date), "dd 'de' MMM, HH:mm", { locale: ptBR })}
                            </span>

                            <span className="font-medium bg-indigo-50 text-indigo-700 px-2 py-1 rounded-md border border-indigo-100">
                              Peso: {task.weight}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 ml-4 border-l border-gray-200 pl-4">
                        <button
                          onClick={() => onTaskEdit(task)}
                          className="p-2 text-gray-400 hover:text-indigo-600 transition-colors rounded-lg hover:bg-indigo-50"
                          title="Editar tarefa"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(task.id)}
                          className="p-2 text-gray-400 hover:text-red-600 transition-colors rounded-lg hover:bg-red-50"
                          title="Excluir tarefa"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
