"""Módulo de configuração da base de dados e gestão de sessões."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ==============================================================================
# MODO 2: AMBIENTE DE PRODUÇÃO (Remoto)
# Nota: Para rodar localmente sem configurar variáveis de ambiente,
# você pode descomentar o MODO 1 e comentar o MODO 2 temporariamente.
# ==============================================================================

try:
    from pydantic_settings import BaseSettings

    class Settings(BaseSettings):
        DATABASE_URL: str

        class Config:
            env_file = ".env"

    settings = Settings()
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
except (ImportError, ValueError):
    # Fallback para caso não tenha o .env configurado ou a lib instalada
    # Isso evita que o teste quebre antes mesmo de começar
    SQLALCHEMY_DATABASE_URL = "sqlite:///./studystreak.db"

# ==============================================================================

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # O argumento 'connect_args' é específico e necessário para o SQLite.
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()