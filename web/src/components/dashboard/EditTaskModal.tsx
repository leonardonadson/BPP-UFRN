import React, { useEffect, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { Task, UpdateTaskRequest } from '@/types/task';
import type { Subject } from '@/types/subject';
import { taskService } from '@/services/taskService';
import { subjectService } from '@/services/subjectService';
import { X, ChevronDown } from 'lucide-react';

const editTaskSchema = z.object({
    title: z.string().min(1, 'Título é obrigatório'),
    description: z.string().optional(),
    subject: z.string().min(1, 'Disciplina é obrigatória'),
    weight: z.number().min(1).max(10),
    due_date: z.string().min(1, 'Data de entrega é obrigatória'),
});

type EditTaskFormData = z.infer<typeof editTaskSchema>;

interface EditTaskModalProps {
    task: Task;
    onClose: () => void;
    onTaskUpdated: () => void;
}

export const EditTaskModal: React.FC<EditTaskModalProps> = ({
    task,
    onClose,
    onTaskUpdated,
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
    } = useForm<EditTaskFormData>({
        resolver: zodResolver(editTaskSchema),
        defaultValues: {
            title: task.title,
            description: task.description || '',
            subject: task.subject,
            weight: task.weight,
        },
    });

    const subjectValue = watch('subject') || '';

    useEffect(() => {
        // Formatar a data para o input datetime-local
        if (task.due_date) {
            const date = new Date(task.due_date);
            setValue('due_date', date.toISOString().slice(0, 16));
        }

        // Carregar disciplinas
        subjectService.getSubjects()
            .then((data) => {
                setSubjects(data);
            })
            .catch(err => console.error('Erro ao carregar disciplinas:', err));
    }, [task.due_date, task.subject, setValue]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const onSubmit = async (data: EditTaskFormData) => {
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

            const updateData: UpdateTaskRequest = {
                ...data,
                due_date: new Date(data.due_date).toISOString(),
            };

            await taskService.updateTask(task.id, updateData);
            onTaskUpdated();
        } catch (error: any) {
            console.error('Erro ao atualizar tarefa:', error);
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
            className="fixed inset-0 backdrop-blur-sm bg-black/30 dark:bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto"
            onClick={handleOverlayClick}
            aria-modal="true"
            role="dialog"
        >
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-lg w-full transition-colors">
                <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">Editar Tarefa</h2>
                    <button
                        type="button"
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-1 transition duration-150 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-5">
                    {/* Título */}
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                            Título *
                        </label>
                        <input
                            {...register('title')}
                            type="text"
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                            placeholder="Ex: Estudar para prova de Matemática"
                        />
                        {errors.title && (
                            <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.title.message}</p>
                        )}
                    </div>

                    {/* Descrição */}
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                            Descrição
                        </label>
                        <textarea
                            {...register('description')}
                            rows={3}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none transition-colors"
                            placeholder="Detalhes adicionais sobre a tarefa..."
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        {/* Disciplina */}
                        <div ref={dropdownRef} className="relative">
                            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                                Disciplina *
                            </label>
                            <div className="relative">
                                <input
                                    {...register('subject')}
                                    type="text"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 pr-10 transition-colors"
                                    placeholder="Ex: Cálculo I, História, etc."
                                    autoComplete="off"
                                    onFocus={() => setShowDropdown(true)}
                                    onClick={() => setShowDropdown(true)}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowDropdown(!showDropdown)}
                                    className="absolute inset-y-0 right-0 px-3 flex items-center text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
                                >
                                    <ChevronDown className="w-5 h-5" />
                                </button>
                            </div>

                            {showDropdown && (
                                <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto transition-colors">
                                    {filteredSubjects.length > 0 ? (
                                        <ul className="py-1">
                                            {filteredSubjects.map(s => (
                                                <li
                                                    key={s.id}
                                                    className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-primary-50 dark:hover:bg-gray-700 cursor-pointer"
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
                                        <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                                            Nenhuma encontrada. Pressione <span className="font-semibold text-primary-600 dark:text-primary-400">Salvar</span> para criar <b>"{subjectValue}"</b>.
                                        </div>
                                    )}
                                </div>
                            )}

                            {errors.subject && (
                                <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.subject.message}</p>
                            )}
                        </div>
                        {/* Peso */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                                Peso (1-10) *
                            </label>
                            <input
                                {...register('weight', { valueAsNumber: true })}
                                type="number"
                                min="1"
                                max="10"
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                            />
                            {errors.weight && (
                                <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.weight.message}</p>
                            )}
                        </div>
                    </div>

                    {/* Data e Hora */}
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                            Data e Hora de Entrega *
                        </label>
                        <input
                            {...register('due_date')}
                            type="datetime-local"
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors style-color-scheme"
                            style={{ colorScheme: 'inherit' }}
                        />
                        {errors.due_date && (
                            <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.due_date.message}</p>
                        )}
                    </div>

                    {/* Botões */}
                    <div className="flex justify-end space-x-3 pt-4 border-t dark:border-gray-700 mt-6 transition-colors">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-6 py-2 text-sm font-bold text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition duration-150"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="px-6 py-2 text-sm font-bold text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 disabled:opacity-50 dark:shadow-neon dark:hover:shadow-neon-hover transition-all duration-300 shadow-md"
                        >
                            {isSubmitting ? 'Salvando...' : 'Salvar Alterações'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
