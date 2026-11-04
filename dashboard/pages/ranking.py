import re

import altair as alt
import pandas as pd
import streamlit as st

from data.load_data import carregar_demonstrativo, carregar_indicadores
from pages.indicadores import INDICADORES


PAGE_STYLE = """
<style>
    .st-key-rank_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .rank-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .rank-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .rank-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .st-key-rank_topo label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-rank_kpi_topo,
    .st-key-rank_kpi_base,
    .st-key-rank_maiores,
    .st-key-rank_menores {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
    }

    .rank-kpi-label {
        font-size: 12px;
        color: var(--cti-muted);
    }

    .rank-kpi-value {
        font-size: clamp(20px, 1.9vw, 26px);
        white-space: nowrap;
        font-weight: 700;
        color: var(--cti-blue);
        line-height: 1.3;
    }

    .rank-kpi-note {
        font-size: 11px;
        color: #8AA4BF;
    }

    .rank-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
        margin-bottom: 2px;
    }

    .rank-card-note {
        font-size: 11px;
        color: #8AA4BF;
        margin-bottom: 10px;
    }
</style>
"""


def _moeda_mi(valor):
    texto = f"{abs(float(valor)):,.2f}".replace(",", "X")
    texto = texto.replace(".", ",").replace("X", ".")
    sinal = "−" if float(valor) < 0 else ""
    return f"{sinal}R$ {texto} mi"


def _rotulo_cenario(valor):
    if pd.isna(valor):
        return "Cenário sem identificação"

    try:
        return f"Cenário {int(float(valor))}"
    except (TypeError, ValueError):
        pass

    encontrados = re.findall(r"\d+", str(valor))

    if encontrados:
        return f"Cenário {int(encontrados[-1])}"

    return str(valor).strip()


def _card_metrica(rotulo, valor, detalhe):
    st.markdown(
        f"""
        <div class="rank-kpi-label">{rotulo}</div>
        <div class="rank-kpi-value">{valor}</div>
        <div class="rank-kpi-note">{detalhe}</div>
        """,
        unsafe_allow_html=True,
    )


def _grafico_ranking(dados, titulo, indicador, formato):
    with st.container(key="rank_grafico"):
        st.markdown(
            f'<div class="rank-card-title">{titulo}</div>',
            unsafe_allow_html=True,
        )

        if formato == "moeda":
            eixo = f"{indicador} (R$ milhões)"
        elif formato == "percentual":
            eixo = indicador + " (%)"
        elif formato == "dias":
            eixo = indicador + " (dias)"
        else:
            eixo = indicador

        grafico = (
            alt.Chart(dados)
            .mark_bar(color="#1677E8", cornerRadiusEnd=4)
            .encode(
                x=alt.X(
                    "Valor:Q",
                    title=eixo,
                ),
                y=alt.Y(
                    "Cenário:N",
                    sort="-x",
                    title=None,
                ),
                tooltip=[
                    alt.Tooltip("Cenário:N"),
                    alt.Tooltip("Valor:Q", title=indicador, format=",.3f"),
                ],
            )
            .properties(height=420)
        )

        st.altair_chart(grafico, use_container_width=True)


def render_ranking():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="rank_page"):
        try:
            df = carregar_indicadores()
        except Exception as erro:
            st.error(f"Não foi possível carregar os indicadores: {erro}")
            return

        indicadores_disponiveis = [
            nome for nome in INDICADORES
            if nome in df.columns
        ]

        if not indicadores_disponiveis:
            st.warning("Não há indicadores disponíveis para o ranking.")
            return

        anos = sorted(
            pd.to_numeric(df["Ano_Numero"], errors="coerce")
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        with st.container(key="rank_topo"):
            titulo, coluna_ano, coluna_metrica, coluna_botao = st.columns(
                [2.7, 1, 1.4, 1.3],
                vertical_alignment="bottom",
            )

            with titulo:
                st.markdown(
                    """
                    <div class="rank-eyebrow">PAINEL FINANCEIRO</div>
                    <div class="rank-title">Ranking de cenários</div>
                    <div class="rank-subtitle">
                        Classifique os cenários pelo indicador selecionado.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with coluna_ano:
                ano = st.selectbox(
                    "Ano",
                    options=anos,
                    index=len(anos) - 1,
                    key="rank_ano",
                )

            with coluna_metrica:
                indicador = st.selectbox(
                    "Indicador",
                    options=indicadores_disponiveis,
                    index=indicadores_disponiveis.index("EBITDA")
                    if "EBITDA" in indicadores_disponiveis else 0,
                    key="rank_indicador",
                )

            with coluna_botao:
                if st.button(
                    "Nova simulação",
                    icon=":material/add:",
                    key="rank_nova_simulacao",
                    use_container_width=True,
                ):
                    st.session_state.pagina_atual = "Simular novo cenário"
                    st.rerun()

        dados_ano = df.loc[
            df["Ano_Numero"].eq(ano),
            ["Cenario", indicador],
        ].copy()

        dados_ano[indicador] = pd.to_numeric(
            dados_ano[indicador],
            errors="coerce",
        )

        dados_ano = (
            dados_ano.dropna()
            .groupby("Cenario", as_index=False)[indicador]
            .mean()
            .sort_values(indicador, ascending=False)
        )

        if dados_ano.empty:
            st.warning(
                f"Não há valores de {indicador} disponíveis para o ano {ano}."
            )
            return

        formato = INDICADORES[indicador]["formato"]

        divisor = 1_000_000 if formato == "moeda" else 1
        dados_ano["Valor"] = dados_ano[indicador] / divisor

        dados_ano["Cenário"] = dados_ano["Cenario"].map(_rotulo_cenario)

        maior = dados_ano.iloc[0]
        menor = dados_ano.iloc[-1]

        col_topo, col_base = st.columns(2)

        with col_topo:
            with st.container(key="rank_kpi_topo"):
                valor = (
                    _moeda_mi(maior["Valor"])
                    if formato == "moeda"
                    else f"{maior['Valor']:.2f}"
                )
                _card_metrica(
                    f"Maior {indicador}",
                    valor,
                    f"{maior['Cenário']} · Ano {ano}",
                )

        with col_base:
            with st.container(key="rank_kpi_base"):
                valor = (
                    _moeda_mi(menor["Valor"])
                    if formato == "moeda"
                    else f"{menor['Valor']:.2f}"
                )
                _card_metrica(
                    f"Menor {indicador}",
                    valor,
                    f"{menor['Cenário']} · Ano {ano}",
                )

        _grafico_ranking(
            dados_ano.head(10).sort_values("Valor", ascending=True),
            f"10 maiores cenários — {indicador}",
            indicador,
            formato,
        )

        st.caption(
            "Fonte: aba _Indicadores da planilha Analise_Financeira.xlsx. "
            "O ranking considera a média dos registros de cada cenário "
            "no ano selecionado."
        )