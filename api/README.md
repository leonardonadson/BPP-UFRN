# StudyStreak API - Endpoints

## 🔐 Autenticação

### `POST /auth/register`
```json
{
  "email": "usuario@email.com",
  "username": "nome_usuario",
  "password": "senha123"
}
```

### `POST /auth/login`
```json
{
  "email": "usuario@email.com",
  "password": "senha123"
}
```
**Resposta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "token_type": "bearer"
}
```

***

## 👤 Usuários (🔒 Requer Authentication)

### `GET /users/me`
Retorna dados do usuário logado.

### `GET /users/dashboard`
Retorna dashboard completo com tarefas e badges.

---

## 📝 Tarefas (🔒 Requer Authentication)

### `POST /tasks/`
```json
{
  "title": "Estudar para prova",
  "description": "Revisar capítulos 1-5",
  "subject": "Matemática",
  "weight": 8,
  "due_date": "2025-09-30T18:00:00"
}
```

### `GET /tasks/`
**Query params:** `skip`, `limit`, `subject`, `completed`

### `GET /tasks/{task_id}`
Busca tarefa específica.

### `PATCH /tasks/{task_id}/complete`
Completa tarefa e retorna pontos/badges ganhos:
```json
{
  "task": {...},
  "points_earned": 80,
  "streak_updated": true,
  "badges_earned": [...]
}
```

### `DELETE /tasks/{task_id}`
Remove tarefa.

### `GET /tasks/subjects/list`
Lista disciplinas disponíveis.

---

## 🔑 Autorização

**Header obrigatório para endpoints protegidos:**
```
Authorization: Bearer SEU_TOKEN_AQUI
```

**Swagger UI:** http://127.0.0.1:8000/docs
1. Login via `/auth/login`
2. Copie o token
3. Clique "Authorize" 
4. Digite: `Bearer TOKEN`

