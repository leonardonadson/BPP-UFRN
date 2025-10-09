"""Módulo de configuração da base de dados e gestão de sessões."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MODO 1: AMBIENTE DE TESTES / QA (Local)
#SQLALCHEMY_DATABASE_URL = "sqlite:///./studystreak.db"
# ==============================================================================

 MODO 2: AMBIENTE DE PRODUÇÃO (Remoto)
 from pydantic_settings import BaseSettings

 class Settings(BaseSettings):
     DATABASE_URL: str

     class Config:
         env_file = ".env"

 settings = Settings()
 SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
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
