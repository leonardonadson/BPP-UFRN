# tests/unit/test_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas import UserCreate, TaskCreate, UserLogin

def test_user_create_valid():
    """Testa criação de usuário com dados válidos."""
    user = UserCreate(email="valid@test.com", username="validuser", password="securepassword")
    assert user.email == "valid@test.com"
    assert user.username == "validuser"

def test_user_password_too_short():
    """Testa se a senha curta lança erro."""
    with pytest.raises(ValidationError) as exc:
        UserCreate(email="test@test.com", username="user", password="123")

    # Verifica se a mensagem de erro contém o texto esperado
    assert "A senha deve ter pelo menos 6 caracteres" in str(exc.value)

def test_user_username_too_short():
    """Testa validação de tamanho de username."""
    with pytest.raises(ValidationError) as exc:
        UserCreate(email="test@test.com", username="oi", password="securepassword")
    assert "O nome de usuário deve ter pelo menos 3 caracteres" in str(exc.value)

def test_task_create_valid():
    """Testa criação de tarefa válida."""
    task = TaskCreate(title="Valid Task", subject="Math", weight=5)
    assert task.weight == 5

def test_task_weight_validation():
    """Testa limites do peso da tarefa (1-10)."""
    # Teste peso < 1
    with pytest.raises(ValidationError) as exc:
        TaskCreate(title="Task", subject="Math", weight=0)
    assert "O peso deve estar entre 1 e 10" in str(exc.value)

    # Teste peso > 10
    with pytest.raises(ValidationError) as exc:
        TaskCreate(title="Task", subject="Math", weight=11)
    assert "O peso deve estar entre 1 e 10" in str(exc.value)

def test_task_title_validation():
    """Testa validação de título."""
    # Título vazio ou muito curto
    with pytest.raises(ValidationError) as exc:
        TaskCreate(title="  ", subject="Math")
    assert "O título deve ter pelo menos 3 caracteres" in str(exc.value)

def test_task_description_too_long():
    """Testa descrição muito longa (> 1000 chars)."""
    long_desc = "a" * 1001
    with pytest.raises(ValidationError) as exc:
        TaskCreate(title="Task", subject="Math", description=long_desc)
    assert "A descrição não pode ter mais de 1000 caracteres" in str(exc.value)

def test_user_login_password_required():
    """Testa login com senha vazia."""
    with pytest.raises(ValidationError) as exc:
        UserLogin(email="test@test.com", password="")
    assert "A senha é obrigatória" in str(exc.value)