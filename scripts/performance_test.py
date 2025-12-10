import sys
import os
import cProfile
import pstats
import random
import string
from io import StringIO
from sqlalchemy.orm import joinedload
from sqlalchemy import func

# Configuração de Caminho para importar seus arquivos reais
sys.path.append(os.path.join(os.getcwd(), 'api'))

from app.database import SessionLocal, engine, Base
from app.models import User, Task, Badge

# ==========================================
# Configurações & Seed (Mantido igual)
# ==========================================
NUM_USERS = 500
TASKS_PER_USER = 100 # Aumentei para pesar mais na soma

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def seed_database(db):
    print("--- Verificando/Gerando Massa de Dados ---")
    if db.query(User).count() >= NUM_USERS:
        print("Banco populado. Pulando seed.")
        return

    print("Gerando usuários e tarefas...")
    users = [User(email=f"user{i}_{generate_random_string()}@test.com", username=f"u{i}", hashed_password="123") for i in range(NUM_USERS)]
    db.add_all(users)
    db.commit()

    all_users = db.query(User).all()
    tasks = []
    for user in all_users:
        for _ in range(TASKS_PER_USER):
            tasks.append(Task(
                title=generate_random_string(20),
                subject="Math",
                weight=random.randint(1, 10), # Pontos aleatórios para somar
                points_awarded=random.randint(1, 100),
                owner_id=user.id,
                is_completed=True
            ))
    db.add_all(tasks)
    db.commit()
    print("Seed concluído.")

# ==========================================
# GARGALO 1: Soma de Pontos (Dashboard)
# Referência: app/routers/users.py
# ==========================================
def scenario_1_dashboard_sum_python(db):
    """Simula: users.py -> sum(t.points_awarded for t in tasks)"""
    user = db.query(User).first()
    # Traz tarefas para a RAM
    tasks = db.query(Task).filter(Task.owner_id == user.id).all()
    # Soma no Python
    total = sum(t.points_awarded for t in tasks)
    return total

def scenario_1_dashboard_sum_sql(db):
    """Otimização: Soma direto no SQL"""
    user = db.query(User).first()
    # Soma no Banco
    total = db.query(func.sum(Task.points_awarded)).filter(Task.owner_id == user.id).scalar()
    return total or 0

# ==========================================
# GARGALO 2: Verificação de Badges
# Referência: app/services/badge_service.py
# ==========================================
def scenario_2_badges_len_all(db):
    """Simula versão ruim: len(query.all())"""
    user = db.query(User).first()
    # Traz objetos pesados para contar
    tasks = db.query(Task).filter(Task.owner_id == user.id, Task.is_completed == True).all()
    return len(tasks)

def scenario_2_badges_count_sql(db):
    """Simula sua versão atual: query.count()"""
    user = db.query(User).first()
    # Conta no banco
    count = db.query(Task).filter(Task.owner_id == user.id, Task.is_completed == True).count()
    return count

# ==========================================
# GARGALO 3: Paginação (tasks.py)
# Teste de Offset Pagination
# ==========================================
def scenario_3_pagination_shallow(db):
    """Página 1: skip=0 (Rápido)"""
    # Simula: list_tasks(filters=TaskFilterParams(skip=0, limit=10))
    return db.query(Task).limit(10).all()

def scenario_3_pagination_deep(db):
    """Página 500: skip=5000 (Lento - O Banco lê e descarta 5k linhas)"""
    # Simula: list_tasks(filters=TaskFilterParams(skip=5000, limit=10))
    return db.query(Task).offset(5000).limit(10).all()

# ==========================================
# GARGALO 4: Carregamento de Relações (users.py)
# Lazy Load vs Eager Load
# ==========================================
def scenario_4_lazy_loading(db):
    """Simula o atual users.py: Acessar .tasks depois de carregar user"""
    # 1. Carrega usuários (simula get_current_user)
    users = db.query(User).limit(50).all()
    count = 0
    for user in users:
        # GARGALO: O SQLAlchemy faz 1 query extra AQUI para cada usuário
        count += len(user.tasks)
    return count

def scenario_4_eager_loading(db):
    """Otimização: Carregar user JÁ com as tasks (JOIN)"""
    # 1. Carrega usuários COM as tarefas (1 Query só com JOIN)
    users = db.query(User).options(joinedload(User.tasks)).limit(50).all()
    count = 0
    for user in users:
        # Zero custo: dados já estão na memória
        count += len(user.tasks)
    return count

# ==========================================
# Execução
# ==========================================
def run_profile(name, func, db):
    print(f"\n--- Analisando: {name} ---")
    profiler = cProfile.Profile()
    profiler.enable()
    # Rodamos 100 vezes para o gargalo ficar visível, já que o SQLite é muito rápido
    for _ in range(100):
        func(db)
    profiler.disable()

    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('tottime')
    ps.print_stats(5)
    print(s.getvalue())

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)

        # Dashboard: Python vs SQL Sum
        run_profile("Gargalo 1: Soma Python (users.py)", scenario_1_dashboard_sum_python, db)
        run_profile("Gargalo 1: Soma SQL (Otimizado)", scenario_1_dashboard_sum_sql, db)

        # Badges: Len vs Count
        run_profile("Gargalo 2: Listar Tudo (Bad Practice)", scenario_2_badges_len_all, db)
        run_profile("Gargalo 2: SQL Count (badge_service.py)", scenario_2_badges_count_sql, db)

        # Paginação
        run_profile("Gargalo 3: Paginação Inicial (skip=0)", scenario_3_pagination_shallow, db)
        run_profile("Gargalo 3: Paginação Profunda (skip=5000)", scenario_3_pagination_deep, db)

        # Lazy vs Eager
        run_profile("Gargalo 4: Lazy Loading (users.py atual)", scenario_4_lazy_loading, db)
        run_profile("Gargalo 4: Eager Loading (Otimizado)", scenario_4_eager_loading, db)

    finally:
        db.close()