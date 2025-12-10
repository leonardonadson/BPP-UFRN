# Registro de Depuração e Correção de Bugs

## Bug #1: Falha na Concessão de Badge na Contagem Exata

### 1. Identificação
* **Data:** 09/12/2025
* **Módulo:** `services/badge_service.py`
* **Severidade:** Média (Afeta a experiência de gamificação)

### 2. Descrição
Quando o usuário completa exatamente a quantidade de tarefas necessária para uma badge (ex: 10 tarefas para "Estudioso"), a badge não é concedida naquele momento. Ela só aparece após completar a tarefa seguinte (11ª).

### 3. Investigação
**Técnica Utilizada:** Debugger (Análise de Estado de Transação).

1. Coloquei um breakpoint em `badge_service.py` na linha que conta as tarefas: `completed_tasks_count = db.query(Task)...count()`.
2. Completei a 10ª tarefa via API.
3. O Debugger mostrou que `completed_tasks_count` retornou **9**, mesmo que a tarefa atual já estivesse marcada como `True` na memória Python.
4. Verifiquei em `database.py` que `autoflush=False`. Isso impede que o `SELECT COUNT` veja a alteração não commitada da tarefa atual.

### 4. Causa Raiz
Configuração de `autoflush=False` no SQLAlchemy combinada com uma query de leitura (`db.query`) executada dentro da mesma transação de escrita antes do flush explícito.

### 5. Correção
Forçar um `db.flush()` antes de verificar as badges para garantir que o banco "veja" a tarefa atual.

**Arquivo:** `app/services/score_service.py`

**Antes:**
```python
task.is_completed = True
points_earned = award_points_for_task(user, task, db)
streak_updated = update_user_streak(user, db)
badges_earned = check_and_award_badges(user, db) # Bug: Banco ainda vê tarefa como incompleta
```

**Depois:**
```python
task.is_completed = True
# ... (código intermediário)
db.flush()  # <--- CORREÇÃO: Sincroniza memória com transação do banco
badges_earned = check_and_award_badges(user, db)
```


### 6. Verificação
Teste manual: Ao completar a 10ª tarefa, a badge "Estudioso" foi retornada imediatamente na resposta JSON.


## Bug #2: Crash no Dashboard com Usuário Novo (Divisão por Zero)

### 1. Identificação
* **Data:** 09/12/2025
* **Módulo:** `app/routers/users.py`
* **Severidade:** Alta (Impede acesso ao Dashboard para novos usuários)

### 2. Descrição
Quando um usuário recém-cadastrado (sem tarefas) tenta acessar seu dashboard, a API retorna erro 500. Usuários com tarefas cadastradas conseguem acessar normalmente.

### 3. Investigação
**Técnica Utilizada:** Análise de Stack Trace.

1. Criei um usuário novo e imediatamente requisitei `GET /users/dashboard`.
2. A API retornou Status 500.
3. Analisei o Stack Trace no terminal do servidor:
   `File "users.py", line 25, in get_user_dashboard`
   `average = total_task_points / len(tasks)`
   `ZeroDivisionError: division by zero`
4. Identifiquei que o código tenta calcular uma média estatística dividindo pelo total de tarefas (`len(tasks)`), sem verificar se a lista está vazia.

### 4. Causa Raiz
Falta de tratamento para o caso de borda onde o divisor (número de tarefas) é zero.

### 5. Correção
Adicionar uma verificação condicional antes da divisão.

**Arquivo:** `app/routers/users.py`

**Antes:**
```python
total_task_points = sum(t.points_awarded for t in tasks)
average = total_task_points / len(tasks) # Crash se tasks for vazio
print(f"Média: {average}")
```

**Depois:**
```python
total_task_points = sum(t.points_awarded for t in tasks)
if len(tasks) > 0:
    average = total_task_points / len(tasks)
    print(f"Média: {average}")
else:
    print("Média: 0 (Sem tarefas)")
```

## Bug #3: Vulnerabilidade de DoS na Listagem (Limite Infinito)
### 1. Identificação
* **Data:** 09/12/2025
* **Módulo:** 'schemas.py'
* **Severidade:** Crítica (Potencial Negação de Serviço)

### 2. Descrição
É possível solicitar /tasks/?limit=1000000. O servidor tenta carregar todos os objetos na memória, causando lentidão ou travamento.

### 3. Investigação
**Técnica Utilizada:** Debugger (Análise de Estado de Transação).

1. Revisei o arquivo schemas.py.
2. Notei que limit: int = 100 é apenas um valor padrão. Não existe código impedindo que o usuário envie um valor maior.

### 4. Causa Raiz
ausência de validação de limite máximo (Upper Bound Constraint) no seu schema de entrada de dados.

### 5. Correção
A mesma correção do Bug #2 resolve este, limitando o máximo (le=100).

**Arquivo:** app/schemas.py

**Antes:**
```python
class TaskFilterParams(BaseModel):
    skip: int = 0
    limit: int = 100
```

**Depois:**
```python
from pydantic import Field

class TaskFilterParams(BaseModel):
    skip: int = Field(0, ge=0, description="Registros para pular")
    limit: int = Field(100, ge=1, le=100, description="Limite de registros")
```

## 📊 Evidência de análise de performance

Abaixo, estão documentados prints que evidenciam a resolução dos bugs encontrados no código não revisado:

![Resultados "ANTES/DEPOIS" de funções específicas da API](docs\assets)