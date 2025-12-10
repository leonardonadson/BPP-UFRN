from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# CORREÇÃO: Importações alteradas para absolutas
from app.auth.auth_bearer import get_current_user
from app.database import get_db
from app.models import Task as TaskModel
from app.models import User
from app.schemas import Task, TaskCreate, TaskFilterParams, TaskResponse
from app.services.score_service import process_task_completion

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_task_for_user_dependency(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskModel:
    """Dependência para buscar uma tarefa específica do usuário logado."""
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
    filters: TaskFilterParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista as tarefas do usuário com filtros opcionais"""
    query = db.query(TaskModel).filter(TaskModel.owner_id == current_user.id)

    # [OTIMIZAÇÃO DE PERFORMANCE - GARGALO #2]
    # Refatoração: Aplicamos os filtros diretamente no objeto Query (SQL WHERE)
    # ao invés de recuperar todos os dados (.all()) e filtrar com Python.
    # Isso implementa a técnica de "Push-down Predicate", economizando CPU e I/O.
    if filters.subject:
        query = query.filter(TaskModel.subject == filters.subject)

    if filters.completed is not None:
        query = query.filter(TaskModel.is_completed == filters.completed)

    # [OTIMIZAÇÃO DE PERFORMANCE - GARGALO #3]
    # Ordenação feita no banco para aproveitar índices (quando existirem)
    query = query.order_by(TaskModel.due_date.asc(), TaskModel.weight.desc())

    # Paginação via SQL (LIMIT/OFFSET) para evitar carregar a tabela inteira
    tasks = query.offset(filters.skip).limit(filters.limit).all()
    return tasks

@router.get("/{task_id}", response_model=Task)
def get_task(
    task: TaskModel = Depends(get_task_for_user_dependency)
):
    """Busca uma tarefa específica do usuário"""
    return task

@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task: TaskModel = Depends(get_task_for_user_dependency),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca uma tarefa como concluída delegando para a camada de serviço"""
    if task.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tarefa já foi concluída"
        )

    completion_data = process_task_completion(current_user, task, db)
    return completion_data

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task: TaskModel = Depends(get_task_for_user_dependency),
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
    """Lista todas as disciplinas distintas das tarefas do usuário"""
    subjects = db.query(TaskModel.subject).filter(
        TaskModel.owner_id == current_user.id,
        TaskModel.subject.isnot(None)
    ).distinct().all()

    return [subject[0] for subject in subjects]
