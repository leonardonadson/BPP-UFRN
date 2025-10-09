# Métricas de Qualidade do Código – Projeto StudyStreak
Introdução
Este documento apresenta e analisa as métricas quantitativas de qualidade recolhidas durante o processo de
desenvolvimento e refatoração da API do projeto StudyStreak. O objetivo é demonstrar a evolução da saúde
do código através do uso de ferramentas de análise estática e documentar o estado final de qualidade da
aplicação.

# 1. Ferramenta Utilizada: Pylint
A principal ferramenta utilizada para a análise de qualidade foi o Pylint, um analisador de código
estático para Python. Ele foi escolhido pela sua capacidade de realizar uma verificação completa, que inclui:

    Detecção de erros: Encontrar bugs prováveis no código.

    Aplicação de convenções de estilo: Garantir a conformidade com o guia de estilo PEP 8.

    Identificação de code smells: Sugerir oportunidades de refatoração para melhorar a estrutura e a legibilidade do código.

    Sistema de pontuação: Fornecer uma nota de 0 a 10 que serve como uma métrica objetiva da qualidade geral do código.

A análise foi executada de forma consistente através de um script (analise.bat) que invocava o Pylint sobre o pacote principal da aplicação (api/app).

# 2. Evolução da Pontuação de Qualidade
A jornada para alcançar um código de alta qualidade foi iterativa, como demonstram as pontuações do Pylint em diferentes fases do projeto.

Análise Inicial (Nota: 5.80/10)

    A primeira análise, realizada após a estruturação inicial da API, resultou numa nota baixa de 5.80/10.

Principais Problemas Detetados:

    Erros de Importação (E0402): O Pylint não estava a conseguir resolver as importações relativas do projeto, gerando um grande número de falsos positivos.

    Código Morto (W0611, W0613): Várias importações e argumentos de função não estavam a ser utilizados.

    Inconsistências de Formatação (C): Havia muitos problemas de espaçamento, linhas demasiado longas e falta de newlines no final dos ficheiros.

Esta nota inicial serviu como um baseline, indicando que, embora a API fosse funcional, havia uma dívida técnica significativa e espaço para melhorias em estrutura, estilo e robustez.

Análises Intermediárias (Nota: 7.13/10 a 7.20/10)

Após as primeiras grandes refatorações (Atualizações #1, #2, #3), a pontuação subiu para a faixa de 7.13 a 7.20.

Análise dos Resultados:

    Melhoria: A correção de code smells estruturais, como a duplicação de código e a separação de responsabilidades, resultou num aumento significativo da nota.

    Estagnação: A pontuação estagnou em torno de 7/10 porque o problema fundamental com as importações persistia. Durante esta fase, as importações foram alteradas de relativas para absolutas, o que mudou o tipo de erro de E0402 para E0401 (Unable to import), mas não resolveu a causa raiz do problema de configuração do Pylint.

Esta fase foi crucial para aprender que a qualidade do código não depende apenas do código em si, mas também da configuração correta das ferramentas de análise para que elas entendam a arquitetura do projeto.

Análise Final (Nota: 10.00/10)

A pontuação máxima de 10.00/10  foi alcançada após a "Atualização #4", que consistiu em duas frentes:

    Configuração Definitiva do Pylint: O analise.bat e o .pylintrc foram ajustados para que o Pylint analisasse a API como um pacote, resolvendo de vez todos os erros de importação.

    Limpeza Final do Código: Foram corrigidos todos os apontamentos restantes e válidos do relatório, incluindo a remoção de todo o "código morto", a correção da formatação e a aplicação de pequenas refatorações de legibilidade.

    Atingir a nota 10/10 valida que a base de código do projeto se encontra num estado de alta qualidade, consistente, legível e aderente às boas práticas da comunidade Python.

# 3. Análise de Complexidade (Radon)
Para complementar a análise do Pylint, foi utilizada a ferramenta radon para medir a complexidade ciclomática do código. A complexidade ciclomática avalia o número de "caminhos" lógicos independentes através do código. Um valor baixo indica que as funções são simples e fáceis de testar.

Comando Executado: radon cc api/app -a

Complexidade Ciclomática Média: A (2.11)

Análise
    Uma baixa complexidade média confirma que as refatorações, como a extração de funções e a separação de responsabilidades, foram bem-sucedidas em manter a lógica do programa simples e focada, um pilar fundamental para a manutenibilidade a longo prazo.

# 4. Conclusão
As métricas demonstram uma clara e significativa evolução na qualidade do código da API StudyStreak. O projeto evoluiu de uma base funcional com uma pontuação de qualidade modesta para uma aplicação robusta, limpa e com nota máxima numa das ferramentas de análise estática mais rigorosas do mercado. Este processo iterativo de análise, identificação de problemas e refatoração foi fundamental para pagar a dívida técnica inicial e estabelecer uma base sólida para futuras evoluções do projeto.