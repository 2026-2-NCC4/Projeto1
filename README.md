# FECAP - Fundação de Comércio Álvares Penteado

<p align="center">
<a href= "https://www.fecap.br/"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhZPrRa89Kma0ZZogxm0pi-tCn_TLKeHGVxywp-LXAFGR3B1DPouAJYHgKZGV0XTEf4AE&usqp=CAU" alt="FECAP - Fundação de Comércio Álvares Penteado" border="0"></a>
</p>

# CTI Analytics

## Atlas

## Integrantes: <a href="https://github.com/rafafmorais">Rafaela Florêncio Morais</a>, <a href="https://github.com/juliaa-pg">Julia Pereira Godinho</a> e <a href="https://github.com/Mariana851">Mariana Almeida Nascimento</a> 

## Professores Orientadores: <a href="https://www.linkedin.com/in/eduardo-savino/">Eduardo Savino Gomes</a>, <a href="https://www.linkedin.com/in/luisspires/">Luis Pires</a>, <a href="https://www.linkedin.com/in/mauricio-lopes-42b8b33a3/">Mauricio Lopes</a> e <a href="https://www.linkedin.com/in/professorrodnil/">Rodnil da Silva Moreira Lisboa</a>

## Descrição

<p align="center">
  <img src="imagens/ctilogo.png" alt="CTI Analytics" width="500">
</p>


O projeto consiste no desenvolvimento de uma Plataforma Analítica de Planejamento Financeiro, criada para transformar dados financeiros brutos em informações úteis para a tomada de decisões. A solução realiza a coleta, preparação, integração e análise dos dados, permitindo identificar padrões, comparar períodos e acompanhar indicadores financeiros e operacionais.

A plataforma também disponibiliza relatórios gerenciais e um dashboard interativo, com no mínimo cinco indicadores, filtros e visualizações. Dessa forma, os usuários podem acompanhar KPIs, analisar relações entre variáveis, avaliar cenários e realizar análises de sensibilidade, apoiando decisões estratégicas e operacionais com base nos dados.
<br><br>

## 🛠 Estrutura de pastas

<pre>
│
├── data
│   ├── raw                      # base original (Demonstrativo Fecap v3.csv)
│   └── staging                  # bases normalizadas e resumo estatístico
│
├── documentos
│   └── entrega 1
│       ├── análise inferencial de dados
│       ├── contabilidade e finanças
│       ├── ES e ML
│       └── pi_ciência de dados
│
├── imagens
│
├── notebooks
│   ├── 01_exploracao.ipynb
│   ├── 02_tratamento.ipynb
│   └── 03_kpis.ipynb
│
├── staging                      # dados_tratados.csv (gerado pelo notebook 02)
│
└── README.md
</pre>


## 💻 Como executar

### 1. Pré-requisitos

- <a href="https://www.python.org/downloads/">Python 3</a>
- Jupyter Notebook (ou VS Code / JupyterLab)

### 2. Instalar as bibliotecas

Todas as bibliotecas usadas nos notebooks do projeto precisam estar instaladas:

| Biblioteca | Uso no projeto |
|---|---|
| `pandas` | leitura, tratamento e exportação dos dados |
| `numpy` | cálculos numéricos |
| `matplotlib` | gráficos |
| `seaborn` | gráficos estatísticos |
| `scipy` | funções estatísticas (notebook de análise descritiva) |
| `openpyxl` | geração e formatação da planilha Excel de KPIs |
| `jupyter` | execução dos notebooks |

Instale tudo de uma vez pelo terminal:

```sh
pip install pandas numpy matplotlib seaborn scipy openpyxl jupyter
```

### 3. Executar os notebooks

Abra o Jupyter a partir da pasta do projeto:

```sh
jupyter notebook
```

Em seguida, abra cada notebook e execute todas as células com **Run All** (menu *Cell > Run All* no Jupyter Notebook, ou *Run > Run All Cells* no JupyterLab / VS Code).

Execute os notebooks da pasta `notebooks` **nesta ordem**, pois cada um usa arquivos gerados pelo anterior:

1. `01_exploracao.ipynb` – exploração da base original (`data/raw/Demonstrativo Fecap v3.csv`)
2. `02_tratamento.ipynb` – limpeza e transformação; gera `staging/dados_tratados.csv`
3. `03_kpis.ipynb` – cálculo dos indicadores financeiros; gera a planilha `Analise_Financeira.xlsx`

> ⚠️ Os notebooks usam caminhos relativos (ex.: `../data/raw/...`), então devem ser executados de dentro da pasta `notebooks`, sem mover os arquivos de lugar.

**Notebook de Análise Descritiva** (`documentos/entrega 1/análise inferencial de dados/Entrega1_Analise_Descritiva.ipynb`): esse notebook lê o arquivo `Demonstrativo_Normalizado.csv`, que deve estar na mesma pasta do notebook antes de dar **Run All**.

## 📋 Licença/License
<a href="https://github.com/2026-2-NCC4/Projeto1.git">Atlas - CTI Analytics </a> © 2026 by <a href="https://github.com/2026-2-NCC4/Projeto1.git">Mariana Almeida, Julia Godinho, Rafaela Florêncio Morais</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International</a>
<br><img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" style="max-width: 1em;max-height:1em;margin-left: .2em;"><img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" style="max-width: 1em;max-height:1em;margin-left: .2em;">

## 🎓 Referências

Aqui estão as referências usadas no projeto.

1. <https://github.com/iuricode/readme-template>
2. <https://github.com/gabrieldejesus/readme-model>
3. <https://chooser-beta.creativecommons.org/>
4. <https://www.toptal.com/developers/gitignore>
