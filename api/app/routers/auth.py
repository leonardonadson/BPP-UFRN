from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# CORREÇÃO: Importações alteradas para absolutas
from app.auth.auth_handler import create_access_token, get_password_hash, verify_password
from app.database import get_db
from app.models import User as UserModel
from app.schemas import Token, User, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])

def _validate_user_creation(user_data: UserCreate, db: Session):
    """Verifica se o email e o username já estão em uso."""
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe"
        )

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário após validar os dados."""
    _validate_user_creation(user, db)

    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Autentica um usuário e retorna token JWT"""
    user = db.query(UserModel).filter(UserModel.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
