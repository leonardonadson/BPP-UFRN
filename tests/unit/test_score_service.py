# tests/unit/test_score_service.py
import pytest
from app.services.score_service import calculate_task_points

def test_calculate_points_on_time_standard_weight():
    """
    Testa o cálculo de pontos para uma tarefa entregue no prazo.
    Cenário: Peso 1, No Prazo.
    Resultado Esperado: 10 pontos (1 * 10).
    """
    # ARRANGE (Preparar)
    weight = 1
    on_time = True

    # ACT (Agir)
    points = calculate_task_points(weight, on_time)

    # ASSERT (Verificar)
    assert points == 10

def test_calculate_points_on_time_high_weight():
    """
    Testa o cálculo de pontos com peso maior.
    Cenário: Peso 5, No Prazo.
    Resultado Esperado: 50 pontos (5 * 10).
    """
    # ARRANGE
    weight = 5
    on_time = True

    # ACT
    points = calculate_task_points(weight, on_time)

    # ASSERT
    assert points == 50

def test_calculate_points_late_penalty():
    """
    Testa a penalidade para tarefa entregue com atraso.
    Cenário: Peso 4, Atrasada.
    Resultado Esperado: 20 pontos (metade de 40).
    """
    # ARRANGE
    weight = 4
    on_time = False

    # ACT
    points = calculate_task_points(weight, on_time)

    # ASSERT
    assert points == 20

def test_calculate_points_late_minimum_value():
    """
    Testa se a pontuação mínima é respeitada (Edge Case).
    Cenário: Peso 1, Atrasada.
    Cálculo: (1 * 10) / 2 = 5. O mínimo é 5.
    """
    # ARRANGE
    weight = 1
    on_time = False

    # ACT
    points = calculate_task_points(weight, on_time)

    # ASSERT
    assert points == 5