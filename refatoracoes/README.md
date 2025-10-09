# Processo de Análise de Qualidade
As análises de qualidade do código foram realizadas com as ferramentas Pylint e Radon. Abaixo estão
as instruções para executar as mesmas análises.

**Pré-requisitos**:

    Python e as dependências do projeto instaladas (pip install -r requirements.txt).
    As ferramentas de análise instaladas no ambiente virtual (pip install pylint radon).

**Passo a Passo para Execução**:

    1. Abra um terminal na pasta raiz do projeto (BPP-UFRN).

    2. Ative o ambiente virtual: .\api\venv\Scripts\activate

    3. Para análise com Pylint:
        Execute o script de análise: .\analise.bat
        Este script executa o Pylint no pacote da aplicação (api/app) utilizando as configurações definidas no ficheiro .pylintrc para garantir uma análise precisa e relevante.

    4. Para Análise de Complexidade com Radon:

        1. pip install radon

        2. radon cc api/app -a

        Este último comando calcula a complexidade ciclomática de todas as funções e métodos e, com a opção -a, exibe a média geral no final.


**Convenções de Código**

    O projeto foi desenvolvido seguindo um conjunto de convenções para garantir a consistência e a legibilidade do código.

    Guia de Estilo: O código segue o guia de estilo oficial do Python, PEP 8. A conformidade foi verificada e reforçada através do Pylint.

    Ordem de Importações: As importações foram padronizadas na seguinte ordem: 1. Bibliotecas padrão do Python; 2. Bibliotecas de terceiros (ex: FastAPI); 3. Importações da aplicação local (from app...).

    Nomenclatura: Foram utilizados nomes descritivos e que revelam a intenção, seguindo o padrão snake_case para variáveis e funções, e PascalCase para classes.

    Docstrings: Funções e módulos importantes foram documentados com docstrings para explicar o seu propósito, argumentos e retorno.

**Resumo das Métricas Atuais:**

    Após os ciclos de refatoração, as métricas de qualidade do código-fonte da API são as seguintes:

        - Pontuação do Pylint: 10.00 / 10

        - Complexidade Ciclomática Média (Radon): A (2.11)

    A pontuação máxima no Pylint e uma baixa complexidade média indicam que a base de código atingiu um alto nível de qualidade, consistência e manutenibilidade.


