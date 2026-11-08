# Entrega 2: Análise Inferencial de Dados

## Descrição

Este repositório traz a segunda entrega da disciplina, cujo objetivo é conduzir uma análise de regressão sobre os dados financeiros do projeto (a mesma base da entrega anterior, já tratada e normalizada). O trabalho cobre:

- Escolha das variáveis do modelo, com análise de correlação para evitar relações puramente contábeis
- Ajuste de uma regressão linear múltipla por mínimos quadrados ordinários (OLS)
- Interpretação dos coeficientes
- Avaliação da qualidade do ajuste (R², R² ajustado) e testes de hipótese (testes t e teste F)
- Diagnósticos dos resíduos: gráficos de resíduos, Q-Q e histograma, testes de Breusch-Pagan, Shapiro-Wilk e Durbin-Watson, e VIF
- Verificação de sensibilidade do modelo
- Registro das limitações da análise

## Arquivos do repositório

| Arquivo | Descrição |
|---|---|
| `Entrega2_Analise_Regressao.ipynb` | Notebook Jupyter com todo o código da análise, já executado (gráficos e tabelas inclusos) |
| `Análise Inferencial - Entrega.pdf` | Relatório técnico em PDF com os resultados, tabelas, gráficos e glossário dos termos |

## Sobre a base de dados

Os dados representam uma simulação de Monte Carlo de uma empresa de concessão, com 1.200 cenários financeiros projetados para cada um dos 12 anos do contrato, totalizando 14.400 observações. Nesta entrega o modelo ajustado é:

**Geração de Caixa = β₀ + β₁ × Resultado Líquido + β₂ × Ano + erro**

Receita, EBITDA e Resultado Líquido têm correlação acima de 0,99 entre si (quase uma identidade contábil), por isso não foram usados para prever uns aos outros. A Geração de Caixa segue uma lógica própria e foi escolhida como variável a explicar.

## Como rodar o notebook

O notebook usa Python 3 e as bibliotecas abaixo:

```bash
pip install pandas numpy scipy matplotlib seaborn statsmodels jupyter
```

A base de dados usada pelo notebook (`Demonstrativo_Normalizado.csv`) está em outra parte do repositório, fora desta entrega. Baixe o notebook e o CSV para a mesma pasta antes de rodar:

```bash
jupyter notebook Entrega2_Analise_Regressao.ipynb
```

e rodar todas as células (Cell > Run All).

## Principais resultados

- O modelo explica cerca de 45% da variação da Geração de Caixa (R² = 0,447), com coeficientes e teste F estatisticamente significativos.
- O coeficiente do Resultado Líquido é negativo (cerca de -0,93), o que contraria a intuição. Dentro de cada ano a relação entre lucro e caixa é positiva em 9 dos 12 anos, e o sinal negativo geral vem principalmente do Ano 12. Sem o Ano 12, os coeficientes do Resultado Líquido e do Ano trocam de sinal e o R² cai para cerca de 0,30.
- Os diagnósticos mostram que as premissas do OLS não são totalmente atendidas: os resíduos se organizam por ano, têm variância não constante, não são normais e são autocorrelacionados.
- Tratando o ano como categoria, o R² sobe para cerca de 0,88. Só o ano já explica cerca de 87,5% da variação, e o Resultado Líquido acrescenta menos de 1 ponto percentual.

Os detalhes de cada cálculo, com os gráficos e a explicação de cada termo, estão no notebook e no relatório.
