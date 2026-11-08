# 📊 Projeto Interdisciplinar: Ciência de Dados – CTI Analytics

## 📖 Descrição

O **CTI Analytics** consiste no desenvolvimento de uma plataforma analítica voltada ao planejamento e desempenho financeiro da CTI Global, com o objetivo de transformar grandes volumes de dados financeiros em informações estratégicas para apoiar a tomada de decisões.

Esta entrega contempla o desenvolvimento de um **dashboard interativo**, construído em Python utilizando Streamlit, com a finalidade de disponibilizar indicadores financeiros, análises estatísticas e visualizações que permitam acompanhar o desempenho da empresa.


## 🎯 Objetivo

Desenvolver e disponibilizar um painel de indicadores financeiros capaz de apoiar decisões estratégicas e operacionais, oferecendo uma visão integrada do desempenho da empresa.

O dashboard permite acompanhar indicadores, analisar resultados históricos, comparar cenários e explorar relações entre variáveis financeiras.

## 📊 Indicadores Implementados

O painel contempla indicadores financeiros relacionados ao desempenho econômico e operacional da empresa, incluindo:

* Receita;
* EBITDA;
* Margem EBITDA;
* Margem Líquida;
* Resultado Líquido;
* Liquidez Corrente;
* Capital de Giro;
* Geração de Caixa;
* NOPAT;
* ROIC;
* EVA.

Os indicadores são apresentados por meio de cards, gráficos e visualizações comparativas, permitindo acompanhar os resultados e identificar variações relevantes.

## 📈 Funcionalidades do Dashboard

O dashboard foi desenvolvido com navegação organizada em páginas específicas, reunindo diferentes perspectivas de análise.

As principais funcionalidades estão distribuídas nas seguintes páginas:

* **Visão Geral:** apresenta os principais KPIs financeiros, gráficos de desempenho e informações resumidas sobre a situação financeira da empresa;
* **Indicadores:** disponibiliza os indicadores financeiros calculados a partir das demonstrações contábeis, permitindo acompanhar seus resultados;
* **Insights:** apresenta interpretações dos dados e informações relevantes identificadas nas análises, auxiliando na compreensão dos resultados;
* **Regressão:** reúne análises estatísticas e modelos de regressão para investigar relações entre variáveis financeiras e identificar tendências;
* **Cenários:** permite explorar e comparar diferentes cenários financeiros, apoiando a avaliação de possibilidades e resultados.

## 🔎 Filtros, Comparações e Visualizações

Foram implementados recursos interativos para facilitar a exploração dos dados e a análise financeira.

O dashboard permite:

* Filtrar informações por ano e cenário;
* Comparar resultados financeiros entre diferentes períodos;
* Acompanhar a evolução dos indicadores;
* Visualizar variações de desempenho;
* Analisar indicadores por meio de gráficos e KPIs;
* Identificar tendências e padrões nos dados.

As visualizações foram organizadas para facilitar a interpretação das informações e proporcionar uma experiência de análise mais intuitiva.

## 📉 Análises Estatísticas e Financeiras

Além da apresentação dos indicadores, a plataforma contempla análises que ampliam a capacidade de interpretação dos dados.

**Análise de Regressão**

Utiliza modelos estatísticos para investigar relações entre variáveis financeiras, avaliar comportamentos e identificar possíveis tendências.

**Insights Analíticos**

Transforma os resultados das análises em informações interpretativas, destacando variações, padrões e pontos de atenção relevantes para a tomada de decisão.

**Análise de Cenários**

Permite explorar diferentes possibilidades financeiras e observar como alterações nas condições analisadas podem influenciar os resultados.

## 🔗 Integração dos Dados

O dashboard utiliza os dados preparados na **Entrega 1**, seguindo as etapas de tratamento, organização e padronização da base financeira.

A integração contempla:

* Leitura dos dados financeiros tratados;
* Organização das informações para utilização no dashboard;
* Padronização dos indicadores;
* Disponibilização dos dados para as diferentes páginas da aplicação;
* Tratamento de informações ausentes e inconsistências.

A integração garante que as análises apresentadas na plataforma utilizem uma fonte de dados organizada e consistente.

## 🖥️ Tecnologias Utilizadas

O desenvolvimento da solução utilizou as seguintes tecnologias:

* **Python:** linguagem principal de desenvolvimento;
* **Streamlit:** construção da aplicação web e do dashboard interativo;
* **Pandas:** manipulação, tratamento e organização dos dados;
* **NumPy:** operações numéricas e cálculos;
* **Altair:** construção de gráficos e visualizações;
* **SciPy:** suporte às análises estatísticas;
* **Statsmodels:** construção e avaliação de modelos estatísticos;
* **Scikit-learn:** ferramentas de modelagem e análise de dados;
* **Git e GitHub:** versionamento e organização do código-fonte.

## 📁 Estrutura do Projeto

O projeto está organizado em diretórios que separam os dados, scripts, componentes e funcionalidades da aplicação.

A estrutura principal contempla:

* **`data/`** – organização dos dados brutos, intermediários e processados;
* **`notebooks/`** – notebooks utilizados na exploração, tratamento e análise dos dados;
* **`dashboard/`** – aplicação principal desenvolvida em Streamlit;
* **`dashboard/pages/`** – páginas e funcionalidades do dashboard;
* **`dashboard/components/`** – componentes reutilizáveis da interface;
* **`dashboard/assets/`** – arquivos de estilização e recursos visuais;

## ☁️ Publicação do Dashboard

A solução foi desenvolvida para disponibilização em ambiente web, permitindo o acesso ao painel por meio de um navegador.

**Acesso ao dashboard publicado:**

[Link]


## 📦 Arquivos da Entrega

A entrega contempla:

* **Scripts em Python:** responsáveis pelo processamento dos dados, cálculos e funcionamento da aplicação;
* **Dashboard interativo:** plataforma desenvolvida em Streamlit;
* **Documentação técnica:** instruções de execução, descrição das funcionalidades, fontes de dados, fórmulas e limitações;
* **Dados preparados:** base financeira tratada e integrada à aplicação;
* **Dicionário de KPIs e planilha de validação:** documentação de apoio para garantir a consistência dos indicadores.

Todos os arquivos estão organizados nas pastas do projeto.