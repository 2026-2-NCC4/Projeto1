# 📊 Contabilidade e Finanças: Indicadores Financeiros

## 📖 Descrição do Trabalho

Esta etapa do projeto é voltada para a análise financeira dos cenários presentes na base de dados.

A partir da base já tratada, foram calculados indicadores financeiros para os **1.200 cenários**, considerando os **12 anos disponíveis**. O objetivo é organizar as informações contábeis e transformar os dados em indicadores que auxiliem na comparação e análise do desempenho financeiro ao longo do período.

Os resultados foram consolidados em uma planilha Excel, permitindo consultar diferentes cenários e acompanhar seus indicadores ano a ano.

## 🎯 Objetivo

Desenvolver a etapa de análise financeira do projeto, buscando:

* Calcular os principais indicadores financeiros;
* Analisar liquidez, endividamento, rentabilidade e geração de valor;
* Organizar as demonstrações contábeis utilizadas nos cálculos;
* Permitir a visualização dos resultados por cenário e por ano;
* Preparar os resultados para a etapa posterior de comparação e ranking dos anos.

## ⚙️ Tecnologias Utilizadas

🐍 **Python** – Desenvolvimento dos cálculos e processamento dos dados.

📊 **Pandas** – Manipulação, organização e consolidação da base.

🔢 **NumPy** – Apoio aos cálculos numéricos.

📑 **OpenPyXL** – Geração e formatação da planilha Excel.

📓 **Jupyter Notebook** – Desenvolvimento e validação da análise.

## 📈 Indicadores Calculados

Foram trabalhados os seguintes indicadores:

* Margem EBITDA;
* Margem Líquida;
* Liquidez Corrente (LC);
* Liquidez Seca (LS);
* Liquidez Imediata (LI);
* Liquidez Geral (LG);
* Participação de Capital de Terceiros (PCT);
* Composição do Endividamento (CE);
* Imobilização do Patrimônio Líquido (IPL);
* EBITDA;
* NOPAT;
* Capital Investido;
* EVA;
* MVA Aproximado.

O **WACC de 8%** também foi utilizado como parâmetro para os cálculos relacionados à geração de valor.

## 📊 Organização da Análise

Os indicadores foram calculados para cada combinação de cenário e ano, resultando na consolidação dos dados dos **1.200 cenários ao longo de 12 anos**.

Também foram organizadas as informações das demonstrações contábeis utilizadas na análise, incluindo:

* Balanço Patrimonial;
* Demonstração do Resultado do Exercício (DRE);
* Fluxo de Caixa.

## 📁 Planilha de Indicadores

Foi desenvolvida uma planilha para facilitar a consulta e interpretação dos resultados.

Ela está organizada nas seguintes áreas:

* **Dicionário de KPIs Financeiros** – apresenta os indicadores utilizados e suas respectivas definições;
* **Demonstrações Contábeis** – reúne as contas contábeis utilizadas na análise;
* **Indicadores - Índices** – apresenta os indicadores financeiros de cada cenário ao longo dos anos;
* **Dados de Base** – contém os dados utilizados na construção da análise.

A planilha também permite selecionar um cenário específico para visualizar seus resultados ao longo dos 12 anos.

## 🧪 Validação

Durante o desenvolvimento foram realizadas verificações para garantir:

✔️ Cálculo dos indicadores para todos os cenários;

✔️ Correspondência entre os anos e seus respectivos cenários;

✔️ Preservação das informações originais da base;

✔️ Identificação dos dados indisponíveis sem substituí-los artificialmente por zero;

✔️ Organização dos resultados para utilização nas próximas etapas da análise.

## ⚠️ Observação sobre o Ano 12

O Ano 12 apresenta ausência estrutural de algumas informações contábeis na base original.

Por esse motivo, quando não existem dados suficientes para determinado cálculo, o resultado é apresentado como **N/D (Não Disponível)**, evitando considerar informações inexistentes como valor zero.

## 📖 Situação Atual


A etapa de cálculo e organização dos indicadores financeiros foi desenvolvida e os resultados foram consolidados para análise.

A próxima etapa consiste na definição da metodologia de comparação dos resultados e na construção do **ranking dos anos**, utilizando os indicadores financeiros calculados nesta fase.

## 📦 Arquivos da Entrega

Os arquivos referentes à análise financeira estão disponíveis na pasta **Contabilidade e Finanças**, incluindo os notebooks utilizados nos cálculos e a planilha com os resultados consolidados.
