# Análise de Desempenho e Otimização

## 1. Metodologia
Para garantir a escalabilidade do **StudyStreak**, foi realizada uma análise de desempenho focada nos gargalos de I/O (Banco de Dados) e CPU. Utilizou-se a biblioteca nativa `cProfile` para medição determinística.

* **Ambiente:** Local (SQLite).
* **Massa de Dados:** 500 Usuários, 50.000 Tarefas.
* **Ferramenta:** Script dedicado `scripts/performance_test.py`.

---

## 2. Gargalo #1: O Problema N+1 (Lazy Loading)

Este foi o gargalo mais crítico encontrado na aplicação, impactando diretamente a listagem de usuários e o dashboard.

### 🔍 Identificação
* **Módulo:** `app/routers/users.py` (simulado via script de teste)
* **Função Afetada:** Listagem de usuários acessando `.tasks`.
* **Problema:** O uso padrão do SQLAlchemy (Lazy Load) dispara uma nova query SQL para cada usuário listado para buscar suas tarefas. Em uma lista de 50 usuários, eram executadas 51 queries (1 para usuários + 50 para tarefas).
* **Complexidade:** $O(N)$ queries.

### 📊 Medição Inicial (Antes)
* **Tempo Total:** **44.381s** (para 100 iterações do teste).
* **Chamadas ao Banco:** 5.100 chamadas a `fetchall` (massivo overhead de rede/disco).

### 🛠️ Otimização Aplicada
* **Técnica:** **Eager Loading** (Carregamento Antecipado).
* **Descrição:** Utilização de `joinedload` para carregar usuários e tarefas em uma única query SQL usando `JOIN`.

**Código Antes (Implícito):**
```python
users = db.query(User).all()
for user in users:
    print(user.tasks) # Dispara query extra aqui
```

**Código Depois (Otimizado):**
```python
# Traz tudo em 1 Query
users = db.query(User).options(joinedload(User.tasks)).all()
```

### 📈 Medição Final (Depois)
* **Tempo Total:** 17.036s.
* **Ganho de Performance:** ~2.6x mais rápido (Redução de 61% no tempo).
* **Chamadas ao Banco:** Reduzidas drasticamente (o profile mostra apenas o overhead base do teste).

### ⚖️ Trade-offs
* **Memória:** O Eager Loading traz mais dados de uma vez para a RAM. Para listas gigantescas, deve ser combinado com paginação para evitar Out of Memory.


## 3. Gargalo #2: Agregação de Dados (Dashboard)
### 🔍 Identificação
* **Módulo:** app/routers/users.py

* **Função Afetada:** get_user_dashboard (Cálculo de pontos totais).

* **Problema:** A aplicação buscava todos os objetos de tarefa do banco de dados, serializava para objetos Python e somava os pontos na memória da aplicação (CPU Bound).

### 📊 Medição Inicial (Antes)
* **Tempo Total:** 0.680s.

* **Custo:** Alto consumo de memória para instanciar objetos Task apenas para ler um número inteiro (points_awarded).

### 🛠️ Otimização Aplicada
* **Técnica:** Database Aggregation (Push-down).

* **Descrição:** Delegação do cálculo matemático para o motor do banco de dados usando func.sum().

**Código Antes:**
```python
total = sum(t.points_awarded for t in tasks)
```

**Código Depois:**
```python
total = db.query(func.sum(Task.points_awarded)).filter(...).scalar()
```

### 📈 Medição Final (Depois)
* **Tempo Total:** 0.519s.

* **Ganho de Performance:** ~23% mais rápido.

* **Impacto Real:** Embora o ganho de tempo pareça modesto no SQLite local, a economia de Memória RAM é a principal vitória, pois deixamos de instanciar milhares de objetos desnecessários.

### ⚖️ Trade-offs
Cache: Ao somar direto no banco, perdemos a chance de ter os objetos "hidratados" na sessão do ORM para uso imediato posterior.


### 4. Gargalo #3: Contagem de Registros (Badges)

### 🔍 Identificação
* **Módulo:** app/services/badge_service.py

* **Cenário:** Verificar quantas tarefas o usuário completou.

* **Problema:** Comparação entre trazer todos os dados (.all()) versus contar no banco (.count()).

