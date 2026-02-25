from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.auth_bearer import get_current_user
from app.database import get_db
from app.models import Subject as SubjectModel
from app.models import User
from app.schemas import Subject, SubjectCreate

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post("/", response_model=Subject, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova disciplina para o usuário"""
    # Verificar se já existe uma disciplina com o mesmo nome para este usuário
    existing = db.query(SubjectModel).filter(
        SubjectModel.owner_id == current_user.id,
        SubjectModel.name == subject.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disciplina com este nome já existe"
        )

    db_subject = SubjectModel(
        name=subject.name,
        owner_id=current_user.id
    )

    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)

    return db_subject


@router.get("/", response_model=List[Subject])
def list_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas as disciplinas do usuário"""
    subjects = db.query(SubjectModel).filter(
        SubjectModel.owner_id == current_user.id
    ).order_by(SubjectModel.name.asc()).all()

    return subjects


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deleta uma disciplina do usuário"""
    subject = db.query(SubjectModel).filter(
        SubjectModel.id == subject_id,
        SubjectModel.owner_id == current_user.id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )

    db.delete(subject)
    db.commit()
