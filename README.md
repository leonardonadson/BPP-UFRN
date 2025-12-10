# 🎯 StudyStreak - Boas Práticas de Programação

## 🚀 Descrição do Projeto

Este repositório reúne o código e a documentação do **StudyStreak**, uma plataforma web de produtividade acadêmica gamificada desenvolvida para a disciplina **Boas Práticas de Programação (BPP 2025.2)**.

O objetivo principal é aplicar princípios de engenharia de software com **código limpo, identificação de code smells e refatoração**, além de um processo de **planejamento de produto** com backlog e critérios de qualidade, resultando em um software manutenível e escalável.

> 📌 Propósito: Entregar um MVP funcional que permita gerenciar tarefas acadêmicas com engajamento via pontos, streaks e badges, priorizando a experiência do estudante e a qualidade interna do código.

***

## 📚 Tópicos e Conceitos Abordados

### 🔹 Planejamento de Produto

*   Visão de Produto, público-alvo e hipótese de valor orientada ao problema central do estudante universitário.
*   MVP com API e Web App: cadastro, listagem e conclusão de tarefas, pontos e conquistas iniciais.
*   Product Backlog com user stories, critérios de aceitação e critérios de qualidade para cada item.

### 🔹 Boas Práticas e Qualidade

*   Clean Code: nomes claros, funções pequenas, responsabilidade única e formatação consistente.
*   Identificação de code smells: Long Method, Duplicate Code, Poor Naming e catálogo de refatorações.
*   Métricas de qualidade: complexidade ciclomática e duplicação monitoradas com ferramentas de análise.

### 🔹 Arquitetura e Estrutura

*   Monorepo com backend e frontend em pastas dedicadas, documentação e registro de refatorações.
*   Arquitetura em camadas no backend: controllers, services, models e utils para separação de responsabilidades.
*   Componentização no frontend: reutilização e clareza de estado para páginas e componentes de UI.

***

## ▶️ Como Executar o Projeto

### 📌 Pré-requisitos

*   Python 3.10+ e gerenciador de pacotes com venv.
*   Node.js 18+ com npm ou yarn para o frontend.
*   Banco local SQLite para desenvolvimento e Postgres para produção.

### 📥 Clonar o Repositório

```bash
git clone https://github.com/leonardonadson/BPP-UFRN.git
cd BPP-UFRN
```

### 📂 Backend (API - FastAPI)

