"""Módulo com os endpoints para informações de utilizadores."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# CORREÇÃO: Importações alteradas para absolutas
from app.auth.auth_bearer import get_current_user
from app.database import get_db
from app.models import User as UserModel
from app.schemas import User, UserDashboard

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Retorna informações do usuário atual."""
    return current_user


@router.get("/dashboard", response_model=UserDashboard)
def get_user_dashboard(
    current_user: UserModel = Depends(get_current_user),
    _db: Session = Depends(get_db) # Renomeado para _db
):
    """Retorna dashboard completo do usuário."""
    # Embora 'db' não seja usado diretamente aqui, as relações do SQLAlchemy
    # podem precisar de uma sessão ativa para carregar dados (lazy loading).
    # Por isso, é uma boa prática mantê-lo.
    tasks = current_user.tasks
    badges = current_user.badges

    return {"user": current_user, "tasks": tasks, "badges": badges}