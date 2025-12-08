# tests/unit/test_auth.py
from app.models import User
from app.auth.auth_handler import get_password_hash, verify_password, create_access_token, decode_jwt

def test_register_user_success(client, db_session):
    """
    Testa o registro de um usuário com sucesso.
    Cobre: routers/auth.py (rota register) + models.py
    """
    payload = {
        "email": "novo@example.com",
        "username": "novousuario",
        "password": "senha123forte"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    # Verifica se a senha foi salva como hash no banco
    user_db = db_session.query(User).filter(User.email == payload["email"]).first()
    assert user_db is not None
    assert user_db.hashed_password != payload["password"]

def test_register_duplicate_email(client, db_session):
    """
    Testa o erro ao tentar registrar email duplicado.
    Cobre: Validação em routers/auth.py (_validate_user_creation)
    """
    # 1. Criar usuário existente
    user = User(email="duplicado@example.com", username="user1", hashed_password="123")
    db_session.add(user)
    db_session.commit()

    # 2. Tentar criar outro com mesmo email
    payload = {
        "email": "duplicado@example.com",
        "username": "user2",
        "password": "senha123"
    }
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email já cadastrado"

def test_login_success(client, db_session):
    """
    Testa o login com sucesso e geração de token.
    Cobre: routers/auth.py (login), auth_handler.py (verify_password, create_token)
    """
    # 1. Setup
    password = "minhasenha123"
    hashed = get_password_hash(password)
    user = User(email="login@example.com", username="loginuser", hashed_password=hashed)
    db_session.add(user)
    db_session.commit()

    # 2. Login
    payload = {"email": "login@example.com", "password": password}
    response = client.post("/auth/login", json=payload)

    # 3. Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Validar se o token gerado é real
    payload_token = decode_jwt(data["access_token"])
    assert payload_token["sub"] == str(user.id)

def test_login_wrong_password(client, db_session):
    """
    Testa login com senha errada.
    Cobre: auth_handler.py (verify_password falhando)
    """
    # 1. Setup
    hashed = get_password_hash("senha_certa")
    user = User(email="erro@example.com", username="errouser", hashed_password=hashed)
    db_session.add(user)
    db_session.commit()

    # 2. Tentativa com senha errada
    payload = {"email": "erro@example.com", "password": "senha_errada"}
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"

def test_auth_handler_direct(client):
    """
    Testa funções utilitárias do auth_handler diretamente para garantir 100% lá.
    """
    # Teste de hash
    pwd = "teste"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("errada", hashed) is False

    # Teste de token inválido
    assert decode_jwt("token_invalido_aleatorio") is None