# 🎯 StudyStreak - Boas Práticas de Programação

## 🚀 Descrição do Projeto

Este repositório reúne o código e a documentação do **StudyStreak**, uma plataforma web de produtividade acadêmica gamificada desenvolvida para a disciplina **Boas Práticas de Programação (BPP 2025.2)**.

O objetivo principal é aplicar princípios de engenharia de software com **código limpo, identificação de code smells e refatoração**, além de um processo de **planejamento de produto** com backlog e critérios de qualidade, resultando em um software manutenível e escalável.

> 📌 Propósito: Entregar um MVP funcional que permita gerenciar tarefas acadêmicas com engajamento via pontos, streaks e badges, priorizando a experiência do estudante e a qualidade interna do código.

***

## 📚 Tópicos e Conceitos Abordados

### 🔹 Planejamento de Produto

* Visão de Produto, público-alvo e hipótese de valor orientada ao problema central do estudante universitário.
* MVP com API e Web App: cadastro, listagem e conclusão de tarefas, pontos e conquistas iniciais.
* Product Backlog com user stories, critérios de aceitação e critérios de qualidade para cada item.

### 🔹 Boas Práticas e Qualidade

* Clean Code: nomes claros, funções pequenas, responsabilidade única e formatação consistente.
* Identificação de code smells: Long Method, Duplicate Code, Poor Naming e catálogo de refatorações.
* Métricas de qualidade: complexidade ciclomática e duplicação monitoradas com ferramentas de análise.

### 🔹 Arquitetura e Estrutura

* Monorepo com backend e frontend em pastas dedicadas, documentação e registro de refatorações.
* Arquitetura em camadas no backend: controllers, services, models e utils para separação de responsabilidades.
* Componentização no frontend: reutilização e clareza de estado para páginas e componentes de UI.

***

## ▶️ Como Executar o Projeto

### 📌 Pré-requisitos

* Python 3.10+ e gerenciador de pacotes com venv.
* Node.js 18+ com npm ou yarn para o frontend.
* Banco local SQLite para desenvolvimento e Postgres para produção.

### 📥 Clonar o Repositório

```bash
git clone [https://github.com/leonardonadson/BPP-UFRN.git](https://github.com/leonardonadson/BPP-UFRN.git)
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

📋 Pré-requisitos de Teste
Certifique-se de estar no ambiente virtual (venv) do backend e instale as dependências:

```bash
pip install pytest pytest-cov
```

## 🚀 Comandos de Execução
1. Executar todos os testes: Roda testes unitários (lógica de negócio/schemas) e de integração (rotas/banco).

```bash
pytest
```

2. Executar com Relatório de Cobertura: Exibe a porcentagem de cobertura no terminal.

```bash
pip install pytest pytest-cov
```

3. Gerar Relatório HTML Detalhado: Gera um site estático em tests/coverage-results/ para inspeção visual linha a linha.

```bash
pytest --cov=app --cov-report=html tests/
```


## 📂 Estrutura do Repositório

```
studystreak/
├── api/                  # Backend (FastAPI)
│   └── src/
│       ├── controllers/
│       ├── models/
│       ├── services/
│       └── utils/
├── web/                  # Frontend (React + Vite)
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── docs/                 # Visão, backlog e materiais do produto
├── refactoring/          # Registro de code smells e refatorações
└── README.md
```

*   Monorepo para desenvolvimento coeso de API e Web App com documentação centralizada.

***

## 🛠️ Tecnologias

*   Backend: Python, FastAPI, SQLAlchemy, autenticação JWT.
*   Frontend: React com Vite, componentes reutilizáveis e estado claro.
*   Banco de Dados: SQLite (dev) e PostgreSQL (produção).
*   Estilização: TailwindCSS para prototipagem rápida e responsiva.
*   Qualidade: pylint, flake8, black, radon, ESLint, Prettier.
*   Testes: pytest, httpx (API) e Vitest (frontend).
*   Deploy: Vercel com configuração para monorepo.

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
