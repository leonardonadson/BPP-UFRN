# Log de Refatorações

## Atualização #1: Centralização da Lógica de Negócio e Remoção de Duplicação
- **Data**: 29/09/2025
- **Code Smells Identificados**:
    - **Código Duplicado (Duplicate Code)**: Nos endpoints `get_task`, `complete_task`, `delete_task`.
    - **Método Longo / Múltiplas Responsabilidades (Long Method)**: O endpoint `complete_task` orquestrava a lógica de negócio.
    - **Gerenciamento de Transação Ineficiente**: Múltiplos `db.commit()` eram chamados por diferentes serviços para uma única ação do usuário.
- **Técnicas Aplicadas**:
    - **Extrair Função (Extract Method)**: Criada uma dependência (`get_task_for_user_dependency`) para remover a duplicação de código.
    - **Mover Método (Move Method)**: A lógica de orquestração de `complete_task` foi movida do `router` para uma nova função `process_task_completion` na camada de serviço (`score_service.py`).
    - **Consolidar Transação**: Os `db.commit()` individuais foram removidos dos serviços e um único `commit` foi colocado ao final da função `process_task_completion`.
- **Arquivos Afetados**:
    - `api/app/routers/tasks.py`
    - `api/app/services/score_service.py`
    - `api/app/services/badge_service.py`

---

### Antes e Depois

