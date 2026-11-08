# 📊 Entrega 02 – Painel Financeiro Operacional

## 📖 Descrição

Esta etapa do projeto consiste no desenvolvimento de um **painel financeiro operacional** integrado à plataforma CTI Analytics, com o objetivo de transformar os dados financeiros da CTI Global em informações visuais e estratégicas para acompanhamento do desempenho da empresa.

O dashboard foi desenvolvido utilizando **Python e Streamlit**, permitindo explorar os indicadores financeiros, acompanhar sua evolução ao longo dos anos e comparar o desempenho entre diferentes cenários.

A implementação contempla a organização dos indicadores em páginas específicas, proporcionando uma visão mais clara, dinâmica e integrada dos resultados financeiros.

## 📈 Funcionalidades Implementadas

O dashboard reúne diferentes perspectivas de análise financeira e estatística, organizadas nas seguintes páginas:

* **Visão Geral:** apresenta um resumo do desempenho financeiro por meio de indicadores-chave (KPIs), gráficos de evolução e informações relevantes para a tomada de decisão;
* **Indicadores:** reúne os principais indicadores financeiros calculados a partir das demonstrações contábeis, permitindo acompanhar os resultados da empresa;
* **Tendência:** apresenta a evolução dos indicadores ao longo dos anos, possibilitando identificar comportamentos e tendências financeiras;
* **Comparação:** permite analisar e comparar o desempenho financeiro entre diferentes cenários;
* **Ranking:** organiza os cenários de acordo com seu desempenho nos indicadores financeiros, facilitando a identificação dos melhores resultados;
* **Regressão:** disponibiliza análises estatísticas e modelos de regressão para investigar relações entre variáveis financeiras, identificar padrões e avaliar possíveis tendências;
* **Insights:** apresenta interpretações dos resultados financeiros e estatísticos, destacando informações relevantes, variações e oportunidades identificadas a partir dos dados.

## 📊 Indicadores Financeiros

O painel contempla indicadores relacionados ao desempenho econômico-financeiro da empresa, incluindo:

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

Os indicadores são apresentados por meio de cards, gráficos e comparações, facilitando a interpretação dos resultados e o acompanhamento do desempenho financeiro.

## 📉 Evolução e Comparação Financeira

Foram desenvolvidas visualizações para acompanhar o comportamento dos indicadores ao longo dos anos.

As análises permitem:

* Acompanhar a evolução da receita e do EBITDA;
* Observar o comportamento das margens financeiras;
* Comparar resultados entre períodos;
* Identificar variações no desempenho financeiro;
* Analisar diferenças entre os cenários disponíveis na base.

## 📈 Análise de Regressão

A página de Regressão contempla análises estatísticas para investigar o relacionamento entre variáveis financeiras.

Por meio de modelos de regressão, é possível:

* Investigar relações entre indicadores financeiros;
* Avaliar a influência de variáveis explicativas sobre uma variável de interesse;
* Analisar os resultados estatísticos dos modelos;
* Identificar tendências e padrões presentes nos dados;
* Apoiar a interpretação do comportamento financeiro da empresa.

## 💡 Insights Financeiros

A página de Insights reúne interpretações e informações extraídas das análises realizadas no dashboard.

Seu objetivo é transformar os resultados numéricos em informações mais acessíveis, destacando:

* Variações relevantes nos indicadores;
* Evolução do desempenho financeiro;
* Pontos de atenção identificados nos resultados;
* Comparações entre períodos e cenários;
* Informações que podem auxiliar na tomada de decisão.

## 🎯 Metas e Análise de Sensibilidade

A entrega também contempla a proposta de acompanhamento de metas financeiras, permitindo relacionar os resultados obtidos com referências de desempenho.

Além disso, são consideradas análises de sensibilidade para avaliar como alterações em variáveis relevantes podem impactar os resultados financeiros e as margens da empresa.

Essas análises têm como finalidade apoiar a avaliação de diferentes possibilidades e auxiliar no planejamento financeiro.

## 🖥️ Tecnologias Utilizadas

O desenvolvimento do painel utilizou as seguintes tecnologias:

* **Python** – linguagem principal de desenvolvimento;
* **Streamlit** – construção e disponibilização do dashboard;
* **Pandas e NumPy** – manipulação e processamento dos dados;
* **Altair** – criação de gráficos e visualizações;
* **SciPy** – apoio às análises estatísticas;
* **Statsmodels** – construção e avaliação de modelos estatísticos;
* **Scikit-learn** – apoio à modelagem e análise de dados;
* **Git e GitHub** – versionamento e organização do projeto.

## 📁 Estrutura do Dashboard

O painel foi integrado à estrutura principal da plataforma CTI Analytics, mantendo a organização das páginas e dos componentes visuais.

As funcionalidades estão distribuídas entre as seguintes páginas:

* **Visão Geral;**
* **Indicadores;**
* **Tendência;**
* **Comparação;**
* **Ranking;**
* **Meta Analítica x Meta Realizada**
* **Regressão;**
* **Insights.**

Cada página possui visualizações e recursos próprios, contribuindo para uma análise integrada do desempenho financeiro da empresa.

## ⚠️ Consistência dos Dados

Os indicadores apresentados no dashboard utilizam a base financeira tratada do projeto.

Os cálculos e resultados devem permanecer consistentes com o **Dicionário de KPIs Financeiros** e com a **planilha de validação**, garantindo padronização das fórmulas e confiabilidade das informações apresentadas.

Informações ausentes na base original são tratadas como não disponíveis, evitando a substituição indevida de valores ausentes por zero.

## 📦 Arquivos da Entrega

O código-fonte do dashboard e seus componentes estão organizados na estrutura principal do projeto CTI Analytics.

A implementação pode ser consultada no repositório, na pasta:

**`dashboard/`**

Os arquivos de processamento, carregamento dos dados, componentes visuais, páginas e recursos utilizados na aplicação estão organizados em seus respectivos diretórios.