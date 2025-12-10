# Análise de Gerenciamento de Memória

## 1. Ferramentas Utilizadas
Conforme exigido para Python, utilizou-se o módulo nativo **`tracemalloc`** para monitorar alocação de blocos de memória e **`time`** para medir impacto de processamento.

## 2. Otimização #1: Cache com Limite (LRU)

### Identificação
* **Módulo:** `app/services/score_service.py`
* **Função:** `calculate_task_points`
* **Problema:** Cálculos de pontuação são chamados milhares de vezes. Como a lógica é determinística (mesmo peso sempre gera mesmos pontos), reprocessar isso consome ciclos de CPU e alocação temporária desnecessária.

### Otimização Implementada
Aplicou-se o decorator `@lru_cache` (Least Recently Used) da biblioteca `functools`. Isso armazena os resultados das últimas 128 chamadas na memória.

**Código Antes:**
```python
def calculate_task_points(weight: int, ...):
    # Executa cálculo matemático toda vez
    return base_points * 10
```

**Código Depois (Otimizado):**
```python
@lru_cache(maxsize=128)
def calculate_task_points(weight: int, ...):
    # Retorna valor da memória se já foi calculado
    return base_points * 10
```

### Medição de Resultados
O teste simulou uma carga de regra de negócio ("Heavy Load") em 50.000 chamadas.

* **Tempo SEM Cache:** ~1.80s (Alto consumo de CPU devido ao reprocessamento)

* **Tempo COM Cache:** ~0.006s (Resposta quase instantânea)

* **Ganho de Performance:** A versão otimizada elimina o gargalo de CPU em chamadas repetitivas, ideal para cálculos determinísticos.

## 3. Otimização #2: Uso de Generators (Lazy Evaluation)

### Identificação
* **Módulo:** `app/utils/export.py` (Utilitário de Exportação).
* **Cenário:** Geração de relatórios CSV ou processamento em lote de grandes volumes de dados (`Task`).
* **Problema:** A abordagem tradicional utiliza listas (`list comprehension`) para formatar os dados. Isso força o Python a alocar memória para **todos** os registros simultaneamente ($O(N)$). Para grandes volumes (ex: 100.000 tarefas), isso causa picos de consumo de RAM que podem derrubar o servidor (*Out of Memory*).

### Otimização Implementada
Adoção de **Generators** utilizando a instrução `yield`.
Ao contrário das listas, os geradores não armazenam os dados na memória. Eles produzem um item por vez sob demanda ($O(1)$), descartando o anterior imediatamente.

**Código Antes (Lista - Consumo Alto):**
```python
# Aloca espaço para 100% dos itens na RAM antes de retornar
report_data = [f"{t.id},{t.title}\n" for t in all_tasks]
return report_data
```

**Código Depois (Generator - Consumo Baixo):**
```python
# Mantém apenas 1 item na RAM por vez
def export_tasks_csv(tasks_query):
    for task in tasks_query:
        yield f"{task.id},{task.title}\n"
```

### Medição de Resultados
Teste realizado simulando a exportação de 100.000 registros (Task).

* **Lista (Padrão)**: 6.75 MB
Crescimento linear ($O(N)$). Risco alto em produção

* **Generator (otimizado)**: 0.0006 MB
Consumo constante ($O(1)$). Uso de memória insignificante.

## 📊 Evidência de análise de memória

Abaixo, está documentado o print que evidencia a evolução (ANTES/DEPOIS) de dois módulos específicos, em questão de gerenciamento de memória:

![Resultados "ANTES/DEPOIS" de gerenciamento de memória](docs\assets\BPP_MEMORIA_ANTES_DEPOIS.png)