# tests/unit/test_tasks_errors.py
import pytest
from app.models import User, Task
from app.main import app
from app.auth.auth_bearer import get_current_user

# Fixture local para criar um usuário padrão para estes testes
@pytest.fixture
def auth_user(db_session):
    user = User(email="error_tester@example.com", username="errortester", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_complete_already_completed_task(client, db_session, auth_user):
    """
    Testa o erro 400 ao tentar completar uma tarefa que JÁ foi completada.
    Cobre: Linha 'if task.is_completed:' em routers/tasks.py
    """
    # 1. Setup: Criar tarefa já completada
    task = Task(title="Já Feita", subject="X", owner_id=auth_user.id, is_completed=True)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    task_id = task.id # Salvar ID

    # 2. Override Auth
    app.dependency_overrides[get_current_user] = lambda: auth_user

    # 3. Act: Tentar completar de novo
    response = client.patch(f"/tasks/{task_id}/complete")

    # 4. Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Tarefa já foi concluída"

    app.dependency_overrides = {}

def test_get_non_existent_task(client, auth_user):
    """
    Testa o erro 404 ao buscar uma tarefa que não existe.
    Cobre: get_task_for_user_dependency (erro 404)
    """
    app.dependency_overrides[get_current_user] = lambda: auth_user

    # ID 9999 não existe
    response = client.get("/tasks/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada"

    app.dependency_overrides = {}

def test_delete_task(client, db_session, auth_user):
    """
    Testa a deleção de tarefa com sucesso.
    Cobre: Rota delete em routers/tasks.py
    """
    # 1. Setup
    task = Task(title="Para Deletar", subject="Lixo", owner_id=auth_user.id)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    task_id = task.id

    app.dependency_overrides[get_current_user] = lambda: auth_user

    # 2. Act
    response = client.delete(f"/tasks/{task_id}")

    # 3. Assert
    assert response.status_code == 204 # No Content

    # Verificar se sumiu do banco
    task_db = db_session.query(Task).filter(Task.id == task_id).first()
    assert task_db is None

    app.dependency_overrides = {}

def test_list_subjects(client, db_session, auth_user):
    """
    Testa a listagem de disciplinas distintas.
    Cobre: Rota /tasks/subjects/list
    """
    # 1. Setup: Criar 3 tarefas com 2 disciplinas diferentes
    t1 = Task(title="T1", subject="Matemática", owner_id=auth_user.id)
    t2 = Task(title="T2", subject="Matemática", owner_id=auth_user.id) # Repetida
    t3 = Task(title="T3", subject="História", owner_id=auth_user.id)

    db_session.add_all([t1, t2, t3])
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: auth_user

    # 2. Act
    response = client.get("/tasks/subjects/list")

    # 3. Assert
    assert response.status_code == 200
    subjects = response.json()
    assert len(subjects) == 2 # Matemática e História
    assert "Matemática" in subjects
    assert "História" in subjects

    app.dependency_overrides = {}