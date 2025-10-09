# Scripts e Ferramentas de Análise de Qualidade
Este documento descreve as ferramentas de análise estática de código utilizadas no projeto StudyStreak e fornece as instruções para executar os scripts de análise de qualidade.

**1. Ferramentas Utilizadas**

O projeto utiliza duas ferramentas principais para garantir a qualidade e a consistência do código-fonte da API:

    Pylint:
    Propósito: Análise estática completa, verificação de conformidade com o guia de estilo PEP 8, deteção de erros e    identificação de code smells.

    Instalação: pip install pylint

    Radon:
    Propósito: Análise de métricas de complexidade de código, com foco na medição da complexidade ciclomática.

    Instalação: pip install radon

**2. Scripts de Análise**

Para facilitar a execução das análises, foram definidos os seguintes processos:

    Análise Geral com Pylint:
    O principal script de análise do projeto é o analise.bat, localizado na raiz do projeto.

    O que faz: Este script executa o Pylint sobre o pacote principal da aplicação (api/app), utilizando as configurações definidas no ficheiro .pylintrc para gerar um relatório de qualidade detalhado.

    Como Executar:

    1. Abra um terminal na pasta raiz do projeto.

    2. Ative o ambiente virtual:
    .\api\venv\Scripts\activate

    3. Execute o script:
    .\analise.bat

    Análise de Complexidade com Radon:
    mede a complexidade ciclomática do código, utilizando a ferramenta Radon diretamente através de comandos.

    Como Executar:

    1. Certifique-se de que o ambiente virtual está ativo.

    2. Execute o comando no terminal a partir da raiz do projeto:
    radon cc api/app -a