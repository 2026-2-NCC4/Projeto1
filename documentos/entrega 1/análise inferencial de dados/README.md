# Entrega 1: Análise Descritiva dos Dados

## Descrição

Este repositório traz a primeira entrega da disciplina, cujo objetivo é fazer a análise descritiva completa dos dados financeiros do projeto (a mesma base trabalhada no Projeto Interdisciplinar, já tratada e normalizada). O trabalho cobre:

- Medidas de posição: média, mediana e moda
- Medidas de dispersão: variância, desvio padrão e coeficiente de variação
- Representações gráficas: histogramas e boxplots, um por indicador
- Identificação de valores atípicos (outliers) pela regra do IQR
- Leitura do comportamento geral, da distribuição e da variabilidade dos principais indicadores financeiros

## Arquivos do repositório

| Arquivo | Descrição |
|---|---|
| `Entrega1_Analise_Descritiva.ipynb` | Notebook Jupyter com todo o código da análise, já executado (gráficos e tabelas inclusos) |
| `Entrega1_RelatorioAD.pdf` | Relatório em PDF com a análise escrita, tabelas e gráficos |

## Sobre a base de dados

Os dados representam uma simulação de Monte Carlo de uma empresa de concessão, com 1.200 cenários financeiros possíveis projetados para cada um dos 12 anos do contrato. As contas estão organizadas em três grupos: Balanço Patrimonial (BAL), Demonstração do Resultado do Exercício (DRE) e Fluxo de Caixa (FLU). Para esta entrega, foram selecionados 6 indicadores principais: Receita, EBITDA, Resultado Líquido, Geração de Caixa, Saldo Final de Caixa e Total do Ativo.

## Como rodar o notebook

O notebook usa Python 3 e as bibliotecas abaixo:

```bash
pip install pandas numpy scipy matplotlib seaborn jupyter
```

A base de dados usada pelo notebook (`Demonstrativo_Normalizado.csv`) está em outra parte do repositório, fora desta entrega. Baixe o notebook e o CSV para a mesma pasta antes de rodar:

```bash
jupyter notebook Entrega1_Analise_Descritiva.ipynb
```

e rodar todas as células (Cell > Run All).

## Principais resultados

- Receita, EBITDA e Total do Ativo têm risco real baixo entre cenários (coeficiente de variação de cerca de 2%, depois de corrigida a mistura entre dispersão e crescimento explicada no notebook).
- Geração de Caixa e Saldo Final de Caixa são os indicadores mais voláteis, com coeficiente de variação entre 33% e 41%, e concentram a maior parte dos cenários atípicos.
- A dispersão entre cenários cresce de forma regular até o Ano 12 para Receita, EBITDA e Resultado Líquido. Já para Saldo Final de Caixa e Total do Ativo, ela cresce até os Anos 10-11 e cai no Ano 12, efeito do encerramento da concessão.

Os detalhes de cada cálculo, com os gráficos e a explicação de cada etapa, estão no notebook e no relatório.
