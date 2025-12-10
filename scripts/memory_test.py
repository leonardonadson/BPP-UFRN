import sys
import os
import tracemalloc
import time
from functools import lru_cache

# Configuração de Path
sys.path.append(os.path.join(os.getcwd(), 'api'))

# Importações Reais
from app.models import Task
from app.services.score_service import calculate_task_points

print("--- Iniciando Testes de Otimização (Memória e CPU) ---\n")

# ==============================================================================
# CENÁRIO 1: Otimização de CPU com LRU Cache
# Alvo: Simulação de Regra de Negócio Complexa em score_service.py
# ==============================================================================

def simulated_heavy_load():
    """
    Simula uma validação de regra de negócio mais complexa.
    Ex: Verificar se a data é feriado, calcular multiplicadores dinâmicos, etc.
    Isso consome CPU.
    """
    _ = [x**2 for x in range(500)] # Pequena carga matemática

# 1. Versão SEM Cache (Simulando Carga Real)
def calculate_standard(weight, on_time):
    simulated_heavy_load() # O sistema gasta tempo processando
    return calculate_task_points(weight, on_time)

# 2. Versão COM Cache (Otimizada)
@lru_cache(maxsize=128)
def calculate_cached(weight, on_time):
    simulated_heavy_load() # Na primeira vez processa... nas outras, PULA isso!
    return calculate_task_points(weight, on_time)

def test_cache_performance():
    print("[1] Testando Eficiência de Cache (LRU)...")

    iterations = 50_000

    # Teste A: Sem Cache
    start = time.time()
    for _ in range(iterations):
        calculate_standard(5, True)
        calculate_standard(3, False)
    duration_no_cache = time.time() - start

    # Teste B: Com Cache
    start = time.time()
    for _ in range(iterations):
        calculate_cached(5, True)
        calculate_cached(3, False)
    duration_cache = time.time() - start

    print(f"    Tempo SEM Cache: {duration_no_cache:.4f}s")
    print(f"    Tempo COM Cache: {duration_cache:.4f}s")
    print(f"    >>> Ganho de Performance: {duration_no_cache / duration_cache:.1f}x mais rápido")
    print("    (Cache eliminou o reprocessamento da regra de negócio)\n")

# ==============================================================================
# CENÁRIO 2: Otimização de RAM com Generators
# Alvo: Exportação de CSV (Mantido o sucesso anterior)
# ==============================================================================

def test_generator_memory():
    print("[2] Testando Eficiência de Memória (Generators)...")

    # Massa de dados: 100.000 tarefas
    large_dataset = [
        Task(id=i, title=f"Task {i}", points_awarded=10, is_completed=True)
        for i in range(100_000)
    ]

    tracemalloc.start()

    # Abordagem Ruim: Lista
    s1 = tracemalloc.take_snapshot()
    _ = [f"{t.id},{t.title}\n" for t in large_dataset]
    s2 = tracemalloc.take_snapshot()
    mem_list = s2.compare_to(s1, 'lineno')[0].size_diff / 1024 / 1024

    tracemalloc.stop()
    tracemalloc.start()

    # Abordagem Boa: Generator
    s1 = tracemalloc.take_snapshot()
    gen = (f"{t.id},{t.title}\n" for t in large_dataset)
    for _ in gen: pass # Consome
    s2 = tracemalloc.take_snapshot()
    mem_gen = s2.compare_to(s1, 'lineno')[0].size_diff / 1024 / 1024

    print(f"    Memória (Lista):     {mem_list:.2f} MiB")
    print(f"    Memória (Generator): {mem_gen:.4f} MiB")
    print(f"    >>> Economia de RAM: {(1 - (mem_gen/mem_list))*100:.1f}%")

if __name__ == "__main__":
    test_cache_performance()
    test_generator_memory()