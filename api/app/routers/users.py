"""Módulo com os endpoints para informações de utilizadores."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.auth_bearer import get_current_user
from ..database import get_db
from ..models import User as UserModel
from ..schemas import User, UserDashboard

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=User)
def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Retorna informações do usuário atual."""
    return current_user

@router.get("/dashboard", response_model=UserDashboard)
def get_user_dashboard(
    current_user: UserModel = Depends(get_current_user)
    # LIMPEZA: Removido o argumento 'db: Session' que não era utilizado.
):
    """Retorna dashboard completo do usuário."""
    tasks = current_user.tasks
    badges = current_user.badges
    
    return {"user": current_user, "tasks": tasks, "badges": badges}
