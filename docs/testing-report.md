# Relatório de Testes e Qualidade - StudyStreak API

## 1. Suite de Testes

### 1.1 Visão Geral
* **Framework Utilizado:** Pytest
* **Total de Testes:** 38 (Quase 4x o requisito de 10+)
    * 4 Testes Unitários (Lógica de Pontuação)
    * 2 Testes de Integração (Banco de Dados)
    * 6 Testes de API Tarefas (Sucesso + Erros)
    * 5 Testes de API Autenticação (Rotas)
    * 6 Testes de Segurança (Middleware/Bearer)
    * 5 Testes Unitários (Gamificação)
    * 2 Testes de API Usuários (Dashboard)
    * 8 Testes Unitários (Validação de Schemas)
* **Status:** ✅ Passing (100% Aprovado)
* **Tempo de Execução:** ~2.0s (Princípio FAST mantido)

### 1.2 Estrutura do Projeto
* `tests/unit/`: Testes isolados que não dependem do banco de dados (Regras de negócio e Schemas).
* `tests/integration/`: Testes que validam rotas da API e persistência no banco de dados.
* `tests/conftest.py`: Infraestrutura de testes com banco SQLite em memória e fixtures reutilizáveis.
* `tests/coverage-results/`: Relatórios HTML de cobertura.

### 1.3 Detalhamento da Suíte (Arquivos)

Abaixo, o escopo funcional de cada arquivo de teste implementado:

* **`tests/integration/test_auth.py`**:
    Valida o ciclo de vida da conta do usuário. Cobre o registro bem-sucedido, bloqueio de emails duplicados (Regra de Negócio), login com credenciais válidas e rejeição de senhas incorretas.

* **`tests/integration/test_auth_bearer.py`**:
    Testa a segurança e o middleware `JWTBearer`. Garante que rotas protegidas rejeitem requisições sem cabeçalho, com tokens malformados, expirados ou pertencentes a usuários deletados (Erro 401/403).

* **`tests/integration/test_badges.py`**:
    Verifica o motor de gamificação. Testa a inicialização das medalhas padrão no banco e as condições de gatilho para ganhar medalhas (1ª tarefa, 100 pontos, Streak de 3 dias), assegurando que o usuário não ganhe medalhas repetidas.

* **`tests/unit/test_score_service.py`**:
    Testes unitários puros da lógica matemática de pontuação. Valida cálculos de peso, penalidades por atraso (50%) e pontuação mínima, sem necessidade de conexão com o banco.

* **`tests/integration/test_score_service_db.py`**:
    Testes de integração do serviço de pontuação. Verifica se a função `process_task_completion` persiste corretamente os pontos no saldo do usuário, marca a tarefa como concluída e incrementa o contador de ofensiva (streak) no banco.

* **`tests/integration/test_tasks.py`**:
    Cobre o "Caminho Feliz" (Happy Path) do gerenciamento de tarefas. Valida a criação de tarefas vinculadas ao usuário logado e a listagem correta apenas das tarefas do proprietário.

* **`tests/integration/test_tasks_errors.py`**:
    Foca no tratamento de exceções e casos de borda das tarefas. Valida tentativas de completar tarefas já finalizadas (Erro 400), busca de tarefas inexistentes (Erro 404) e exclusão de registros.

* **`tests/integration/test_users.py`**:
    Valida os endpoints de leitura de dados do usuário. Testa a rota de perfil (`/me`) e a agregação de dados complexos do Dashboard (User + Tasks + Badges) para garantir que o JSON de resposta esteja estruturado corretamente.

* **`tests/unit/test_schemas.py`**:
    Testes unitários de validação de dados (Pydantic). Garante que regras de entrada — como tamanho mínimo de senha, limites de peso (1-10) e validação de campos obrigatórios — rejeitem dados inválidos antes mesmo de atingirem o banco de dados.

## 2. Cobertura de Código
*(Ver evolução detalhada em coverage-report.md)*

### 2.1 Métricas Finais (Snapshot)
| Módulo | Cobertura | Meta | Status |
| :--- | :---: | :---: | :--- |
| **PROJETO INTEIRO** | **92%** | **70%** | 🏆 Excelência |
| `routers/users.py` | 100% | 85% | ✅ |
| `models.py` | 100% | 100% | ✅ |
| `badge_service.py` | 97% | 85% | ✅ |
| `routers/auth.py` | 96% | 85% | ✅ |
| `schemas.py` | 96% | 85% | ✅ |
| `routers/tasks.py` | 90% | 70% | ✅ |
| `auth/auth_bearer.py`| 89% | 70% | ✅ |

## 3. Conclusão
A aplicação StudyStreak atingiu o estado da arte em qualidade de código para um MVP acadêmico. A cobertura de 92% assegura que praticamente todos os caminhos lógicos — do banco de dados à interface HTTP — foram verificados automaticamente.