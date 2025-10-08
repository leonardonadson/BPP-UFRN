# Catálogo de Code Smells Identificados

Este documento cataloga os principais code smells identificados no código da API durante o processo de refatoração, conforme as atualizações descritas no refactoring-log.md. Cada secção mostra o problema encontrado e um trecho do código antes da refatoração ser aplicada.

# Identificados na Atualização #1

Nesta fase, focámo-nos em centralizar a lógica de negócio que estava espalhada e duplicada no router de tarefas.


# 1. Código Duplicado (Duplicate Code)

Ficheiro(s) Afetado(s): api/app/routers/tasks.py

Descrição: A lógica para procurar uma tarefa na base de dados e validar se ela pertencia ao utilizador logado estava repetida em três endpoints diferentes (get_task, complete_task, delete_task).

Status: Corrigido na Atualização #1.

Trecho de Código (em complete_task):

    
    # Lógica de busca e validação DUPLICADA
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(...)


# 2. Método Longo / Múltiplas Responsabilidades (Long Method)

Ficheiro(s) Afetado(s): api/app/routers/tasks.py

Descrição: O endpoint complete_task não só lidava com o pedido HTTP, mas também orquestrava toda a lógica de negócio de pontuação, streaks e badges, violando o Princípio da Responsabilidade Única.

Status: Corrigido na Atualização #1.

Trecho de Código (em complete_task):

    @router.patch("/{task_id}/complete", response_model=TaskResponse)
    def complete_task(
        task_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # ... (lógica de busca) ...
            
        # LÓGICA DE NEGÓCIO no router
        task.is_completed = True
        points_earned = award_points_for_task(current_user, task, db)
        streak_updated = update_user_streak(current_user, db)
        badges_earned = check_and_award_badges(current_user, db)
            
        db.commit() # Commit final no router
            
        return { ... }


# 3. Gerenciamento de Transação Ineficiente

Ficheiro(s) Afetado(s): api/app/services/score_service.py, api/app/services/badge_service.py

Descrição: Várias funções de serviço realizavam os seus próprios db.commit(). Para uma única ação do utilizador (completar uma tarefa), eram feitas múltiplas transações na base de dados, o que é ineficiente e potencialmente inseguro.

Status: Corrigido na Atualização #1.

Trecho de Código (em award_points_for_task):

    def award_points_for_task(user: User, task: Task, db: Session) -> int:
        # ... (lógica de atribuição de pontos) ...
            
        user.total_points += points
        task.points_awarded = points
        task.completed_at = datetime.now()
            
        db.commit() # Commit individual e ineficiente
        return points


# Identificados na Atualização #2

Nesta atualização, o foco foi melhorar a clareza e a separação de responsabilidades no fluxo de autenticação.


# 4. Método Longo / Múltiplas Responsabilidades (Long Method)
Ficheiro(s) Afetado(s): api/app/routers/auth.py

Descrição: A função register_user era responsável por duas tarefas distintas: validar se o email e o nome de utilizador já existiam (lógica de negócio) e criar o novo registo no banco de dados (ação).

Status: Corrigido na Atualização #2.

Trecho de Código:

    @router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
    def register_user(user: UserCreate, db: Session = Depends(get_db)):
        # Validação e criação misturadas
        if db.query(UserModel).filter(UserModel.email == user.email).first():
            raise HTTPException(...)
        
        if db.query(UserModel).filter(UserModel.username == user.username).first():
            raise HTTPException(...)
        
        hashed_password = get_password_hash(user.password)
        # ... (criação do utilizador) ...


# Identificados na Atualização #3

A última refatoração focou-se em tornar o código mais legível e, principalmente, mais fácil de estender no futuro.

# 5. Lista de Parâmetros Longa (Long Parameter List)
Ficheiro(s) Afetado(s): api/app/routers/tasks.py

Descrição: A função list_tasks recebia múltiplos parâmetros para filtros e paginação (skip, limit, subject, completed). Isto tornava a assinatura da função longa, menos legível e difícil de manter ou estender com novos filtros.

Status: Corrigido na Atualização #3.

Trecho de Código:

    def list_tasks(
        skip: int = 0,
        limit: int = 100,
        subject: Optional[str] = Query(None, description="Filtrar por disciplina"),
        completed: Optional[bool] = Query(None, description="Filtrar por status de conclusão"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # ...