from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserDashboard, User
from ..models import User as UserModel
from ..auth.auth_bearer import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=User)
def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    return current_user

@router.get("/dashboard", response_model=UserDashboard)
def get_user_dashboard(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna dashboard completo do usuário"""
    # Buscar tarefas do usuário
    tasks = current_user.tasks
    
    # Buscar badges do usuário
    badges = current_user.badges
    
    return {
        "user": current_user,
        "tasks": tasks,
        "badges": badges
    }
