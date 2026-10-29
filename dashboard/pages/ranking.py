import altair as alt
import pandas as pd
import streamlit as st

from data.load_data import carregar_demonstrativo
from pages.regressao import VARIAVEIS


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


def _card_metrica(rotulo, valor, detalhe):
    st.markdown(
        f"""
        <div class="rank-kpi-label">{rotulo}</div>
        <div class="rank-kpi-value">{valor}</div>
        <div class="rank-kpi-note">{detalhe}</div>
        """,
        unsafe_allow_html=True,
    )


def _grafico_ranking(dados, titulo, chave):
    with st.container(key=chave):
        st.markdown(f'<div class="rank-card-title">{titulo}</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="rank-card-note">EBITDA acumulado no ano selecionado</div>',
            unsafe_allow_html=True,
        )

        grafico = (
            alt.Chart(dados)
            .mark_bar(color="#1677E8", cornerRadiusEnd=4)
            .encode(
                x=alt.X(
                    "Valor:Q",
                    title="EBITDA (R$ mi)",
                    axis=alt.Axis(format=",.1f"),
                ),
                y=alt.Y(
                    "Cenário:N",
                    sort="-x" if "maiores" in chave else "x",
                    title=None,
                ),
                tooltip=[
                    alt.Tooltip("Cenário:N"),
                    alt.Tooltip("Valor:Q", format=",.2f", title="EBITDA (R$ mi)"),
                ],
            )
            .properties(height=300)
        )

        st.altair_chart(grafico, use_container_width=True)


def render_ranking():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="rank_page"):
        try:
            df = carregar_demonstrativo()
        except Exception as erro:
            st.error(f"Não foi possível carregar a base do demonstrativo: {erro}")
            return

        coluna_metrica = VARIAVEIS.get("EBITDA")
        colunas_necessarias = {"Ano", "Cenario", coluna_metrica}
        ausentes = colunas_necessarias.difference(df.columns)

        if ausentes:
            st.error(
                "A base não contém as colunas necessárias para o ranking: "
                + ", ".join(sorted(ausentes))
            )
            return

        anos = sorted(
            pd.to_numeric(df["Ano"], errors="coerce")
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        if not anos:
            st.warning("Não há anos disponíveis para montar o ranking.")
            return

        with st.container(key="rank_topo"):
            titulo, coluna_ano, coluna_botao = st.columns(
                [3.2, 1, 1.3],
                vertical_alignment="bottom",
            )

            with titulo:
                st.markdown(
                    """
                    <div class="rank-eyebrow">PAINEL FINANCEIRO</div>
                    <div class="rank-title">Ranking de cenários</div>
                    <div class="rank-subtitle">
                        Compare os cenários pelo EBITDA no ano escolhido.
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
            pd.to_numeric(df["Ano"], errors="coerce") == ano,
            ["Cenario", coluna_metrica],
        ].copy()

        dados_ano["Cenario"] = pd.to_numeric(
            dados_ano["Cenario"], errors="coerce"
        )
        dados_ano[coluna_metrica] = pd.to_numeric(
            dados_ano[coluna_metrica], errors="coerce"
        )

        dados_ano = (
            dados_ano.dropna()
            .groupby("Cenario", as_index=False)[coluna_metrica]
            .mean()
            .sort_values(coluna_metrica, ascending=False)
        )

        if dados_ano.empty:
            st.warning(f"Não há valores de EBITDA disponíveis para {ano}.")
            return

        dados_ano["Valor"] = dados_ano[coluna_metrica] / 1_000_000
        dados_ano["Cenário"] = dados_ano["Cenario"].map(
            lambda numero: f"Cenário {int(numero)}"
        )

        maior = dados_ano.iloc[0]
        menor = dados_ano.iloc[-1]

        col_topo, col_base = st.columns(2)

        with col_topo:
            with st.container(key="rank_kpi_topo"):
                _card_metrica(
                    "Maior EBITDA",
                    _moeda_mi(maior["Valor"]),
                    f"Cenário {int(maior['Cenario'])} · Ano {ano}",
                )

        with col_base:
            with st.container(key="rank_kpi_base"):
                _card_metrica(
                    "Menor EBITDA",
                    _moeda_mi(menor["Valor"]),
                    f"Cenário {int(menor['Cenario'])} · Ano {ano}",
                )

        maiores = dados_ano.head(10).sort_values("Valor", ascending=True)
        menores = dados_ano.tail(10).sort_values("Valor", ascending=False)

        col_maiores, col_menores = st.columns(2)

        with col_maiores:
            _grafico_ranking(
                maiores,
                "10 maiores cenários",
                "rank_maiores",
            )

        with col_menores:
            _grafico_ranking(
                menores,
                "10 menores cenários",
                "rank_menores",
            )

        st.caption(
            "Fonte: Demonstrativo Normalizado. Valores monetários convertidos "
            "para R$ milhões. O ranking considera os registros do ano selecionado."
        )