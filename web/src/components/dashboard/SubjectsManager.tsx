import React, { useEffect, useState } from 'react';
import type { Subject } from '@/types/subject';
import { subjectService } from '@/services/subjectService';
import { BookOpen, Plus, Trash2, Loader2 } from 'lucide-react';

interface SubjectsManagerProps {
    onSubjectsChange?: () => void;
}

export const SubjectsManager: React.FC<SubjectsManagerProps> = ({ onSubjectsChange }) => {
    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [newSubjectName, setNewSubjectName] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isAdding, setIsAdding] = useState(false);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(null);

    const loadSubjects = async () => {
        try {
            const data = await subjectService.getSubjects();
            setSubjects(data);
        } catch (err) {
            console.error('Erro ao carregar disciplinas:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadSubjects();
    }, []);

    const handleAddSubject = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newSubjectName.trim()) return;

        setIsAdding(true);
        setError(null);

        try {
            await subjectService.createSubject({ name: newSubjectName.trim() });
            setNewSubjectName('');
            await loadSubjects();
            onSubjectsChange?.();
        } catch (err: any) {
            const detail = err.response?.data?.detail;
            setError(typeof detail === 'string' ? detail : 'Erro ao criar disciplina');
        } finally {
            setIsAdding(false);
        }
    };

    const handleDeleteSubject = async (subjectId: number) => {
        setDeletingId(subjectId);
        try {
            await subjectService.deleteSubject(subjectId);
            await loadSubjects();
            onSubjectsChange?.();
        } catch (err) {
            console.error('Erro ao deletar disciplina:', err);
        } finally {
            setDeletingId(null);
        }
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-5 transition-colors">
            <div className="flex items-center space-x-2 mb-4">
                <BookOpen className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h3 className="text-base font-semibold text-gray-900 dark:text-white">Disciplinas</h3>
            </div>

            {/* Formulário para adicionar */}
            <form onSubmit={handleAddSubject} className="flex space-x-2 mb-4">
                <input
                    type="text"
                    value={newSubjectName}
                    onChange={(e) => setNewSubjectName(e.target.value)}
                    placeholder="Nova disciplina..."
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    disabled={isAdding}
                />
                <button
                    type="submit"
                    disabled={isAdding || !newSubjectName.trim()}
                    className="p-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 disabled:opacity-50 transition duration-150"
                >
                    {isAdding ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <Plus className="w-4 h-4" />
                    )}
                </button>
            </form>

            {error && (
                <p className="text-xs text-red-600 dark:text-red-400 mb-3">{error}</p>
            )}

            {/* Lista de disciplinas */}
            {isLoading ? (
                <div className="text-center py-4">
                    <Loader2 className="w-5 h-5 animate-spin text-gray-400 dark:text-gray-500 mx-auto" />
                </div>
            ) : subjects.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                    Nenhuma disciplina cadastrada
                </p>
            ) : (
                <ul className="space-y-2">
                    {subjects.map((subject) => (
                        <li
                            key={subject.id}
                            className="flex items-center justify-between px-3 py-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg group hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        >
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-200 truncate">
                                {subject.name}
                            </span>
                            <button
                                onClick={() => handleDeleteSubject(subject.id)}
                                disabled={deletingId === subject.id}
                                className="p-1 text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 transition-colors rounded-full hover:bg-red-50 dark:hover:bg-red-900/30 opacity-0 group-hover:opacity-100 focus:opacity-100"
                            >
                                {deletingId === subject.id ? (
                                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                ) : (
                                    <Trash2 className="w-3.5 h-3.5" />
                                )}
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};
