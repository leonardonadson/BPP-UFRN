"""Módulo com os endpoints para informações de utilizadores."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

# CORREÇÃO: Importações alteradas para absolutas
from app.auth.auth_bearer import get_current_user
from app.auth.auth_handler import get_password_hash
from app.database import get_db
from app.models import User as UserModel
from app.models import Task
from app.schemas import User, UserDashboard, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Retorna informações do usuário atual."""
    return current_user


@router.put("/me", response_model=User)
def update_current_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza as informações do usuário atual (Nome de usuário, email, senha)."""
    
    # Validações de duplicidade
    if user_update.email and user_update.email != current_user.email:
        if db.query(UserModel).filter(UserModel.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado para outro usuário"
            )
            
    if user_update.username and user_update.username != current_user.username:
        if db.query(UserModel).filter(UserModel.username == user_update.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário já existe"
            )

    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        current_user.hashed_password = hashed_password
        del update_data["password"]

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exclui a conta do usuário logado e todos os dados em cascata."""
    db.delete(current_user)
    db.commit()
    return None



@router.get("/dashboard", response_model=UserDashboard)
def get_user_dashboard(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna dashboard completo do usuário (Otimizado)."""

    # 1. OTIMIZAÇÃO GARGALO #4 (N+1):
    # Recarrega o usuário trazendo Tarefas e Badges em uma única Query (Eager Loading)
    # Isso evita queries extras quando acessamos .tasks e .badges depois.
    user_full = db.query(UserModel).options(
        joinedload(UserModel.tasks),
        joinedload(UserModel.badges)
    ).filter(UserModel.id == current_user.id).first()

    # 2. OTIMIZAÇÃO GARGALO #1 (Soma em Memória):
    # Faz a soma dos pontos diretamente no Banco de Dados (SQL SUM)
    # Em vez de: sum(t.points_awarded for t in tasks)
    total_task_points = db.query(func.sum(Task.points_awarded))\
        .filter(Task.owner_id == current_user.id).scalar() or 0

    # Lógica de visualização (apenas print)
    tasks_count = len(user_full.tasks)
    if tasks_count > 0:
        average = total_task_points / tasks_count
        print(f"Média: {average:.2f}")
    else:
        print("Média: 0 (Sem tarefas)")

    # Retorna o objeto carregado de forma otimizada
    return {
        "user": user_full,
        "tasks": user_full.tasks,
        "badges": user_full.badges
    }