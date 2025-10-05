from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_length_validator(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('A senha não pode ter mais de 72 bytes')
        if len(v) < 6:
            raise ValueError('A senha deve ter pelo menos 6 caracteres')
        return v
    
    @validator('username')
    def username_validator(cls, v):
        if len(v) < 3:
            raise ValueError('O nome de usuário deve ter pelo menos 3 caracteres')
        if len(v) > 50:
            raise ValueError('O nome de usuário não pode ter mais de 50 caracteres')
        return v

class User(UserBase):
    id: int
    total_points: int
    current_streak: int
    last_activity_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# REATORAÇÃO: Nova classe para agrupar os parâmetros de filtro de tarefas.
# Isto resolve o code smell "Long Parameter List" no router.

class TaskFilterParams(BaseModel):
    skip: int = 0
    limit: int = 100
    subject: Optional[str] = None
    completed: Optional[bool] = None

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    weight: int = 1
    due_date: Optional[datetime] = None
    
    @validator('title')
    def title_validator(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('O título deve ter pelo menos 3 caracteres')
        if len(v) > 200:
            raise ValueError('O título não pode ter mais de 200 caracteres')
        return v.strip()
    
    @validator('subject')
    def subject_validator(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('A disciplina deve ter pelo menos 2 caracteres')
        if len(v) > 100:
            raise ValueError('A disciplina não pode ter mais de 100 caracteres')
        return v.strip()
    
    @validator('weight')
    def weight_validator(cls, v):
        if v < 1 or v > 10:
            raise ValueError('O peso deve estar entre 1 e 10')
        return v
    
    @validator('description')
    def description_validator(cls, v):
        if v and len(v) > 1000:
            raise ValueError('A descrição não pode ter mais de 1000 caracteres')
        return v.strip() if v else v

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    is_completed: bool
    completed_at: Optional[datetime]
    points_awarded: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class BadgeBase(BaseModel):
    name: str
    description: str
    icon: str
    points_required: int = 0
    tasks_required: int = 0

class Badge(BadgeBase):
    id: int

    class Config:
        from_attributes = True

class UserBadge(BaseModel):
    badge: Badge
    earned_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def password_validator(cls, v):
        if len(v) < 1:
            raise ValueError('A senha é obrigatória')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('A senha não pode ter mais de 72 bytes')
        return v

class TaskResponse(BaseModel):
    task: Task
    points_earned: int
    streak_updated: bool
    badges_earned: List[Badge] = []

class UserDashboard(BaseModel):
    user: User
    tasks: List[Task]
    badges: List[UserBadge]

class UserStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    total_points: int
    current_streak: int
    badges_count: int
    completion_rate: float
    
    class Config:
        from_attributes = True

class TasksBySubject(BaseModel):
    subject: str
    total_tasks: int
    completed_tasks: int
    total_points: int

class MessageResponse(BaseModel):
    message: str
    success: bool = True
 
class ErrorResponse(BaseModel):
    detail: str
    error: bool = True