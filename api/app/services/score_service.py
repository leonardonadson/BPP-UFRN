# Conteúdo para: api/app/services/score_service.py (Versão 2)

from datetime import datetime, date
from sqlalchemy.orm import Session
from ..models import User, Task
from .badge_service import check_and_award_badges # Importar o serviço de badges

def calculate_task_points(weight: int, completed_on_time: bool = True) -> int:
    base_points = weight * 10
    if completed_on_time:
        return base_points
    else:
        return max(base_points // 2, 5)

def update_user_streak(user: User, db: Session) -> bool:
    """Atualiza o streak do usuário. O commit foi removido."""
    today = date.today()
    last_activity = user.last_activity_date.date() if user.last_activity_date else None
    
    streak_incremented = False
    if last_activity is None:
        user.current_streak = 1
        streak_incremented = True
    elif last_activity == today:
        return False 
    elif (today - last_activity).days == 1:
        user.current_streak += 1
        streak_incremented = True
    else:
        user.current_streak = 1
        streak_incremented = True
        
    if streak_incremented:
        user.last_activity_date = datetime.now()
    
    # REATORAÇÃO: O db.commit() foi removido daqui
    return streak_incremented

def award_points_for_task(user: User, task: Task, db: Session) -> int:
    """Calcula e atribui pontos. O commit foi removido."""
    on_time = task.due_date is None or datetime.now() <= task.due_date
    points = calculate_task_points(task.weight, on_time)
    
    user.total_points += points
    task.points_awarded = points
    task.completed_at = datetime.now()
    
    # REATORAÇÃO: O db.commit() foi removido daqui
    return points

# REATORAÇÃO: Nova função para orquestrar a lógica de negócio de completar uma tarefa
def process_task_completion(user: User, task: Task, db: Session) -> dict:
    """
    Orquestra todo o processo de completar uma tarefa:
    1. Marca a tarefa como concluída.
    2. Atribui pontos.
    3. Atualiza o streak.
    4. Verifica e concede badges.
    5. Realiza um único commit no banco de dados.
    """
    task.is_completed = True
    
    points_earned = award_points_for_task(user, task, db)
    streak_updated = update_user_streak(user, db)
    badges_earned = check_and_award_badges(user, db)
    
    db.commit() # Único commit para toda a operação
    
    return {
        "task": task,
        "points_earned": points_earned,
        "streak_updated": streak_updated,
        "badges_earned": badges_earned
    }