import { api } from './api';
import type { Subject, CreateSubjectRequest } from '@/types/subject';

export const subjectService = {
    async createSubject(data: CreateSubjectRequest): Promise<Subject> {
        try {
            const { data: subject } = await api.post<Subject>('/subjects/', data);
            return subject;
        } catch (error: any) {
            throw error;
        }
    },

    async getSubjects(): Promise<Subject[]> {
        try {
            const { data } = await api.get<Subject[]>('/subjects/');
            return data;
        } catch (error: any) {
            throw error;
        }
    },

    async deleteSubject(subjectId: number): Promise<void> {
        try {
            await api.delete(`/subjects/${subjectId}`);
        } catch (error: any) {
            throw error;
        }
    },
};
