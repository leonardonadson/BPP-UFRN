# Documentação da API - StudyStreak

Esta documentação detalha todas as rotas da API backend (FastAPI) para nortear o desenvolvimento das telas e integrações no aplicativo mobile.

## URL Base
Presumivelmente configurada como `http://localhost:8000` (desenvolvimento local) ou a URL de produção.

---

## 1. Autenticação (`/auth`)
Rotas para registro e login de usuários. Nenhuma destas rotas requer autenticação prévia (token).

### 1.1 Registrar Usuário
- **Rota:** `POST /auth/register`
- **Descrição:** Cria um novo usuário na do sistema.
- **Parâmetros de Entrada (Body JSON):**
  ```json
  {
    "email": "string (formato de email válido)",
    "username": "string (3 a 50 caracteres)",
    "password": "string (6 a 72 caracteres)"
  }
  ```
- **Resposta de Sucesso (201 Created):**
  ```json
  {
    "email": "string",
    "username": "string",
    "id": int,
    "total_points": int,
    "current_streak": int,
    "last_activity_date": "string (ISO 8601 datetime) ou null",
    "created_at": "string (ISO 8601 datetime)"
  }
  ```
- **Respostas de Erro:**
  - `400 Bad Request`: "Email já cadastrado" ou "Nome de usuário já existe".

### 1.2 Login de Usuário
- **Rota:** `POST /auth/login`
- **Descrição:** Autentica o usuário e retorna o token JWT para acesso às rotas protegidas.
- **Parâmetros de Entrada (Body JSON):**
  ```json
  {
    "email": "string (formato de email válido)",
    "password": "string"
  }
  ```
- **Resposta de Sucesso (200 OK):**
  ```json
  {
    "access_token": "string (JWT)",
    "token_type": "bearer"
  }
  ```
- **Respostas de Erro:**
  - `401 Unauthorized`: "Credenciais inválidas".

---

## 2. Usuários (`/users`)
Rotas relacionadas aos dados do usuário logado. **Requer Token JWT (`Authorization: Bearer <token>`)** em todas as rotas.

### 2.1 Obter Dados do Usuário Atual (Me)
- **Rota:** `GET /users/me`
- **Descrição:** Retorna as informações básicas do usuário logado.
- **Parâmetros:** Nenhum.
- **Resposta de Sucesso (200 OK):**
  ```json
  {
    "email": "string",
    "username": "string",
    "id": int,
    "total_points": int,
    "current_streak": int,
    "last_activity_date": "string (ISO 8601 datetime) ou null",
    "created_at": "string (ISO 8601 datetime)"
  }
  ```

### 2.2 Obter Dashboard do Usuário
- **Rota:** `GET /users/dashboard`
- **Descrição:** Retorna os dados completos do dashboard do usuário, incluindo suas tarefas e badges conquistadas.
- **Parâmetros:** Nenhum.
- **Resposta de Sucesso (200 OK):**
  ```json
  {
    "user": {
      "email": "string",
      "username": "string",
      "id": int,
      "total_points": int,
      "current_streak": int,
      "last_activity_date": "string ou null",
      "created_at": "string"
    },
    "tasks": [
      {
        "id": int,
        "title": "string",
        "description": "string ou null",
        "subject": "string",
        "weight": int,
        "due_date": "string ou null",
        "is_completed": boolean,
        "completed_at": "string ou null",
        "points_awarded": int,
        "created_at": "string",
        "owner_id": int
      }
    ],
    "badges": [
      {
        "badge": {
          "id": int,
          "name": "string",
          "description": "string",
          "icon": "string",
          "points_required": int,
          "tasks_required": int
        },
        "earned_at": "string (ISO 8601 datetime)"
      }
    ]
  }
  ```

### 2.3 Editar Perfil do Usuário
- **Rota:** `PUT /users/me`
- **Descrição:** Permite que o usuário logado edite seus próprios dados (atualização parcial).
- **Parâmetros de Entrada (Body JSON, todos opcionais):**
  ```json
  {
    "email": "string",
    "username": "string (3 a 50 caracteres)",
    "password": "string (6 a 72 caracteres)"
  }
  ```
- **Resposta de Sucesso (200 OK):** Retorna o objeto do usuário atualizado.
- **Respostas de Erro:**
  - `400 Bad Request`: "Email já cadastrado para outro usuário" ou "Nome de usuário já existe".

### 2.4 Excluir Conta do Usuário
- **Rota:** `DELETE /users/me`
- **Descrição:** Exclui a conta do usuário logado e todos os dados em cascata (tarefas, disciplinas e badges).
- **Parâmetros:** Nenhum.
- **Resposta de Sucesso:** `204 No Content` (sem corpo na resposta).

---

## 3. Disciplinas / Matérias (`/subjects`)
Gerenciamento de disciplinas do usuário. **Requer Token JWT**.

### 3.1 Listar Disciplinas
- **Rota:** `GET /subjects/`
- **Descrição:** Retorna a lista de todas as disciplinas cadastradas pelo usuário.
- **Parâmetros:** Nenhum.
- **Resposta de Sucesso (200 OK):** Lista de objetos disciplina.
  ```json
  [
    {
      "name": "string",
      "id": int,
      "created_at": "string",
      "owner_id": int
    }
  ]
  ```

### 3.2 Criar Disciplina
- **Rota:** `POST /subjects/`
- **Descrição:** Cria uma nova disciplina para o usuário logado.
- **Parâmetros de Entrada (Body JSON):**
  ```json
  {
    "name": "string (2 a 100 caracteres)"
  }
  ```
