# Conteúdo para: api/app/models.py (CORRIGIDO)

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    # CORREÇÃO: Removidos os parênteses de func.now()
    last_activity_date = Column(DateTime, default=func.now)
    created_at = Column(DateTime, default=func.now)

    tasks = relationship("Task", back_populates="owner")
    badges = relationship("UserBadge", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    subject = Column(String)
    weight = Column(Integer, default=1)
    due_date = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    points_awarded = Column(Integer, default=0)
    # CORREÇÃO: Removidos os parênteses de func.now()
    created_at = Column(DateTime, default=func.now)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")

class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    icon = Column(String)
    points_required = Column(Integer, default=0)
    tasks_required = Column(Integer, default=0)

    user_badges = relationship("UserBadge", back_populates="badge")

class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    # CORREÇÃO: Removidos os parênteses de func.now()
    earned_at = Column(DateTime, default=func.now)

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")