import re

import altair as alt
import pandas as pd
import streamlit as st

from components.como_interpretar import como_interpretar
from data.load_data import carregar_indicadores
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


def _numero_br(valor, casas=2):
    texto = f"{abs(float(valor)):,.{casas}f}".replace(",", "X")
    texto = texto.replace(".", ",").replace("X", ".")
    sinal = "−" if float(valor) < 0 else ""
    return f"{sinal}{texto}"


def _moeda_mi(valor):
    if abs(float(valor)) >= 1000:
        return f"R$ {_numero_br(float(valor) / 1000)} bi"

    return f"R$ {_numero_br(valor)} mi"


def _formatar_valor(valor, formato):
    if formato == "moeda":
        return _moeda_mi(valor)

    if formato == "percentual":
        return f"{_numero_br(valor)}%"

    if formato == "dias":
        return f"{_numero_br(valor, 1)} dias"

    if formato == "multiplo":
        return f"{_numero_br(valor)}x"

    return _numero_br(valor)


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


def _grafico_ranking(dados, titulo, indicador, formato, chave, cor, ordem):
    with st.container(key=chave):
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
        elif formato == "multiplo":
            eixo = indicador + " (vezes)"
        else:
            eixo = indicador

        grafico = (
            alt.Chart(dados)
            .mark_bar(color=cor, cornerRadiusEnd=4)
            .encode(
                x=alt.X(
                    "Valor:Q",
                    title=eixo,
                    axis=alt.Axis(labelAngle=0, format=",.1f"),
                ),
                y=alt.Y(
                    "Cenário:N",
                    sort=ordem,
                    title=None,
                ),
                tooltip=[
                    alt.Tooltip("Cenário:N"),
                    alt.Tooltip("Valor:Q", title=indicador, format=",.2f"),
                ],
            )
            .properties(height=360)
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
            .reset_index(drop=True)
        )

        if dados_ano.empty:
            st.warning(
                f"Não há valores de {indicador} disponíveis para o ano {ano}."
            )
            return

        formato = INDICADORES[indicador]["formato"]

        if formato == "moeda":
            fator = 1 / 1_000_000
        elif formato == "percentual":
            fator = 100
        else:
            fator = 1

        dados_ano["Valor"] = dados_ano[indicador] * fator
        dados_ano["Cenário"] = dados_ano["Cenario"].map(_rotulo_cenario)
        dados_ano["Posição"] = range(1, len(dados_ano) + 1)

        maior = dados_ano.iloc[0]
        menor = dados_ano.iloc[-1]

        col_topo, col_base = st.columns(2, gap="medium")

        with col_topo:
            with st.container(key="rank_kpi_topo"):
                _card_metrica(
                    f"Maior {indicador}",
                    _formatar_valor(maior["Valor"], formato),
                    f"{maior['Cenário']} · Ano {ano}",
                )

        with col_base:
            with st.container(key="rank_kpi_base"):
                _card_metrica(
                    f"Menor {indicador}",
                    _formatar_valor(menor["Valor"], formato),
                    f"{menor['Cenário']} · Ano {ano}",
                )

        quantidade = min(10, len(dados_ano))

        maiores = dados_ano.head(quantidade)
        menores = dados_ano.tail(quantidade).sort_values(
            "Valor", ascending=True
        )

        col_maiores, col_menores = st.columns(2, gap="medium")

        with col_maiores:
            _grafico_ranking(
                maiores,
                f"{quantidade} maiores cenários — {indicador}",
                indicador,
                formato,
                "rank_maiores",
                "#1677E8",
                "-x",
            )

        with col_menores:
            _grafico_ranking(
                menores,
                f"{quantidade} menores cenários — {indicador}",
                indicador,
                formato,
                "rank_menores",
                "#E7A23B",
                "x",
            )

        with st.expander(
            f"Ver lista completa dos {len(dados_ano)} cenários",
            icon=":material/format_list_numbered:",
        ):
            lista = dados_ano[["Posição", "Cenário", "Valor"]].copy()
            lista[f"{indicador}"] = lista["Valor"].apply(
                lambda valor: _formatar_valor(valor, formato)
            )
            lista = lista[["Posição", "Cenário", indicador]]

            st.dataframe(
                lista,
                hide_index=True,
                use_container_width=True,
                height=420,
            )

        como_interpretar(
            "rank",
            [
                "**Posição:** os cenários são ordenados do maior para o menor "
                "valor do indicador no ano escolhido.",
                "**Maiores e menores:** os dois gráficos mostram os 10 extremos "
                "da lista. A lista completa fica no quadro abaixo deles.",
                "**Maior nem sempre é melhor:** em prazos (PMR, ciclo "
                "financeiro), necessidade de capital de giro e endividamento, "
                "valores menores costumam ser favoráveis.",
                "**Valores vazios:** cenários sem valor para o indicador no ano "
                "não entram no ranking. Indicadores que usam o ano anterior não "
                "existem no Ano 1.",
            ],
        )

        st.caption(
            "Fonte: aba _Indicadores da planilha Analise_Financeira.xlsx. "
            "O ranking considera a média dos registros de cada cenário "
            "no ano selecionado."
        )