"""Relatórios em PDF por página.

Cada página com relatório tem uma função que lê os filtros escolhidos na tela
(no session_state) e devolve (descrição do recorte, função que gera o PDF).
Se um filtro ainda não existir (a página não foi aberta), usa o mesmo valor
inicial da tela. A geração fica em cache para o mesmo recorte.
"""
import unicodedata
from importlib import import_module

import streamlit as st


@st.cache_data(show_spinner=False, max_entries=64)
def _gerar(modulo, *argumentos):
    """Gera o PDF chamando relatorios.<modulo>.gerar(*argumentos), com cache."""
    return import_module(f"relatorios.{modulo}").gerar(*argumentos)


def _anos_demonstrativo():
    from data.load_data import carregar_demonstrativo

    return sorted(carregar_demonstrativo()["Ano"].dropna().astype(int).unique().tolist())


def _primeiro_cenario():
    from data.load_data import carregar_demonstrativo

    return int(carregar_demonstrativo()["Cenario"].dropna().astype(int).min())


def _ultimo_ano_indicadores():
    from data.load_data import carregar_indicadores

    return int(carregar_indicadores()["Ano_Numero"].max())


# ---------- Uma função por página ----------

def _visao_geral(estado):
    ano = estado.get("vg_ano") or _ultimo_ano_indicadores()
    cenario = estado.get("vg_cenario", "Todos os cenários")
    return f"Ano {ano} · {cenario}", lambda: _gerar("visao_geral", int(ano), cenario)


def _indicadores(estado):
    ano = estado.get("ind_filtro_ano") or f"Ano {_ultimo_ano_indicadores()}"
    cenario = estado.get("ind_filtro_cenario", "Todos")
    nome = "Todos os cenários" if cenario == "Todos" else str(cenario)
    if cenario != "Todos":
        from data.load_data import carregar_indicadores
        from pages.indicadores import _mapear_cenarios

        nome = _mapear_cenarios(carregar_indicadores()).get(cenario, cenario)
    return f"{ano} · {nome}", lambda: _gerar("indicadores", ano, cenario)


def _tendencia(estado):
    from pages.tendencias import INDICADORES

    indicador = estado.get("tend_indicador") or list(INDICADORES)[1]
    anos = _anos_demonstrativo()
    # Mesma regra da tela: se o período não for um par (início, fim) válido,
    # usa todos os anos
    periodo = estado.get("tend_periodo")
    if (
        not isinstance(periodo, (tuple, list))
        or len(periodo) != 2
        or periodo[0] not in anos
        or periodo[1] not in anos
    ):
        periodo = (anos[0], anos[-1])
    periodo = tuple(int(a) for a in periodo)
    cenario = estado.get("tend_cenario") or _primeiro_cenario()
    secundario = estado.get("tend_secundario") or "Nenhum"
    return (
        f"{indicador} · Ano {periodo[0]} a {periodo[1]} · Cenário {cenario}",
        lambda: _gerar("tendencia", indicador, periodo, int(cenario), secundario),
    )


def _comparacao(estado):
    from pages.comparacao import _preparar_dados, _rotulo_cenario, cenarios_padrao

    ano = estado.get("comp_ano")
    cenarios = estado.get("comp_cenarios")
    if ano is None or not cenarios:
        df = _preparar_dados()
        ano = ano if ano is not None else int(df["Ano_Numero"].max())
        cenarios = cenarios or cenarios_padrao(df.loc[df["Ano_Numero"] == ano])
    cenarios = tuple(cenarios)
    nomes = ", ".join(_rotulo_cenario(c) for c in cenarios)
    return f"Ano {ano} · {nomes}", lambda: _gerar("comparacao", int(ano), cenarios)


def _ranking(estado):
    ano = estado.get("rank_ano") or _ultimo_ano_indicadores()
    indicador = estado.get("rank_indicador") or "EBITDA"
    return f"Ano {ano} · {indicador}", lambda: _gerar("ranking", int(ano), indicador)


