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


def _grafico_ranking(dados, titulo, indicador, formato, chave, ordem):
    unidades = {
        "moeda": "R$ milhões",
        "percentual": "%",
        "dias": "dias",
        "multiplo": "vezes",
        "numero": "unidades",
    }

    unidade = unidades.get(formato, "unidades")

    with st.container(key=chave):
        st.markdown(
            f'<div class="rank-card-title">{titulo}</div>',
            unsafe_allow_html=True,
        )

        grafico = (
            alt.Chart(dados)
            .mark_bar(color="#1677E8", cornerRadiusEnd=4)
            .encode(
                x=alt.X(
                    "Valor_Grafico:Q",
                    title=f"{indicador} ({unidade})",
                    axis=alt.Axis(format=",.2f"),
                ),
                y=alt.Y(
                    "Cenário:N",
                    sort=alt.SortField(
                        field="Valor_Grafico",
                        order=ordem,
                    ),
                    title=None,
                ),
                tooltip=[
                    alt.Tooltip("Cenário:N", title="Cenário"),
                    alt.Tooltip(
                        "Valor_Grafico:Q",
                        title=f"{indicador} ({unidade})",
                        format=",.2f",
                    ),
                ],
            )
            .properties(height=350)
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

        if not anos:
            st.warning("Não há anos disponíveis para análise.")
            return

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
                        Compare os resultados dos cenários por indicador financeiro.
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
            pd.to_numeric(df["Ano_Numero"], errors="coerce").eq(ano),
            ["Cenario", indicador],
        ].copy()

        dados_ano[indicador] = pd.to_numeric(
            dados_ano[indicador],
            errors="coerce",
        )

        dados_ano = (
            dados_ano.dropna(subset=["Cenario", indicador])
            .groupby("Cenario", as_index=False)[indicador]
            .mean()
        )

        if dados_ano.empty:
            st.warning(
                f"Não há valores de {indicador} disponíveis para {ano}."
            )
            return

        formato = INDICADORES[indicador]["formato"]

        unidades = {
            "moeda": "R$ milhões",
            "percentual": "%",
            "dias": "dias",
            "multiplo": "vezes",
            "numero": "unidades",
        }

        unidade = unidades.get(formato, "unidades")

        divisor = 1_000_000 if formato == "moeda" else 1

        dados_ano["Valor"] = dados_ano[indicador] / divisor

        escala = 1

        if formato == "percentual":
            if dados_ano["Valor"].abs().median() <= 1.5:
                escala = 100

        dados_ano["Valor_Grafico"] = dados_ano["Valor"] * escala
        dados_ano["Cenário"] = dados_ano["Cenario"].map(_rotulo_cenario)

        maiores = dados_ano.nlargest(10, "Valor").sort_values(
            "Valor",
            ascending=False,
        )

        menores = dados_ano.nsmallest(10, "Valor").sort_values(
            "Valor",
            ascending=True,
        )

        maior = dados_ano.loc[dados_ano["Valor"].idxmax()]
        menor = dados_ano.loc[dados_ano["Valor"].idxmin()]

        media = dados_ano["Valor"].mean()
        amplitude = maior["Valor"] - menor["Valor"]
        total_cenarios = len(dados_ano)

        def formatar_card(valor):
            valor = valor * escala

            if formato == "moeda":
                return _moeda_mi(valor)

            if formato == "percentual":
                return f"{valor:.2f}%".replace(".", ",")

            if formato == "dias":
                return f"{valor:.1f} dias".replace(".", ",")

            if formato == "multiplo":
                return f"{valor:.2f} vezes".replace(".", ",")

            return f"{valor:.2f}".replace(".", ",")

        col_maior, col_menor = st.columns(2)

        with col_maior:
            with st.container(key="rank_kpi_topo"):
                _card_metrica(
                    f"Maior {indicador}",
                    formatar_card(maior["Valor"]),
                    f"{maior['Cenário']} · Ano {ano}",
                )

        with col_menor:
            with st.container(key="rank_kpi_base"):
                _card_metrica(
                    f"Menor {indicador}",
                    formatar_card(menor["Valor"]),
                    f"{menor['Cenário']} · Ano {ano}",
                )

        st.markdown("### Insights do ranking")

        st.info(
            f"O ranking apresenta os valores de **{indicador} ({unidade})** "
            f"no ano de **{ano}**. Foram analisados **{total_cenarios} "
            f"cenários**, considerando a média dos registros de cada cenário."
        )

        col_media, col_amplitude, col_quantidade = st.columns(3)

        with col_media:
            with st.container(border=True):
                _card_metrica(
                    "Média dos cenários",
                    formatar_card(media),
                    f"Média de {total_cenarios} cenários",
                )

        with col_amplitude:
            with st.container(border=True):
                _card_metrica(
                    "Diferença entre extremos",
                    formatar_card(amplitude),
                    "Maior valor menos menor valor",
                )

        with col_quantidade:
            with st.container(border=True):
                _card_metrica(
                    "Cenários analisados",
                    str(total_cenarios),
                    f"Ano de referência: {ano}",
                )

        st.markdown(
            f"""
            - **Maior resultado numérico:** {maior['Cenário']}, com
              {formatar_card(maior['Valor'])}.
            - **Menor resultado numérico:** {menor['Cenário']}, com
              {formatar_card(menor['Valor'])}.
            - **Amplitude:** a diferença entre os extremos é de
              {formatar_card(amplitude)}.
            """
        )

        st.markdown("### Comparação dos cenários")

        col_maiores, col_menores = st.columns(2, gap="medium")

        with col_maiores:
            _grafico_ranking(
                maiores,
                f"10 maiores — {indicador}",
                indicador,
                formato,
                "rank_grafico_maiores",
                "descending",
            )

        with col_menores:
            _grafico_ranking(
                menores,
                f"10 menores — {indicador}",
                indicador,
                formato,
                "rank_grafico_menores",
                "ascending",
            )

        with st.expander("Consultar listas completas dos rankings"):
            tabela_maiores = maiores[
                ["Cenário", "Valor_Grafico"]
            ].copy()

            tabela_maiores.insert(
                0,
                "Posição",
                range(1, len(tabela_maiores) + 1),
            )

            tabela_maiores = tabela_maiores.rename(
                columns={"Valor_Grafico": f"{indicador} ({unidade})"}
            )

            tabela_menores = menores[
                ["Cenário", "Valor_Grafico"]
            ].copy()

            tabela_menores.insert(
                0,
                "Posição",
                range(1, len(tabela_menores) + 1),
            )

            tabela_menores = tabela_menores.rename(
                columns={"Valor_Grafico": f"{indicador} ({unidade})"}
            )

            lista_maiores, lista_menores = st.columns(2)

            with lista_maiores:
                st.markdown("**10 maiores cenários**")
                st.table(tabela_maiores)

            with lista_menores:
                st.markdown("**10 menores cenários**")
                st.table(tabela_menores)

        st.caption(
            "Fonte: aba _Indicadores da planilha Analise_Financeira.xlsx. "
            "Os valores representam a média dos registros de cada cenário "
            "no ano selecionado. A classificação é numérica e não significa, "
            "necessariamente, melhor ou pior desempenho."
        )