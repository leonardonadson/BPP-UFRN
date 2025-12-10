from datetime import date, datetime
from functools import lru_cache

from sqlalchemy.orm import Session

# CORREÇÃO: Importações alteradas para absolutas
from app.models import Task, User
from app.services.badge_service import check_and_award_badges

@lru_cache(maxsize=128)
def calculate_task_points(weight: int, completed_on_time: bool = True) -> int:
    """Calcula os pontos de uma tarefa."""
    base_points = weight * 10
    if completed_on_time:
        return base_points
    return max(base_points // 2, 5)


def update_user_streak(user: User, _db: Session) -> bool:
    """Atualiza o streak do usuário. Não realiza commit."""
    today = date.today()
    last_activity = user.last_activity_date.date() if user.last_activity_date else None

    streak_incremented = False

    if last_activity is None:
        user.current_streak = 1
        streak_incremented = True
    elif (today - last_activity).days == 1:
        user.current_streak += 1
        streak_incremented = True
    elif last_activity == today:
        if user.current_streak == 0:
            user.current_streak = 1
            streak_incremented = True
    else: # Mais de um dia de inatividade
        user.current_streak = 1
        streak_incremented = True

    user.last_activity_date = datetime.now()
    return streak_incremented


def award_points_for_task(user: User, task: Task, _db: Session) -> int:
    """Calcula e atribui pontos. Não realiza commit."""
    on_time = task.due_date is None or datetime.now() <= task.due_date
    points = calculate_task_points(task.weight, on_time)

    user.total_points += points
    task.points_awarded = points
    task.completed_at = datetime.now()

    return points


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
    db.flush()
    badges_earned = check_and_award_badges(user, db)

    db.commit()

    return {
        "task": task,
        "points_earned": points_earned,
        "streak_updated": streak_updated,
        "badges_earned": badges_earned
    }