```bash
cd api
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

*   API disponível em http://127.0.0.1:8000.

### 🌐 Frontend (Web - React + Vite)

```bash
cd web
npm install
npm run dev
```

*   Web disponível em http://127.0.0.1:5173 (ou porta indicada pelo Vite).

***

## 🧪 Automação de Testes
O projeto conta com uma suíte de testes robusta (cobrindo 92% do código), seguindo a pirâmide de testes e os princípios FIRST e AAA (Arrange, Act, Assert).

### 📋 Pré-requisitos de Teste
Certifique-se de estar no ambiente virtual (venv) do backend e instale as dependências:

```bash
pip install pytest pytest-cov
```

### 🚀 Comandos de Execução
1. Executar todos os testes: Roda testes unitários (lógica de negócio/schemas) e de integração (rotas/banco).

```bash
pytest
```

2. Executar com Relatório de Cobertura: Exibe a porcentagem de cobertura no terminal.

```bash
pytest --cov=app tests/
```

3. Gerar Relatório HTML Detalhado: Gera um site estático em tests/coverage-results/ para inspeção visual linha a linha.

```bash
pytest --cov=app --cov-report=html tests/
```

***

## ⚡ Análise de Desempenho e Otimização

O projeto inclui uma suíte de testes de performance (`scripts/performance_test.py`) que utiliza **`cProfile`** para identificar gargalos de CPU e I/O (Banco de Dados).

A análise comparou implementações "Ingênuas" contra "Otimizadas" (Best Practices) nos arquivos principais da API, resultando nos seguintes ganhos:

| Gargalo Identificado | Otimização Aplicada | Resultado (Tempo/Recurso) |
| :--- | :--- | :--- |
| **1. Agregação (Dashboard)** | Cálculo via SQL `SUM` vs Python `sum()` | Redução de uso de CPU e Memória RAM |
| **2. Contagem (Badges)** | Uso de `COUNT(*)` vs `len(all())` | Complexidade de Memória de **O(N)** para **O(1)** |
| **3. Paginação (Tasks)** | Filtros SQL (`LIMIT/OFFSET`) | Prevenção de *Full Table Scan* e *Overfetching* |
| **4. N+1 Selects (Users)** | Uso de `joinedload` (Eager Loading) | **2.6x mais rápido** (44s ➝ 17s) |

### 📋 Execução dos Testes
O script de carga popula automaticamente um banco de dados SQLite local com **500 usuários** e **50.000 tarefas** para simular um ambiente de produção real.

```bash
# Certifique-se de estar com o venv ativo
python scripts/performance_test.py
```

### 📊 Resultados e Documentação
A análise completa dos gargalos, comparativos de tempo ("Antes vs Depois") e trade-offs das otimizações encontra-se em:

📄 Documentação Técnica: docs/performance-analysis.md

📸 Evidências de Execução: docs/assets/

***

## 🧠 Gerenciamento de Memória e Eficiência

Para atender aos requisitos de otimização em linguagens gerenciadas (Python), foram implementadas estratégias de **Lazy Evaluation** e **Caching** para mitigar gargalos de RAM e CPU.

A análise foi realizada utilizando **`tracemalloc`** e demonstrou ganhos expressivos em dois cenários críticos:

| Técnica | Aplicação (Arquivo) | Resultado (Antes ➝ Depois) | Impacto |
| :--- | :--- | :--- | :--- |
| **Generators** (Yield) | Exportação de Dados (`app/utils/export.py`) | **6.75 MB ➝ 0.0006 MB** | Economia de **99.9% de RAM** (O(N) ➝ O(1)) |
| **Cache LRU** | Cálculo de Pontuação (`app/services/score_service.py`) | **1.80s ➝ 0.006s** | Execução **300x mais rápida** em cargas repetitivas |

### 🧪 Validação dos Testes
O projeto inclui um script de laboratório que simula alta carga (100.000 registros) para validar essas métricas:

```bash
# Executa a análise comparativa de memória e CPU
python scripts/memory_test.py
```

### 📄 Documentação Técnica
Detalhes sobre a implementação do lru_cache, a substituição de listas por generators e as evidências de execução (snapshots de memória) estão disponíveis em:

* **Relatório Completo:** docs/memory-analysis.md

* **Evidências:** Pasta docs/assets/

***

## 📂 Estrutura do Repositório

```
studystreak/
├── api/                         # Backend (FastAPI)
│   ├── app/
│   │   ├── auth/
│   │   ├── routers/
│   │   ├── services/
│   │   └── utils/
│   └── venv/
│
├── docs/                       # Visão, backlog e materiais do produto
│   ├── assets/
│   ├── coverage-report.md      # Análise de cobertura
│   ├── debugging-log.md        # Gugs encontrados
│   ├── memory-analysis.md      # Gargalos e otimizações
│   ├── performance-analysis.md   # Análise de memória
│   └── testing-report.md         # Relatório completo
│
├── refactoring/                # Registro de code smells e refatorações
│
├── scripts/                    # Análise de performance
│
├── tests/                      # Suíte de Testes Automatizados
│   ├── coverage-results/       # Relatórios HTML
│   ├── integration/            # Testes de rotas e banco de dados
│   └── unit/                   # Testes isolados (Models, Schemas, Services)
│
├── web/                        # Frontend (React + Vite)
│   └── src/
│       ├── components/
│       ├── types/
│       └── services/
│
└── README.md                   # Visão geral + instruções
```

*   Monorepo para desenvolvimento coeso de API e Web App com documentação centralizada.

***

## 🛠 Tecnologias

* **Backend:** Python, FastAPI, SQLAlchemy (com otimizações Eager Loading e Aggregations), autenticação JWT.
* **Frontend:** React com Vite, componentes reutilizáveis e estado claro.
* **Banco de Dados:** SQLite (dev) e PostgreSQL (produção).
* **Estilização:** TailwindCSS para prototipagem rápida e responsiva.
* **Qualidade:** pylint, flake8, black, radon, ESLint, Prettier.
* **Performance & Profiling:** cProfile, pstats (CPU), tracemalloc (Memória).
* **Testes:** pytest, pytest-cov, httpx (API) e Vitest (frontend).
* **Deploy:** Vercel com configuração para monorepo.

***

## 📚 Referências

*   Clean Code e catálogo de refatorações para orientar legibilidade e design interno.
*   Boas práticas de organização em camadas e componentização de UI para escalabilidade.
*   Ferramentas de análise estática e cobertura de testes no ciclo de integração contínua.

***

## 👨‍💻 Autores

<table>
<tr>
<td align="center">
<a href="https://github.com/leonardonadson">
<img src="https://avatars.githubusercontent.com/u/72714982?v=4" width="100px;" alt="Foto de Leonardo Nadson no GitHub"/>
<br>
<sub>
<b>Leonardo Nadson</b>
</sub>
</a>
</td>
<td align="center">
<a href="https://github.com/MarcusAurelius33">
<img src="https://avatars.githubusercontent.com/u/193627412?v=4" width="100px;" alt="Foto de Marcus Aurelius no GitHub"/>
<br>
<sub>
<b>Marcus Aurelius</b>
</sub>
</a>
</td>
</tr>
</table>

Desenvolvido como parte das atividades acadêmicas da disciplina de Boas Práticas de Programação (BPP 2025.2).
