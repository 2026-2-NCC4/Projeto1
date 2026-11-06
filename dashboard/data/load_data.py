from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]

CAMINHO_PLANILHA = (
    ROOT_DIR
    / "documentos"
    / "entrega 2"
    / "contabilidade e finanças"
    / "Analise_Financeira.xlsx"
)

CAMINHO_DEMONSTRATIVO = (
    ROOT_DIR
    / "documentos"
    / "entrega 1"
    / "análise inferencial de dados"
    / "Demonstrativo_Normalizado.csv"
)

ABA_DICIONARIO = "Dicionário de KPIs financeiros"

NOMES_EM_PORTUGUES = {
    "Capex / Receita": "Investimentos / Receita",
    "Capex / D&A": "Investimentos / Depreciação",
    "Payout em Caixa": "Distribuição / Lucro Líquido",
}

COLUNAS_NUMERICAS = [
    "Margem EBITDA",
    "Margem Líquida",
    "LC",
    "LS",
    "LI",
    "LG",
    "PCT",
    "CE",
    "IPL",
    "NOPAT",
    "Capital Investido",
    "ROIC",
    "WACC",
    "EVA",
    "MVA Aproximado",
    "EBITDA",
    "ROE",
    "DuPont - Margem Líquida",
    "DuPont - Giro do Ativo",
    "DuPont - Alavancagem",
    "ROE DuPont",
    "CCL",
    "PMR",
    "PMP",
    "Ciclo Financeiro",
    "Necessidade de Capital de Giro",
    "Recebimentos Estimados",
    "Taxa de Conversão da Receita em Caixa",
    "FCO",
    "FCO / EBITDA",
    "FCO / Lucro Líquido",
    "FCL",
    "Investimentos / Receita",
    "Investimentos / Depreciação",
    "Cobertura de Juros",
    "FCO / Dívida Bruta",
    "Distribuição / Lucro Líquido",
    "Cobertura de Dividendos",
]

COLUNAS_MONETARIAS_EM_MIL = [
    "NOPAT",
    "Capital Investido",
    "EVA",
    "MVA Aproximado",
    "EBITDA",
    "CCL",
    "Necessidade de Capital de Giro",
    "Recebimentos Estimados",
    "FCO",
    "FCL",
]


@st.cache_data
def carregar_indicadores():

    if not CAMINHO_PLANILHA.is_file():
        raise FileNotFoundError(
            "A planilha Analise_Financeira.xlsx não foi encontrada. "
            f"Caminho esperado: {CAMINHO_PLANILHA}"
        )

    df = pd.read_excel(
        CAMINHO_PLANILHA,
        sheet_name="_Indicadores",
    )

    df = df.rename(columns=NOMES_EM_PORTUGUES)

    for coluna in COLUNAS_NUMERICAS:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(
                df[coluna], errors="coerce"
            )

    for coluna in COLUNAS_MONETARIAS_EM_MIL:
        if coluna in df.columns:
            df[coluna] = df[coluna] * 1000

    df["Ano_Numero"] = (
        df["Ano"].astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(int)
    )

    return df


@st.cache_data
def carregar_dicionario():

    if not CAMINHO_PLANILHA.is_file():
        raise FileNotFoundError(
            "A planilha Analise_Financeira.xlsx não foi encontrada. "
            f"Caminho esperado: {CAMINHO_PLANILHA}"
        )

    dicionario = pd.read_excel(
        CAMINHO_PLANILHA,
        sheet_name=ABA_DICIONARIO,
        header=3,
    )

    dicionario = dicionario.dropna(how="all")
    dicionario = dicionario.dropna(subset=["Indicador"])

    dicionario["Indicador"] = dicionario["Indicador"].replace(
        NOMES_EM_PORTUGUES
    )

    return dicionario.reset_index(drop=True)


@st.cache_data
def resumir_indicadores():

    df = carregar_indicadores()

    colunas = [
        coluna
        for coluna in [
            "EBITDA",
            "Margem EBITDA",
            "Margem Líquida",
            "EVA",
            "ROIC",
            "Capital Investido",
            "MVA Aproximado",
        ]
        if coluna in df.columns
    ]

    resumo = (
        df.groupby(["Ano_Numero", "Ano"], as_index=False)
        .agg(
            Cenarios=("Cenario", "nunique"),
            **{
                f"{coluna}_Medio": (coluna, "mean")
                for coluna in colunas
            },
        )
        .sort_values("Ano_Numero")
        .reset_index(drop=True)
    )

    return resumo


@st.cache_data
def carregar_demonstrativo():

    if not CAMINHO_DEMONSTRATIVO.is_file():
        raise FileNotFoundError(
            "O arquivo Demonstrativo_Normalizado.csv não foi encontrado. "
            f"Caminho esperado: {CAMINHO_DEMONSTRATIVO}"
        )

    df = pd.read_csv(
        CAMINHO_DEMONSTRATIVO,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )

    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")
    df["Cenario"] = pd.to_numeric(df["Cenario"], errors="coerce").astype("Int64")

    return df