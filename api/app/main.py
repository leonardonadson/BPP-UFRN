"""Módulo principal da aplicação FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, get_db
from app.models import Base, Subject as SubjectModel, Task as TaskModel
from app.routers import auth, subjects, tasks, users
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
app.include_router(subjects.router)

@app.on_event("startup")
def startup_event():
    """Inicializa dados padrão na startup, como as badges."""
    db = next(get_db())
    initialize_badges(db)
    migrate_subjects(db)

def migrate_subjects(db):
    """
    Migração: garante que todas as tarefas tenham disciplina
    e cria registros Subject a partir dos dados existentes.
    """
    from sqlalchemy import or_

    # 1. Atribuir "Geral" a tarefas sem disciplina
    tasks_without_subject = db.query(TaskModel).filter(
        or_(TaskModel.subject == None, TaskModel.subject == "")  # noqa: E711
    ).all()

    for task in tasks_without_subject:
        task.subject = "Geral"

    if tasks_without_subject:
        db.commit()

    # 2. Criar registros Subject a partir dos subjects distintos das tarefas
    # Agrupa por (owner_id, subject) para criar disciplinas por usuário
    distinct_subjects = db.query(
        TaskModel.owner_id, TaskModel.subject
    ).filter(
        TaskModel.subject.isnot(None),
        TaskModel.subject != ""
    ).distinct().all()

    for owner_id, subject_name in distinct_subjects:
        existing = db.query(SubjectModel).filter(
            SubjectModel.owner_id == owner_id,
            SubjectModel.name == subject_name
        ).first()

        if not existing:
            db_subject = SubjectModel(name=subject_name, owner_id=owner_id)
            db.add(db_subject)

    db.commit()

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
