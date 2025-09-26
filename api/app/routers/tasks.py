from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..schemas import TaskCreate, Task, TaskResponse
from ..models import Task as TaskModel, User
from ..auth.auth_bearer import get_current_user
from ..services.score_service import award_points_for_task, update_user_streak
from ..services.badge_service import check_and_award_badges

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova tarefa para o usuário"""
    db_task = TaskModel(
        **task.dict(),
        owner_id=current_user.id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@router.get("/", response_model=List[Task])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = Query(None, description="Filtrar por disciplina"),
    completed: Optional[bool] = Query(None, description="Filtrar por status de conclusão"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista as tarefas do usuário com filtros opcionais"""
    query = db.query(TaskModel).filter(TaskModel.owner_id == current_user.id)
    
    if subject:
        query = query.filter(TaskModel.subject == subject)
    
    if completed is not None:
        query = query.filter(TaskModel.is_completed == completed)
    
    # Ordenar por urgência (devido date próximo primeiro, depois por peso)
    query = query.order_by(TaskModel.due_date.asc(), TaskModel.weight.desc())
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca uma tarefa específica do usuário"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    return task

@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca uma tarefa como concluída e calcula pontos/streaks/badges"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    if task.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tarefa já foi concluída"
        )
    
    # Marcar como concluída
    task.is_completed = True
    
    # Calcular e atribuir pontos
    points_earned = award_points_for_task(current_user, task, db)
    
    # Atualizar streak
    streak_updated = update_user_streak(current_user, db)
    
    # Verificar e conceder badges
    badges_earned = check_and_award_badges(current_user, db)
    
    return {
        "task": task,
        "points_earned": points_earned,
        "streak_updated": streak_updated,
        "badges_earned": badges_earned
    }

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deleta uma tarefa do usuário"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    db.delete(task)
    db.commit()

@router.get("/subjects/list", response_model=List[str])
def list_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas as disciplinas das tarefas do usuário"""
    subjects = db.query(TaskModel.subject).filter(
        TaskModel.owner_id == current_user.id,
        TaskModel.subject.isnot(None)
    ).distinct().all()
    
    return [subject[0] for subject in subjects]