def _metas(estado):
    ano = estado.get("meta_ano") or _anos_demonstrativo()[-1]
    cenario = estado.get("meta_cenario") or _primeiro_cenario()
    percentil = estado.get("meta_percentil") or 75
    escolhidos = tuple(estado.get("meta_indicadores") or ())
    return (
        f"Ano {ano} · Cenário {cenario} · meta no percentil {percentil}",
        lambda: _gerar("metas", int(ano), int(cenario), int(percentil), escolhidos),
    )


def _sensibilidade(estado):
    ano = estado.get("sens_ano") or _anos_demonstrativo()[-1]
    cenario = estado.get("sens_cenario") or _primeiro_cenario()
    fator = estado.get("sens_fator_simulacao") or "WACC"
    variacao = estado.get("sens_variacao_simulacao", 10) / 100
    return (
        f"Ano {ano} · Cenário {cenario} · simulação {fator} {variacao * 100:+.0f}%",
        lambda: _gerar("sensibilidade", int(ano), int(cenario), fator, variacao),
    )


def _simulador(estado):
    from pages.simulador import MEDIA_CENARIOS, PREMISSAS

    ano = estado.get("sim_ano") or _anos_demonstrativo()[-1]
    cenario = estado.get("sim_cenario", MEDIA_CENARIOS)
    premissas = tuple(
        (chave, estado.get(f"sim_premissa_{chave}", 0) / 100) for chave in PREMISSAS
    )
    nome = cenario if cenario == MEDIA_CENARIOS else f"Cenário {cenario}"
    mudancas = ", ".join(
        f"{PREMISSAS[k]} {v * 100:+.0f}%" for k, v in premissas if v
    ) or "sem premissas alteradas"
    return (
        f"Ano {ano} · {nome} · {mudancas}",
        lambda: _gerar("simulador", int(ano), cenario, dict(premissas)),
    )


def _regressao(estado):
    ano = estado.get("reg_ano") or _anos_demonstrativo()[-1]
    cenario = estado.get("reg_cenario") or _primeiro_cenario()
    return f"Ano {ano} · Cenário {cenario} em destaque", lambda: _gerar("regressao", int(ano), int(cenario))


def _insights(estado):
    from data.load_data import carregar_demonstrativo
    from pages.insights import cenario_padrao

    ano, cenario = estado.get("ins_ano"), estado.get("ins_cenario")
    if ano is None or cenario is None:
        df = carregar_demonstrativo()
        ano = ano if ano is not None else int(df["Ano"].max())
        cenario = cenario if cenario is not None else cenario_padrao(df)
    return f"Ano {ano} · Cenário {cenario}", lambda: _gerar("insights", int(ano), int(cenario))


# Nome da página (como no menu) -> função que monta o relatório
RELATORIOS = {
    "Visão Geral": _visao_geral,
    "Indicadores": _indicadores,
    "Tendência": _tendencia,
    "Comparação": _comparacao,
    "Ranking": _ranking,
    "Metas x Realizado": _metas,
    "Sensibilidade": _sensibilidade,
    "Simular novo cenário": _simulador,
    "Regressão": _regressao,
    "Insights": _insights,
}

# Páginas de conta e ajuda não têm números para relatar
SEM_RELATORIO = {"Configurações", "Ajuda"}


def _slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "_".join(
        "".join(c if c.isalnum() else " " for c in texto.lower()).split()
    )[:80]


def relatorio_da_pagina(pagina, estado):
    """(nome do arquivo, descrição do recorte, gerar) ou None se a página não tem relatório."""
    montar = RELATORIOS.get(pagina)
    if montar is None:
        return None

    recorte, gerar = montar(estado)
    nome_arquivo = f"CTI_relatorio_{_slug(pagina)}_{_slug(recorte)}.pdf"
    return nome_arquivo, recorte, gerar
