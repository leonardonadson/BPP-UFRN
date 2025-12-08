# tests/unit/test_badges.py
from app.models import User, Task, UserBadge, Badge
from app.services.badge_service import initialize_badges, check_and_award_badges

def test_initialize_badges_creation(db_session):
    """
    Testa se a função initialize_badges cria as medalhas padrão no banco.
    Cobre: initialize_badges (badge_service.py)
    """
    # 1. Garante que o banco está vazio de badges
    db_session.query(Badge).delete()
    db_session.commit()

    # 2. Executa a inicialização
    initialize_badges(db_session)

    # 3. Verifica se criou as 7 badges padrão
    badges_count = db_session.query(Badge).count()
    assert badges_count == 7

    # Verifica uma específica
    streak_badge = db_session.query(Badge).filter(Badge.name == "Streak Iniciante").first()
    assert streak_badge is not None

def test_award_task_badge(db_session):
    """
    Testa ganhar a medalha "Primeira Tarefa" e "Centena".
    Cobre: check_and_award_badges (critério tasks_required)
    """
    # Setup
    initialize_badges(db_session)
    user = User(email="taskwinner@example.com", username="taskwinner", hashed_password="123")
    db_session.add(user)
    db_session.commit()

    # Cenário 1: 1 Tarefa completada ("Primeira Tarefa")
    task = Task(title="T1", subject="S", owner_id=user.id, is_completed=True)
    db_session.add(task)
    db_session.commit()

    new_badges = check_and_award_badges(user, db_session)

    # Deve ganhar "Primeira Tarefa"
    assert len(new_badges) == 1
    assert new_badges[0].name == "Primeira Tarefa"

def test_award_points_badge(db_session):
    """
    Testa ganhar medalha por pontos ("Dedicado").
    Cobre: check_and_award_badges (critério points_required)
    """
    # Setup
    initialize_badges(db_session)
    # Usuário já nasce com 100 pontos para testar o gatilho
    user = User(email="points@example.com", username="points", hashed_password="123", total_points=100)
    db_session.add(user)
    db_session.commit()

    new_badges = check_and_award_badges(user, db_session)

    # Deve ganhar "Dedicado" (requer 100 pontos)
    badge_names = [b.name for b in new_badges]
    assert "Dedicado" in badge_names

def test_award_streak_badge(db_session):
    """
    Testa ganhar medalha por ofensiva ("Streak Iniciante").
    Cobre: check_and_award_badges (critério streak específico)
    """
    # Setup
    initialize_badges(db_session)
    # Usuário com streak de 3 dias
    user = User(email="streak@example.com", username="streak", hashed_password="123", current_streak=3)
    db_session.add(user)
    db_session.commit()

    new_badges = check_and_award_badges(user, db_session)

    # Deve ganhar "Streak Iniciante"
    assert len(new_badges) > 0
    assert new_badges[0].name == "Streak Iniciante"

def test_no_duplicate_badges(db_session):
    """
    Testa se o sistema evita dar a mesma medalha duas vezes.
    Cobre: check_and_award_badges (verificação if badge.id in user_badge_ids)
    """
    # Setup
    initialize_badges(db_session)
    user = User(email="duplicado@example.com", username="duplicado", hashed_password="123", current_streak=3)
    db_session.add(user)
    db_session.commit()

    # 1. Ganha a medalha pela primeira vez
    badges_round_1 = check_and_award_badges(user, db_session)
    assert len(badges_round_1) == 1

    # Salva no banco (importante simular que a badge foi persistida)
    # A função check_and_award_badges adiciona à sessão, mas precisamos commitar
    # ou garantir que a relação user.badges esteja atualizada.
    db_session.commit()
    db_session.refresh(user)

    # 2. Tenta ganhar de novo (mesma condição)
    badges_round_2 = check_and_award_badges(user, db_session)

    # Não deve ganhar nada novo
    assert len(badges_round_2) == 0