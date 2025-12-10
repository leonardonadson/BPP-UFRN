from typing import Iterator
from app.models import Task

def export_tasks_generator(tasks: list[Task]) -> Iterator[str]:
    """
    [OTIMIZAÇÃO DE MEMÓRIA]
    Gera linhas formatadas para relatório sob demanda.
    Substitui a criação de uma lista gigante de strings na memória.
    """
    yield "ID,Title,Points,Status\n"  # Cabeçalho

    for task in tasks:
        status = "Completed" if task.is_completed else "Pending"
        # O 'yield' retorna a string e libera a memória dela imediatamente após o uso
        yield f"{task.id},{task.title},{task.points_awarded},{status}\n"