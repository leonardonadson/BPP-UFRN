from datetime import datetime, date
from sqlalchemy.orm import Session
from ..models import User, Task

def calculate_task_points(weight: int, completed_on_time: bool = True) -> int:
    """Calcula pontos baseado no peso da tarefa e se foi concluída no prazo"""
    base_points = weight * 10
    if completed_on_time:
        return base_points
    else:
        return max(base_points // 2, 5)  # Pelo menos 5 pontos

def update_user_streak(user: User, db: Session) -> bool:
    """Atualiza o streak do usuário e retorna se foi incrementado"""
    today = date.today()
    last_activity = user.last_activity_date.date() if user.last_activity_date else None
    
    if last_activity is None:
        # Primeira atividade
        user.current_streak = 1
        user.last_activity_date = datetime.now()
        db.commit()
        return True
    elif last_activity == today:
        # Já teve atividade hoje
        return False
    elif (today - last_activity).days == 1:
        # Atividade consecutiva
        user.current_streak += 1
        user.last_activity_date = datetime.now()
        db.commit()
        return True
    else:
        # Quebrou o streak
        user.current_streak = 1
        user.last_activity_date = datetime.now()
        db.commit()
        return True

def award_points_for_task(user: User, task: Task, db: Session) -> int:
    """Calcula e atribui pontos pela conclusão de uma tarefa"""
    on_time = task.due_date is None or datetime.now() <= task.due_date
    points = calculate_task_points(task.weight, on_time)
    
    user.total_points += points
    task.points_awarded = points
    task.completed_at = datetime.now()
    
    db.commit()
    return points