- **Resposta de Sucesso (201 Created):**
  ```json
  {
    "name": "string",
    "id": int,
    "created_at": "string",
    "owner_id": int
  }
  ```
- **Respostas de Erro:**
  - `400 Bad Request`: "Disciplina com este nome já existe".

### 3.3 Editar Disciplina
- **Rota:** `PUT /subjects/{subject_id}`
- **Descrição:** Renomeia uma disciplina já existente.
- **Parâmetros de Path:** `subject_id` (inteiro).
- **Parâmetros de Entrada (Body JSON):**
  ```json
  {
    "name": "string (2 a 100 caracteres)"
  }
  ```
- **Resposta de Sucesso (200 OK):** Retorna o objeto da disciplina atualizada.
- **Respostas de Erro:**
  - `404 Not Found`: "Disciplina não encontrada".
  - `400 Bad Request`: "Disciplina com este nome já existe".

### 3.4 Deletar Disciplina
- **Rota:** `DELETE /subjects/{subject_id}`
- **Descrição:** Exclui uma disciplina específica.
- **Parâmetros de Path:** `subject_id` (inteiro).
- **Resposta de Sucesso:** `204 No Content` (sem corpo na resposta).
- **Respostas de Erro:**
  - `404 Not Found`: "Disciplina não encontrada".

---

## 4. Tarefas (`/tasks`)
Gerenciamento de tarefas (Tasks). **Requer Token JWT**.

### 4.1 Listar Tarefas
- **Rota:** `GET /tasks/`
- **Descrição:** Retorna a lista de tarefas do usuário, suportando paginação e filtros.
- **Parâmetros de Query (Opcionais):**
  - `skip` (int, default: 0): Quantos registros pular.
  - `limit` (int, default: 100, max: 100): Limite de registros a retornar.
  - `completed` (boolean): Filtrar apenas concluídas (`true`) ou pendentes (`false`).
  - `subject` (string): Filtrar tarefas por nome de uma disciplina específica.
- **Resposta de Sucesso (200 OK):** Lista de tarefas.
  ```json
  [
    {
      "id": int,
      "title": "string",
      "description": "string ou null",
      "subject": "string",
      "weight": int,
      "due_date": "string (ISO 8601) ou null",
      "is_completed": boolean,
      "completed_at": "string ou null",
      "points_awarded": int,
      "created_at": "string",
      "owner_id": int
    }
  ]
  ```

### 4.2 Criar Tarefa
- **Rota:** `POST /tasks/`
- **Descrição:** Cria uma nova tarefa.
- **Parâmetros de Entrada (Body JSON):**
  ```json
  {
    "title": "string (3 a 200 caracteres)",
    "description": "string (até 1000 caracteres) ou null",
    "subject": "string (2 a 100 caracteres)",
    "weight": int (1 a 10, default: 1),
    "due_date": "string (ISO 8601 datetime, opcional)"
  }
  ```
- **Resposta de Sucesso (201 Created):** Retorna o objeto da tarefa criada.

### 4.3 Obter Tarefa por ID
- **Rota:** `GET /tasks/{task_id}`
- **Descrição:** Retorna os detalhes de uma tarefa específica.
- **Parâmetros de Path:** `task_id` (inteiro).
- **Resposta de Sucesso (200 OK):** O objeto da tarefa buscada.
- **Respostas de Erro:**
  - `404 Not Found`: "Tarefa não encontrada".

### 4.4 Atualizar Tarefa
- **Rota:** `PUT /tasks/{task_id}`
- **Descrição:** Atualiza os dados de uma tarefa existente.
- **Parâmetros de Path:** `task_id` (inteiro).
- **Parâmetros de Entrada (Body JSON, enviar apenas o que deseja atualizar):**
  ```json
  {
    "title": "string",
    "description": "string",
    "subject": "string",
    "weight": int,
    "due_date": "string"
  }
  ```
- **Resposta de Sucesso (200 OK):** Retorna a tarefa atualizada.
- **Respostas de Erro:**
  - `400 Bad Request`: "Nenhum campo para atualizar" ou campos inválidos.

### 4.5 Concluir Tarefa
- **Rota:** `PATCH /tasks/{task_id}/complete`
- **Descrição:** Marca a tarefa como concluída, processando a pontuação, ofensiva (streak) e liberação de novas badges no gamification.
- **Parâmetros de Path:** `task_id` (inteiro).
- **Resposta de Sucesso (200 OK):**
  ```json
  {
    "task": {
      // Objeto da tarefa (Task) atualizada
    },
    "points_earned": int,
    "streak_updated": boolean,
    "badges_earned": [
      // Lista de badges (Badge) recém-conquistadas nesta ação
    ]
  }
  ```
- **Respostas de Erro:**
  - `400 Bad Request`: "Tarefa já foi concluída".

### 4.6 Deletar Tarefa
- **Rota:** `DELETE /tasks/{task_id}`
- **Descrição:** Exclui uma tarefa.
- **Parâmetros de Path:** `task_id` (inteiro).
- **Resposta de Sucesso:** `204 No Content` (sem corpo na resposta).

### 4.7 Listar Nomes de Disciplinas (Apenas das Tarefas)
- **Rota:** `GET /tasks/subjects/list`
- **Descrição:** Retorna uma lista simples com os nomes das disciplinas de forma única (*distinct*) apenas baseadas nas disciplinas preenchidas nas tarefas já existentes do usuário.
- **Parâmetros:** Nenhum.
- **Resposta de Sucesso (200 OK):**
  ```json
  [
    "Matemática",
    "Física",
    "Programação"
  ]
  ```
