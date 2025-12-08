# tests/unit/test_tasks.py
from app.models import User, Task
from app.main import app
from app.auth.auth_bearer import get_current_user

def test_create_task(client, db_session):
    """
    Testa a rota POST /tasks/ (Criação de Tarefa).
    """
    # 1. ARRANGE
    user = User(email="taskmaster@example.com", username="taskmaster", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # [IMPORTANTE] Salvamos o ID aqui, enquanto a conexão com o banco ainda está viva!
    owner_id = user.id

    # 2. OVERRIDE
    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "title": "Aprender Pytest",
        "subject": "Qualidade",
        "weight": 5,
        "description": "Criar testes unitários para a API"
    }

    # 3. ACT: AQUI ACONTECE A MÁGICA
    # Quando o client.post roda, ele usa o banco e FECHA a conexão ao terminar.
    response = client.post("/tasks/", json=payload)

    # 4. ASSERT
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]

    # [IMPORTANTE] Aqui usamos a variável 'owner_id' (inteiro) e NÃO 'user.id' (objeto do banco)
    # Se usarmos user.id aqui, dá erro porque a conexão foi fechada no passo 3.
    assert data["owner_id"] == owner_id

    assert "id" in data

    # Limpeza
    app.dependency_overrides = {}

def test_list_tasks(client, db_session):
    """
    Testa a rota GET /tasks/ (Listagem).
    """
    # 1. ARRANGE
    user = User(email="listuser@example.com", username="listuser", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Salvamos o ID aqui também por segurança
    owner_id = user.id

    task = Task(title="Tarefa Existente", subject="DevOps", owner_id=owner_id, weight=3)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    # 2. OVERRIDE
    app.dependency_overrides[get_current_user] = lambda: user

    # 3. ACT
    response = client.get("/tasks/")

    # 4. ASSERT
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Tarefa Existente"

    app.dependency_overrides = {}