1. Endpoint complete_task (em routers/tasks.py)

    ANTES:
    
        @router.patch("/{task_id}/complete", response_model=TaskResponse)
        def complete_task(
            task_id: int,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            # Lógica de busca e validação DUPLICADA
            task = db.query(TaskModel).filter(
                TaskModel.id == task_id,
                TaskModel.owner_id == current_user.id
            ).first()
            
            if not task:
                raise HTTPException(...)
            
            if task.is_completed:
                raise HTTPException(...)
            
            # LÓGICA DE NEGÓCIO no router
            task.is_completed = True
            points_earned = award_points_for_task(current_user, task, db)
            streak_updated = update_user_streak(current_user, db)
            badges_earned = check_and_award_badges(current_user, db)
            
            db.commit() # Commit final no router
            
            return {
                "task": task,
                "points_earned": points_earned,
                "streak_updated": streak_updated,
                "badges_earned": badges_earned
            }


    DEPOIS:
        
        @router.patch("/{task_id}/complete", response_model=TaskResponse)
        def complete_task(
            task: TaskModel = Depends(get_task_for_user_dependency), # Duplicação removida
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            if task.is_completed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tarefa já foi concluída"
                )
            
            # Lógica de negócio DELEGADA para a camada de serviço
            completion_data = process_task_completion(current_user, task, db)
            
            return completion_data

    
2. Função de Serviço award_points_for_task (em services/score_service.py)

    A principal mudança foi a remoção da chamada db.commit(), centralizando a responsabilidade da transação na nova função orquestradora process_task_completion.

    ANTES:

        def award_points_for_task(user: User, task: Task, db: Session) -> int:
        """Calcula e atribui pontos pela conclusão de uma tarefa"""
        on_time = task.due_date is None or datetime.now() <= task.due_date
        points = calculate_task_points(task.weight, on_time)
        
        user.total_points += points
        task.points_awarded = points
        task.completed_at = datetime.now()
        
        db.commit()
        return points
    
    
    DEPOIS:

        def award_points_for_task(user: User, task: Task, db: Session) -> int:
        """Calcula e atribui pontos. O commit foi removido."""
        on_time = task.due_date is None or datetime.now() <= task.due_date
        points = calculate_task_points(task.weight, on_time)
        
        user.total_points += points
        task.points_awarded = points
        task.completed_at = datetime.now()
        
        # O db.commit() foi removido para ser centralizado.
        return points


3. Função de Serviço check_and_award_badges (em services/badge_service.py)
    
    Assim como no score_service, a chamada db.commit() foi removida para garantir uma transação atômica gerenciada pela função orquestradora.

    ANTES:
        
        def check_and_award_badges(user: User, db: Session) -> List[Badge]:
        """Verifica e concede badges baseadas nas conquistas do usuário"""
        awarded_badges = []
        # ... (lógica para verificar badges) ...

        for badge in all_badges:
            # ... (lógica para decidir se a badge deve ser concedida) ...
            
            if should_award:
                user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
                db.add(user_badge)
                awarded_badges.append(badge)
        
        if awarded_badges:
            db.commit()
        
        return awarded_badges

    
    DEPOIS:

        def check_and_award_badges(user: User, db: Session) -> List[Badge]:
        """Verifica e concede badges baseadas nas conquistas do usuário"""
        awarded_badges = []
        # ... (lógica para verificar badges) ...

        for badge in all_badges:
            # ... (lógica para decidir se a badge deve ser concedida) ...
            
            if should_award:
                user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
                db.add(user_badge)
                awarded_badges.append(badge)
        
        # O db.commit() foi removido daqui para ser centralizado
        # na função de serviço principal que orquestra a conclusão da tarefa.
        
        return awarded_badges


    JUSTIFICATIVA E IMPACTO:
        
        Esta refatoração substancial melhora significativamente a arquitetura da aplicação. Mover a lógica de negócio para a camada de 
        serviços e remover a duplicação de código torna os routers mais limpos e focados (agindo como verdadeiros controladores). 
        Centralizar a transação do banco de dados em uma única chamada commit torna a operação de completar uma tarefa atômica, 
        mais segura e mais eficiente. A manutenibilidade e a testabilidade do código foram drasticamente aprimoradas.

    

## Atualização #2: Separação de Responsabilidades no Registo de Utilizador
- **Data**: 04/10/2025
- **Code Smells Identificados**:
    - **Método Longo / Múltiplas Responsabilidades (Long Method)**: A função `register_user` era responsável por validar a existência de dados no banco e também por criar o novo registo.
- **Técnica Aplicada**:
    - **Extrair Função (Extract Method)**: A lógica de validação foi movida para uma função interna e dedicada, `_validate_user_creation`.
- **Ficheiros Afetados**:
    - `api/app/routers/auth.py`

---

### Antes e Depois

1. Função `register_user` (em `routers/auth.py`)

    ANTES:

        @router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
        def register_user(user: UserCreate, db: Session = Depends(get_db)):
            """Registra um novo usuário"""
            # Validação e criação misturadas
            if db.query(UserModel).filter(UserModel.email == user.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
            
            if db.query(UserModel).filter(UserModel.username == user.username).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome de usuário já existe"
                )
            
            hashed_password = get_password_hash(user.password)
            db_user = UserModel(
                email=user.email,
                username=user.username,
                hashed_password=hashed_password
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return db_user

    DEPOIS:

        def _validate_user_creation(user_data: UserCreate, db: Session):
            """Verifica se o email e o username já estão em uso."""
            if db.query(UserModel).filter(UserModel.email == user_data.email).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
            
            if db.query(UserModel).filter(UserModel.username == user_data.username).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nome de usuário já existe"
                )

        @router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
        def register_user(user: UserCreate, db: Session = Depends(get_db)):
            """Registra um novo usuário após validar os dados."""
            # Passo 1: Validação (agora em uma chamada de função clara)
            _validate_user_creation(user, db)
            
            # Passo 2: Criação (a responsabilidade principal da função)
            hashed_password = get_password_hash(user.password)
            db_user = UserModel(
                email=user.email,
                username=user.username,
                hashed_password=hashed_password
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return db_user
        

    JUSTIFICATIVA E IMPACTO:
            
        A separação da lógica de validação da lógica de criação torna a função register_user mais limpa, mais curta e mais fácil de 
        entender. Cada função agora tem uma responsabilidade única e bem definida, o que melhora a legibilidade, facilita a manutenção e 
        abre caminho para testes unitários mais focados no futuro.


## Atualização #3: Melhoria da Legibilidade com Objeto de Parâmetro
- **Data**: 05 de outubro de 2025
- **Code Smells Identificados**:
    - **Lista de Parâmetros Longa (Long Parameter List)**: A função `list_tasks` recebia múltiplos parâmetros para filtros, tornando a sua assinatura poluída e difícil de estender.
- **Técnica Aplicada**:
    - **Introduzir Objeto de Parâmetro (Introduce Parameter Object)**: Os parâmetros de filtro (`skip`, `limit`, `subject`, `completed`) foram agrupados numa nova classe Pydantic, `TaskFilterParams`.
- **Ficheiros Afetados**:
    - `api/app/routers/tasks.py`
    - `api/app/schemas.py`

---

### Antes e Depois

1. Ficheiro 'schemas.py'

    ANTES:

        O ficheiro não tinha uma estrutura dedicada para os filtros da listagem de tarefas.


    DEPOIS:

        Uma nova classe `TaskFilterParams` foi adicionada:
        ```python
        class TaskFilterParams(BaseModel):
            skip: int = 0
            limit: int = 100
            subject: Optional[str] = None
            completed: Optional[bool] = None


2. Função list_tasks (em routers/tasks.py)
    
    ANTES:

        def list_tasks(
            skip: int = 0,
            limit: int = 100,
            subject: Optional[str] = Query(None, description="Filtrar por disciplina"),
            completed: Optional[bool] = Query(None, description="Filtrar por status de conclusão"),
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
        # ...

    
    DEPOIS:

        def list_tasks(
            filters: TaskFilterParams = Depends(), # Assinatura muito mais limpa
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
        # ...´


    JUSTIFICATIVA E IMPACTO:
        
        Esta refatoração melhora drasticamente a legibilidade e a manutenibilidade da função list_tasks. Ao agrupar os múltiplos 
        parâmetros de filtro (skip, limit, subject, completed) num único objeto coeso (TaskFilterParams), a assinatura da função 
        torna-se mais limpa e a sua intenção mais clara, aderindo melhor aos princípios de código limpo.

        O impacto mais significativo é na extensibilidade do código. Agora, para adicionar um novo filtro de pesquisa no futuro 
        (por exemplo, filtrar por weight), basta adicionar um novo campo à classe TaskFilterParams no ficheiro schemas.py, sem a 
        necessidade de alterar a assinatura da função list_tasks. Isto demonstra um design de software mais robusto, flexível e 
        preparado para futuras evoluções da aplicação.