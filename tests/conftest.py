# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importações do seu projeto (ajuste se necessário)
from app.database import Base, get_db
from app.main import app

# 1. Configuração do Banco de Dados de Teste
# Usamos SQLite em memória (:memory:) porque é extremamente rápido
# e garante que os dados sejam apagados após cada teste.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # StaticPool é crucial para testes em memória funcionarem bem
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Fixture da Sessão do Banco (db_session)
# Esta fixture cria as tabelas antes do teste e as destrói depois.
# Garante o princípio "Independent" (Isolamento).
@pytest.fixture(scope="function")
def db_session():
    # Cria todas as tabelas no banco em memória
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Destrói as tabelas para o próximo teste começar limpo
        Base.metadata.drop_all(bind=engine)

# 3. Fixture do Cliente (client)
# Simula o navegador/Postman. Intercepta a dependência 'get_db'
# para usar o nosso banco de teste em vez do banco real.
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Substitui a dependência original do app pela nossa de teste
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Limpa a substituição após o teste
    app.dependency_overrides.clear()