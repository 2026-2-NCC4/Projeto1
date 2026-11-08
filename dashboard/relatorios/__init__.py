"""Relatórios em PDF por página.

Cada página com relatório tem uma função que lê os filtros escolhidos na tela
(no session_state) e devolve (nome do arquivo, descrição do recorte, função
que gera o PDF). A geração fica em cache para o mesmo recorte.
"""
import unicodedata

import streamlit as st


@st.cache_data(show_spinner=False, max_entries=32)
def _pdf_visao_geral(ano, cenario):
    from relatorios import visao_geral

    return visao_geral.gerar(ano, cenario)


@st.cache_data(show_spinner=False, max_entries=32)
def _pdf_insights(ano, cenario):
    from relatorios import insights

    return insights.gerar(ano, cenario)


def _visao_geral(estado):
    from data.load_data import carregar_indicadores

    ano = estado.get("vg_ano")
    if ano is None:
        ano = int(carregar_indicadores()["Ano_Numero"].max())
    cenario = estado.get("vg_cenario", "Todos os cenários")
    return f"Ano {ano} · {cenario}", lambda: _pdf_visao_geral(int(ano), cenario)


def _insights(estado):
    from data.load_data import carregar_demonstrativo
    from pages.insights import cenario_padrao

    ano, cenario = estado.get("ins_ano"), estado.get("ins_cenario")
    if ano is None or cenario is None:
        df = carregar_demonstrativo()
        ano = ano if ano is not None else int(df["Ano"].max())
        cenario = cenario if cenario is not None else cenario_padrao(df)
    return f"Ano {ano} · Cenário {cenario}", lambda: _pdf_insights(int(ano), int(cenario))


# Nome da página (como no menu) -> função que monta o relatório
RELATORIOS = {
    "Visão Geral": _visao_geral,
    "Insights": _insights,
}


def _slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "_" for c in texto.lower()).strip("_")


def relatorio_da_pagina(pagina, estado):
    """(nome do arquivo, descrição do recorte, gerar) ou None se a página não tem relatório."""
    montar = RELATORIOS.get(pagina)
    if montar is None:
        return None

    recorte, gerar = montar(estado)
    nome_arquivo = f"CTI_relatorio_{_slug(pagina)}_{_slug(recorte)}.pdf"
    return nome_arquivo, recorte, gerar
