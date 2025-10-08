"""Módulo principal da aplicação FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, get_db
from app.models import Base
from app.routers import auth, tasks, users
from app.services.badge_service import initialize_badges

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyStreak API",
    description="API para gerenciamento de tarefas acadêmicas com gamificação",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://studystreak-ufrn.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)

@app.on_event("startup")
def startup_event():
    """Inicializa dados padrão na startup, como as badges."""
    db = next(get_db())
    initialize_badges(db)

@app.get("/")
def read_root():
    """Endpoint raiz da API."""
    return {
        "message": "StudyStreak API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    """Endpoint para verificação de saúde da API."""
    return {"status": "healthy", "message": "API está funcionando corretamente"}
