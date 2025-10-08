# Conteúdo para: api/app/services/badge_service.py (Versão 2)

from typing import List

from sqlalchemy.orm import Session
from ..models import Badge, Task, User, UserBadge

def initialize_badges(db: Session):
    default_badges = [
        {
            "name": "Primeira Tarefa", "description": "Completou sua primeira tarefa",
            "icon": "🎯", "tasks_required": 1
        },
        {"name": "Streak Iniciante", "description": "Manteve um streak de 3 dias", "icon": "🔥", "points_required": 0},
        {"name": "Estudioso", "description": "Completou 10 tarefas", "icon": "📚", "tasks_required": 10},
        {"name": "Dedicado", "description": "Acumulou 100 pontos", "icon": "⭐", "points_required": 100},
        {"name": "Streak Master", "description": "Manteve um streak de 7 dias", "icon": "🏆", "points_required": 0},
        {"name": "Centena", "description": "Completou 100 tarefas", "icon": "💯", "tasks_required": 100},
        {"name": "Milhar", "description": "Acumulou 1000 pontos", "icon": "💎", "points_required": 1000},
    ]
    
    for badge_data in default_badges:
        existing_badge = db.query(Badge).filter(Badge.name == badge_data["name"]).first()
        if not existing_badge:
            badge = Badge(**badge_data)
            db.add(badge)
    
    db.commit()

def check_and_award_badges(user: User, db: Session) -> List[Badge]:
    """Verifica e concede badges baseadas nas conquistas do usuário"""
    awarded_badges = []
    all_badges = db.query(Badge).all()
    user_badge_ids = [ub.badge_id for ub in user.badges]
    
    completed_tasks = db.query(Task).filter(
        Task.owner_id == user.id, Task.is_completed is True
    ).count()
    
    for badge in all_badges:
        if badge.id in user_badge_ids:
            continue
        
        should_award = False
        
        if badge.points_required > 0 and user.total_points >= badge.points_required:
            should_award = True
        
        if badge.tasks_required > 0 and completed_tasks >= badge.tasks_required:
            should_award = True
        
        if badge.name == "Streak Iniciante" and user.current_streak >= 3:
            should_award = True
        elif badge.name == "Streak Master" and user.current_streak >= 7:
            should_award = True
        
        if should_award:
            user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            awarded_badges.append(badge)
    
    # REATORAÇÃO: O db.commit() foi removido daqui para ser centralizado
    # na função de serviço principal que orquestra a conclusão da tarefa.
    
    return awarded_badges