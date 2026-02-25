import React, { useEffect, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { CreateTaskRequest } from '@/types/task';
import type { Subject } from '@/types/subject';
import { taskService } from '@/services/taskService';
import { subjectService } from '@/services/subjectService';
import { X, ChevronDown } from 'lucide-react';

const taskSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório'),
  description: z.string().optional(),
  subject: z.string().min(1, 'Disciplina é obrigatória'),
  weight: z.number().min(1).max(10),
  due_date: z.string().min(1, 'Data de entrega é obrigatória'),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface CreateTaskModalProps {
  onClose: () => void;
  onTaskCreated: () => void;
}

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  onClose,
  onTaskCreated
}) => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  });

  const subjectValue = watch('subject') || '';

  useEffect(() => {
    // Definir data/hora padrão como amanhã às 23:59
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(23, 59, 0, 0);
    setValue('due_date', tomorrow.toISOString().slice(0, 16));

    // Carregar disciplinas
    subjectService.getSubjects()
      .then(setSubjects)
      .catch(err => console.error('Erro ao carregar disciplinas:', err));
  }, [setValue]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const onSubmit = async (data: TaskFormData) => {
    try {
      // Criar a disciplina se não existir
      const existing = subjects.find(s => s.name.toLowerCase() === data.subject.toLowerCase());
      if (!existing) {
        try {
          await subjectService.createSubject({ name: data.subject.trim() });
        } catch (err) {
          console.log('Disciplina não criada ou já existia.');
        }
      }

      const taskData: CreateTaskRequest = {
        ...data,
        due_date: new Date(data.due_date).toISOString(),
      };

      await taskService.createTask(taskData);
      onTaskCreated();
    } catch (error: any) {
      console.error('Erro ao criar tarefa:', error);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const filteredSubjects = subjects.filter(s =>
    s.name.toLowerCase().includes(subjectValue.toLowerCase())
  );

  return (
    <div
      className="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-50 overflow-y-auto"
      onClick={handleOverlayClick}
      aria-modal="true"
      role="dialog"
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-lg w-full"
      >
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Nova Tarefa</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-1 transition duration-150 rounded-full hover:bg-gray-100"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-5">
          {/* Título */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Título *
            </label>
            <input
              {...register('title')}
              type="text"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Ex: Estudar para prova de Matemática"
            />
            {errors.title && (
              <p className="mt-1 text-xs text-red-600">{errors.title.message}</p>
            )}
          </div>

          {/* Descrição */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Descrição
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="Detalhes adicionais sobre a tarefa..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Disciplina */}
            <div ref={dropdownRef} className="relative">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Disciplina *
              </label>
              <div className="relative">
                <input
                  {...register('subject')}
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-10"
                  placeholder="Ex: Física, Cálculo..."
                  autoComplete="off"
                  onFocus={() => setShowDropdown(true)}
                  onClick={() => setShowDropdown(true)}
                />
                <button
                  type="button"
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  <ChevronDown className="w-5 h-5" />
                </button>
              </div>

              {showDropdown && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                  {filteredSubjects.length > 0 ? (
                    <ul className="py-1">
                      {filteredSubjects.map(s => (
                        <li
                          key={s.id}
                          className="px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 cursor-pointer"
                          onClick={() => {
                            setValue('subject', s.name, { shouldValidate: true });
                            setShowDropdown(false);
                          }}
                        >
                          {s.name}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="px-4 py-3 text-sm text-gray-500">
                      Nenhuma encontrada. Pressione <span className="font-semibold text-blue-600">Salvar</span> para criar <b>"{subjectValue}"</b>.
                    </div>
                  )}
                </div>
              )}

              {errors.subject && (
                <p className="mt-1 text-xs text-red-600">{errors.subject.message}</p>
              )}
            </div>

            {/* Peso */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Peso (1-10) *
              </label>
              <input
                {...register('weight', { valueAsNumber: true })}
                type="number"
                min="1"
                max="10"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              {errors.weight && (
                <p className="mt-1 text-xs text-red-600">{errors.weight.message}</p>
              )}
            </div>
          </div>

          {/* Data e Hora */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Data e Hora de Entrega *
            </label>
            <input
              {...register('due_date')}
              type="datetime-local"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            {errors.due_date && (
              <p className="mt-1 text-xs text-red-600">{errors.due_date.message}</p>
            )}
          </div>

          {/* Botões */}
          <div className="flex justify-end space-x-3 pt-4 border-t mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 text-sm font-bold text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-150"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 text-sm font-bold text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 disabled:opacity-50 transition duration-150 shadow-md"
            >
              {isSubmitting ? 'Criando...' : 'Criar Tarefa'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
