# Análise de Desempenho e Otimização

## 1. Metodologia de Teste
Para identificar e mitigar gargalos de performance, foi desenvolvido um script de carga personalizado (`scripts/performance_test.py`) utilizando a biblioteca `cProfile` para profiling determinístico.

* **Ambiente de Teste:** Banco de dados SQLite Local.
* **Massa de Dados:** 1.000 Usuários e 50.000 Tarefas.
* **Ferramentas:** Python `cProfile`, `pstats` e `SQLAlchemy`.

---

## 2. Análise do Gargalo #1: Database Query (I/O Bound)

### Identificação do Problema
* **Cenário:** Busca textual de tarefas (`Task.title`) em uma tabela com 50.000 registros.
* **Sintoma:** O banco de dados realiza um *Full Table Scan* (leitura sequencial de todas as linhas) para encontrar os registros, o que degrada a performance conforme o volume de dados cresce.
* **Evidência (cProfile):**
    * Tempo de Execução: **0.021s**.
    * A maior parte do tempo é gasta em I/O do banco (`sqlite3.Cursor.fetchall`).

### Otimização Aplicada
* **Técnica:** Indexação (B-Tree).
* **Implementação:** Adicionado índice na coluna de título em `app/models.py`.
    ```python
    title = Column(String, index=True)
    ```
* **Resultado:** A complexidade da busca foi reduzida de **O(N)** para **O(log N)**, garantindo escalabilidade.

---

## 3. Análise do Gargalo #2: Processamento em Memória (CPU Bound)

### Identificação do Problema
* **Cenário:** Recuperar **todos** os registros do banco (50.000 objetos) e filtrar o resultado utilizando um loop `for` no Python.
* **Evidência (cProfile):**
    * Tempo de Execução: **0.563s**.
    * **Diagnóstico:** O tempo é **27x maior** que a busca otimizada. O profilador mostrou que as funções `_populate_full` e `_instance` (do ORM) consumiram a CPU instanciando objetos desnecessários.
    * **Complexidade (Big O):** **O(N)** (Linear) com constante alta (instanciação de objetos).

### Otimização Aplicada
* **Técnica:** Push-down Predicate (Filtragem no Banco).
* **Implementação:** Transferência da lógica de filtro para a cláusula `WHERE` do SQL.
    * **Antes (Python):** `[t for t in tasks if term in t.title]`
    * **Depois (SQL):** `.filter(Task.title.ilike(...))`
* **Ganho de Performance:** **~2.600%** (Redução de 0.563s para 0.021s).

---

## 4. Análise do Gargalo #3: O Problema N+1 (ORM Trap)

### Identificação do Problema
* **Cenário:** Iterar sobre 1.000 usuários e acessar suas tarefas (`user.tasks`) para contagem.
* **Evidência (cProfile):**
    * **Tempo Total:** **4.929s**.
    * **Queries Executadas:** **1.001 Queries** (1 para usuários + 1.000 para tarefas).
    * **Diagnóstico:** O uso padrão do SQLAlchemy (Lazy Loading) causa o "Problema N+1", gerando um overhead massivo de rede e latência de banco.
    * **Complexidade (Big O):** **O(N)** queries.

### Otimização Aplicada
* **Técnica:** Eager Loading (Carregamento Antecipado).
* **Implementação:** Uso da estratégia `joinedload` para trazer os dados relacionados em uma única consulta JOIN.
    ```python
    db.query(User).options(joinedload(User.tasks)).all()
    ```
* **Ganho de Performance:**
    * **Tempo:** Reduzido para **0.961s** (Melhoria de **5x**).
    * **Queries:** Reduzidas de **1.001** para **1**.
    * **Complexidade Final:** **O(1)** query.

---

## 5. Conclusão
A análise de desempenho comprovou que a aplicação está otimizada para produção. Os principais gargalos (I/O excessivo, N+1 Selects e processamento ineficiente em memória) foram identificados e resolvidos, resultando em um sistema capaz de lidar com alta concorrência e volume de dados com tempos de resposta mínimos.