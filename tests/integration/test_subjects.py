import pytest
from app.models import User, Subject
from app.main import app
from app.auth.auth_bearer import get_current_user


@pytest.fixture
def auth_user(db_session):
    user = User(email="subject_tester@example.com", username="subjecttester", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_create_subject(client, db_session, auth_user):
    """Testa a criação de uma disciplina."""
    owner_id = auth_user.id  # Salvar ID antes da chamada do client
    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.post("/subjects/", json={"name": "Cálculo I"})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Cálculo I"
    assert data["owner_id"] == owner_id
    assert "id" in data

    app.dependency_overrides = {}


def test_list_subjects(client, db_session, auth_user):
    """Testa a listagem de disciplinas."""
    s1 = Subject(name="Matemática", owner_id=auth_user.id)
    s2 = Subject(name="Física", owner_id=auth_user.id)
    db_session.add_all([s1, s2])
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.get("/subjects/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [s["name"] for s in data]
    assert "Matemática" in names or "Física" in names

    app.dependency_overrides = {}


def test_delete_subject(client, db_session, auth_user):
    """Testa a deleção de uma disciplina."""
    subject = Subject(name="Para Deletar", owner_id=auth_user.id)
    db_session.add(subject)
    db_session.commit()
    db_session.refresh(subject)
    subject_id = subject.id

    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.delete(f"/subjects/{subject_id}")

    assert response.status_code == 204

    deleted = db_session.query(Subject).filter(Subject.id == subject_id).first()
    assert deleted is None

    app.dependency_overrides = {}


def test_create_duplicate_subject(client, db_session, auth_user):
    """Testa erro ao criar disciplina com nome duplicado."""
    subject = Subject(name="Duplicada", owner_id=auth_user.id)
    db_session.add(subject)
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.post("/subjects/", json={"name": "Duplicada"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Disciplina com este nome já existe"

    app.dependency_overrides = {}


def test_delete_nonexistent_subject(client, auth_user):
    """Testa erro ao deletar disciplina que não existe."""
    app.dependency_overrides[get_current_user] = lambda: auth_user

    response = client.delete("/subjects/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Disciplina não encontrada"

    app.dependency_overrides = {}
