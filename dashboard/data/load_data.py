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