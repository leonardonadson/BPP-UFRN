from sqlalchemy.orm import Session
from ..models import User, Badge, UserBadge, Task
from typing import List

def initialize_badges(db: Session):
    """Inicializa as badges padrão no banco de dados"""
    default_badges = [
        {"name": "Primeira Tarefa", "description": "Completou sua primeira tarefa", "icon": "🎯", "tasks_required": 1},
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
    
    # Buscar todas as badges disponíveis
    all_badges = db.query(Badge).all()
    
    # Badges já conquistadas pelo usuário
    user_badge_ids = [ub.badge_id for ub in user.badges]
    
    # Contar tarefas completadas
    completed_tasks = db.query(Task).filter(
        Task.owner_id == user.id,
        Task.is_completed == True
    ).count()
    
    for badge in all_badges:
        if badge.id in user_badge_ids:
            continue  # Usuário já possui esta badge
        
        should_award = False
        
        # Verificar critérios baseados em pontos
        if badge.points_required > 0 and user.total_points >= badge.points_required:
            should_award = True
        
        # Verificar critérios baseados em tarefas completadas
        if badge.tasks_required > 0 and completed_tasks >= badge.tasks_required:
            should_award = True
        
        # Verificar critérios especiais para streaks
        if badge.name == "Streak Iniciante" and user.current_streak >= 3:
            should_award = True
        elif badge.name == "Streak Master" and user.current_streak >= 7:
            should_award = True
        
        if should_award:
            user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            awarded_badges.append(badge)
    
    if awarded_badges:
        db.commit()
    
    return awarded_badges
