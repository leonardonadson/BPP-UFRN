from fastapi.testclient import TestClient
from app.main import app
from app.auth.auth_handler import create_access_token
from app.models import User

def test_auth_no_header(client):
    """
    Tenta acessar rota protegida sem enviar cabeçalho Authorization.
    Espera-se 401 Unauthorized.
    """
    response = client.get("/users/me")
    assert response.status_code == 401

def test_auth_invalid_header_scheme(client):
    """
    Envia cabeçalho com esquema errado (Basic ao invés de Bearer).
    """
    headers = {"Authorization": "Basic token_valido"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401

def test_auth_invalid_token(client):
    """
    Tenta acessar com um token Bearer totalmente inválido.
    """
    headers = {"Authorization": "Bearer token_falso_123"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401  # Atualizado de 403 para 401

def test_auth_user_not_found(client, db_session):
    """
    Cenário raro: O token é válido, mas o usuário foi deletado do banco.
    """
    # 1. Criar usuário e gerar token real
    user = User(email="fantasma@test.com", username="fantasma", hashed_password="123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    # 2. DELETAR o usuário do banco
    db_session.delete(user)
    db_session.commit()

    # 3. Tentar acessar com o token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)

    # Atualizado de 404 para 401 (Por segurança, não revelamos que o ID existia)
    assert response.status_code == 401

def test_auth_token_sub_missing(client):
    """
    Testa token válido (assinatura ok) mas sem o campo 'sub'.
    """
    token = create_access_token({"data": "nada"}) # Payload sem 'sub'

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 401 # Atualizado de 403 para 401

def test_auth_token_sub_invalid_format(client):
    """
    Testa token onde 'sub' não é um número inteiro.
    """
    token = create_access_token({"sub": "nao_sou_um_id"})

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)

    assert response.status_code == 401 # Atualizado de 403 para 401