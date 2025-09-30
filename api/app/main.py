from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base
from .routers import auth, tasks, users
from .services.badge_service import initialize_badges

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyStreak API",
    description="API para gerenciamento de tarefas acadêmicas com gamificação",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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
    db = next(get_db())
    initialize_badges(db)

@app.get("/")
def read_root():
    return {
        "message": "StudyStreak API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API está funcionando corretamente"}
