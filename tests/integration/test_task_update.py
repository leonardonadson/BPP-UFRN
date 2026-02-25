import pytest
from app.models import User, Task
from app.main import app
from app.auth.auth_bearer import get_current_user


@pytest.fixture
def auth_user(db_session):
    user = User(email="update_tester@example.com", username="updatetester", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_update_task(client, db_session, auth_user):
    """Testa a atualização de uma tarefa."""
    task = Task(title="Tarefa Original", subject="Matemática", owner_id=auth_user.id, weight=3)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    task_id = task.id

    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Tarefa Atualizada",
        "weight": 5
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Tarefa Atualizada"
    assert data["weight"] == 5
    assert data["subject"] == "Matemática"  # Campo não alterado permanece

    app.dependency_overrides = {}


def test_update_task_not_found(client, auth_user):
    """Testa erro ao tentar atualizar tarefa que não existe."""
    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.put("/tasks/9999", json={"title": "Não Existe"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada"

    app.dependency_overrides = {}


def test_update_task_all_fields(client, db_session, auth_user):
    """Testa a atualização de todos os campos de uma tarefa."""
    task = Task(title="Antes", subject="Física", owner_id=auth_user.id, weight=1)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    task_id = task.id

    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Depois",
        "description": "Descrição nova",
        "subject": "Química",
        "weight": 8,
        "due_date": "2026-06-15T23:59:00"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Depois"
    assert data["description"] == "Descrição nova"
    assert data["subject"] == "Química"
    assert data["weight"] == 8

    app.dependency_overrides = {}
