# Conteúdo para: api/app/routers/tasks.py (Versão 2)

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..schemas import TaskCreate, Task, TaskResponse
from ..models import Task as TaskModel, User
from ..auth.auth_bearer import get_current_user
# REFATORAÇÃO: Apenas o novo serviço unificado é importado
from ..services.score_service import process_task_completion 

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# REFATORAÇÃO: Função de dependência extraída para remover código duplicado
def get_task_for_user_dependency(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskModel:
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
    
    query = query.order_by(TaskModel.due_date.asc(), TaskModel.weight.desc())
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=Task)
def get_task(
    task: TaskModel = Depends(get_task_for_user_dependency) # REFATORAÇÃO 
):
    """Busca uma tarefa específica do usuário"""
    return task

@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task: TaskModel = Depends(get_task_for_user_dependency), # REFATORAÇÃO
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca uma tarefa como concluída delegando para a camada de serviço"""
    if task.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tarefa já foi concluída"
        )
    
    # REFATORAÇÃO: Toda a lógica de negócio foi movida para a camada de serviço.
    # O router agora apenas chama a função orquestradora.
    completion_data = process_task_completion(current_user, task, db)
    
    return completion_data

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task: TaskModel = Depends(get_task_for_user_dependency), # REfATORAÇÃO APLICADA
    db: Session = Depends(get_db)
):
    """Deleta uma tarefa do usuário"""
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