# tests/unit/test_score_service_db.py
from datetime import datetime, timedelta
from app.models import User, Task
from app.services.score_service import process_task_completion, update_user_streak

def test_process_task_completion_success(db_session):
    """
    Testa o fluxo completo de completar uma tarefa:
    1. Cria usuário e tarefa no banco.
    2. Executa a função process_task_completion.
    3. Verifica se os pontos foram dados e a tarefa marcada como concluída.
    """
    # ARRANGE
    # Criar um usuário de teste
    user = User(email="teste@example.com", username="testuser", hashed_password="123")
    db_session.add(user)
    db_session.commit()

    # Criar uma tarefa para esse usuário
    task = Task(
        title="Estudar Pytest",
        subject="Programação",
        weight=2,
        owner_id=user.id
    )
    db_session.add(task)
    db_session.commit()

    # ACT
    # Chama a função principal do serviço
    result = process_task_completion(user, task, db_session)

    # ASSERT
    assert task.is_completed is True
    assert task.points_awarded == 20  # Peso 2 * 10 = 20
    assert user.total_points == 20
    assert result["streak_updated"] is True  # Primeiro uso deve iniciar streak

def test_streak_increment(db_session):
    """
    Testa se o streak aumenta quando o usuário faz tarefa em dias consecutivos.
    """
    # ARRANGE
    # Simula um usuário que fez atividade ONTEM
    yesterday = datetime.now() - timedelta(days=1)
    user = User(
        email="streak@example.com",
        username="streakuser",
        current_streak=5,
        last_activity_date=yesterday
    )
    db_session.add(user)
    db_session.commit()

    # ACT
    # Chama apenas a função de atualizar streak
    streak_updated = update_user_streak(user, db_session)

    # ASSERT
    assert streak_updated is True
    assert user.current_streak == 6  # 5 + 1