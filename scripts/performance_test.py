# scripts/performance_test.py
import sys
import os
import cProfile
import pstats
import random
import string
from io import StringIO
from sqlalchemy.orm import joinedload

# Configuração de Caminho
sys.path.append(os.path.join(os.getcwd(), 'api'))

from app.database import SessionLocal, engine, Base
from app.models import User, Task

# ==========================================
# Configurações
# ==========================================
NUM_USERS = 1000
TASKS_PER_USER = 50
SEARCH_TERM = "Relatório Final"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def seed_database(db):
    print("--- 1. Verificando Banco de Dados ---")
    if db.query(User).count() >= NUM_USERS:
        print("Banco já populado. Pulando Seed.")
        return

    print(f"Gerando {NUM_USERS * TASKS_PER_USER} tarefas...")
    users = [User(email=f"u{i}_{generate_random_string()}@test.com", username=f"u{i}", hashed_password="123") for i in range(NUM_USERS)]
    db.add_all(users)
    db.commit()

    all_users = db.query(User).all()
    tasks = []
    for user in all_users:
        for _ in range(TASKS_PER_USER):
            title = generate_random_string(20)
            if random.random() < 0.01: title = f"Fazer {SEARCH_TERM} agora"
            tasks.append(Task(title=title, subject="DevOps", weight=1, owner_id=user.id))

    db.add_all(tasks)
    db.commit()
    print("Seed concluído.")

# --- GARGALO 1: Query Lenta (Database Bound) ---
def scenario_1_database_search(db):
    """
    Busca usando o motor do banco (SQL).
    O gargalo aqui é o I/O do banco (Full Table Scan se sem índice).
    """
    results = db.query(Task).filter(Task.title.ilike(f"%{SEARCH_TERM}%")).all()
    return len(results)

# --- GARGALO 2: Processamento Lento (CPU Bound) ---
def scenario_2_python_processing(db):
    """
    Busca TUDO do banco e filtra no Python usando um loop.
    Isso é extremamente ineficiente (muita memória e CPU).
    """
    # 1. Traz 50.000 objetos para a memória RAM (Lento!)
    all_tasks = db.query(Task).all()

    filtered_results = []
    # 2. Loop manual no Python (Lento!)
    for task in all_tasks:
        if SEARCH_TERM.lower() in task.title.lower():
            filtered_results.append(task)

    return len(filtered_results)

def run_profile(name, func, db):
    print(f"\n--- Analisando: {name} ---")
    profiler = cProfile.Profile()
    profiler.enable()
    count = func(db)
    profiler.disable()

    print(f"Itens encontrados: {count}")

    s = StringIO()
    # Ordena por 'tottime' para ver onde a CPU gastou mais tempo
    ps = pstats.Stats(profiler, stream=s).sort_stats('tottime')
    ps.print_stats(10) # Top 10 funções
    print(s.getvalue())

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)

        # Executa os dois cenários para comparação
        run_profile("Gargalo 1: Busca no Banco (SQL)", scenario_1_database_search, db)
        run_profile("Gargalo 2: Filtragem no Python (CPU)", scenario_2_python_processing, db)

    finally:
        db.close()

def scenario_3_n_plus_one_problem(db):
    """
    O Erro Clássico: Lazy Loading.
    Buscamos 1000 usuários (1 Query).
    Depois iteramos. Ao tocar em 'user.tasks', o ORM faz UMA NOVA QUERY por usuário.
    Total: 1001 Queries. Lento demais.
    """
    # 1. Busca todos os usuários (Query 1)
    users = db.query(User).all()

    total_tasks = 0
    for user in users:
        # PERIGO: Acessar .tasks aqui dispara uma query nova no banco para CADA usuário
        # Se temos 1000 usuários, faremos 1000 queries aqui dentro.
        total_tasks += len(user.tasks)

    return total_tasks

def scenario_3_optimized_eager_loading(db):
    """
    A Solução: Eager Loading (Joined Load).
    Avisamos ao ORM: "Vou precisar das tarefas, traga tudo junto num JOIN".
    Total: 1 Query (ou 2 dependendo da estratégia).
    """
    # Usamos options(joinedload(...)) para trazer tudo de uma vez
    users = db.query(User).options(joinedload(User.tasks)).all()

    total_tasks = 0
    for user in users:
        # Agora .tasks já está na memória. Zero queries aqui.
        total_tasks += len(user.tasks)

    return total_tasks

# ... (Mantenha a função run_profile igual) ...

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db) # Garante que temos dados

        # --- EXECUÇÃO DOS CENÁRIOS ---
        # run_profile("Gargalo 1...", scenario_1_database_search, db)
        # run_profile("Gargalo 2...", scenario_2_python_processing, db)

        # NOVOS CENÁRIOS
        run_profile("Gargalo 3: N+1 Selects (Lazy Loading)", scenario_3_n_plus_one_problem, db)
        run_profile("Gargalo 3: Eager Loading (Otimizado)", scenario_3_optimized_eager_loading, db)

    finally:
        db.close()