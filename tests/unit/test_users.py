# tests/unit/test_users.py
from app.models import User, Task, Badge, UserBadge
from app.main import app
from app.auth.auth_bearer import get_current_user

def test_read_users_me(client, db_session):
    """
    Testa a rota GET /users/me (Perfil do Usuário).
    """
    # 1. Setup
    user = User(email="me@example.com", username="me_user", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Override Auth
    app.dependency_overrides[get_current_user] = lambda: user

    # 3. Act
    response = client.get("/users/me")

    # 4. Assert
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "me_user"
    assert "id" in data

    # Limpeza
    app.dependency_overrides = {}

def test_read_user_dashboard(client, db_session):
    """
    Testa a rota GET /users/dashboard.
    Verifica se retorna o usuário, suas tarefas e suas badges.
    """
    # 1. ARRANGE: Criar um cenário completo
    user = User(email="dash@example.com", username="dash_user", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id

    # Adicionar uma tarefa
    task = Task(title="Tarefa Dash", subject="Test", owner_id=user_id)
    db_session.add(task)

    # Adicionar uma Badge e dar para o usuário
    badge = Badge(name="Dash Badge", description="Teste", icon="🧪")
    db_session.add(badge)
    db_session.commit()

    user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
    db_session.add(user_badge)
    db_session.commit()

    # 2. Override Auth
    app.dependency_overrides[get_current_user] = lambda: user

    # 3. ACT
    response = client.get("/users/dashboard")

    # 4. ASSERT
    assert response.status_code == 200
    data = response.json()

    # Verifica estrutura do UserDashboard
    assert "user" in data
    assert "tasks" in data
    assert "badges" in data

    # Verifica conteúdo
    assert data["user"]["email"] == "dash@example.com"
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Tarefa Dash"
    assert len(data["badges"]) == 1
    assert data["badges"][0]["badge"]["name"] == "Dash Badge"

    app.dependency_overrides = {}