### 📊 Comparativo
* **Abordagem Ingênua (len(all)):** 0.489s.

* **Abordagem Otimizada (count):** 0.528s.

### 🧠 Análise do Resultado (Anomalia)
Neste teste específico com SQLite local, a versão otimizada teve um tempo técnico similar (ou levemente superior devido ao overhead de conexão do teste).
No entanto, a Complexidade de Memória é o fator decisivo:

* ***Ingênua:** $O(N)$ em memória (Carrega 50.000 linhas se o usuário tiver tudo isso).
* **Otimizada:** $O(1)$ em memória (Retorna sempre 1 número inteiro).
* **Conclusão:** Mantemos a otimização .count() pois ela previne o travamento do servidor (Crash) em cenários de produção com muitos dados, mesmo que o tempo de resposta em disco SSD local seja similar.

### ❌ Antes (Abordagem Ingênua - "Memory Hog")
Nesta abordagem, comum em códigos iniciantes, o ORM carrega todos os objetos do banco de dados para a memória RAM (hidratação de objetos) apenas para contar quantos itens existem na lista.

```python
# Traz TODOS os dados das tarefas (título, descrição, datas...) para a memória
all_completed_tasks = db.query(Task).filter(
    Task.owner_id == user.id,
    Task.is_completed == True
).all()

# O Python conta o tamanho da lista na memória
completed_tasks_count = len(all_completed_tasks)
```

### ✅ Depois (Abordagem Otimizada - Atual)
Esta é a versão atual do código. O SQLAlchemy instrui o banco de dados a fazer a contagem internamente e retornar apenas um número inteiro.

## 5. Análise do Gargalo #4: Carregamento de Relações (Lazy vs Eager Loading)

### Identificação
* **Arquivo:** `app/routers/users.py` (e acessos gerais via `models.py`)
* **Cenário:** Iterar sobre uma lista de usuários para processar suas tarefas (ex: relatórios administrativos ou validações em lote).
* **Problema:** O **Problema N+1**. O comportamento padrão do ORM (Lazy Loading) busca os usuários primeiro (1 Query) e, ao acessar `user.tasks` dentro de um loop, dispara uma **nova query separada** para cada usuário.

### Medição e Análise (Antes)
* **Tempo de Execução:** **44.381s** (para 100 repetições de carga).
* **Comportamento do Banco:** Foram registradas **5.100 chamadas** de execução SQL (`execute`).
* **Diagnóstico:** A latência de rede (round-trip) acumulada de milhares de queries pequenas destrói a performance, muito mais do que o volume de dados em si.

### Otimização Aplicada
* **Técnica:** **Eager Loading** (Carregamento Antecipado).
* **Implementação:** Instruir o SQLAlchemy a realizar um `JOIN` no banco de dados, trazendo o Usuário e suas Tarefas em uma única consulta SQL.

**Código Antes (Lazy - Lento):**
```python
# Dispara 1 Query para buscar usuários
users = db.query(User).limit(50).all()

for user in users:
    # GARGALO: Dispara +1 Query SQL a cada iteração do loop
    total_tasks = len(user.tasks)
 ```

**Código Depois (Eager - Otimizado):**
```python
from sqlalchemy.orm import joinedload

# Dispara APENAS 1 Query (LEFT JOIN users + tasks)
users = db.query(User).options(joinedload(User.tasks)).limit(50).all()

for user in users:
    # Acesso instantâneo (Dados já estão na memória RAM)
    total_tasks = len(user.tasks)
 ```

### 📈 Medição Final (Depois)
* **Tempo Total:** 17.036s.

* **Ganho de Performance:** ~2.6x mais rápido (Redução de 61% no tempo total).

* **Redução de I/O::** O número de queries caiu de $N+1$ para $1$, eliminando o overhead de conexão.

### ⚖️ Trade-offs
* **Consumo de Memória:** O Eager Loading carrega todos os dados relacionados para a memória da aplicação de uma só vez.

* **Risco:** Se um usuário tiver milhões de tarefas, trazê-las todas via joinedload pode causar Estouro de Memória (Out of Memory).

* **Mitigação:** Para relações muito grandes, deve-se evitar tanto o Lazy quanto o Eager loading puro, preferindo queries específicas com paginação.





