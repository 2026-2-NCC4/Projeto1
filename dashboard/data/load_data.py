from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]

CAMINHO_PLANILHA = (
    ROOT_DIR
    / "documentos"
    / "entrega 1"
    / "contabilidade e finanças"
    / "Analise_Financeira.xlsx"
)

# Base larga (1.200 cenários x 12 anos) com as contas da DRE, do fluxo
# de caixa e do balanço em colunas. É a mesma usada na análise de regressão.
CAMINHO_DEMONSTRATIVO = (
    ROOT_DIR
    / "documentos"
    / "entrega 1"
    / "análise inferencial de dados"
    / "Demonstrativo_Normalizado.csv"
)


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

    colunas_numericas = [
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
    ]

    for coluna in colunas_numericas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(
                df[coluna], errors="coerce"
            )

    df["Ano_Numero"] = (
        df["Ano"].astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(int)
    )

    return df

#calculando as médias dos indicadores por ano, para exibir no dashboard
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

#carregando a base larga do demonstrativo, usada na página de regressão
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
