from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base
from .routers import auth, tasks, users
from .services.badge_service import initialize_badges

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyStreak API",
    description="API para gerenciamento de tarefas acadêmicas com gamificação",
    version="1.0.0"
)

# Incluir routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)

@app.on_event("startup")
def startup_event():
    """Inicializa dados padrão na startup"""
    db = next(get_db())
    initialize_badges(db)

@app.get("/")
def read_root():
    """Endpoint raiz da API"""
    return {
        "message": "StudyStreak API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    """Endpoint para verificação de saúde da API"""
    return {"status": "healthy", "message": "API está funcionando corretamente"}
