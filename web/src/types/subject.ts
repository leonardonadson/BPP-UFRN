export interface Subject {
  id: number;
  name: string;
  created_at: string;
  owner_id: number;
}

export interface CreateSubjectRequest {
  name: string;
}
