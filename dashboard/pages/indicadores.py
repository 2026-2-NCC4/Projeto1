# pages/indicadores.py

import streamlit as st
import pandas as pd
import plotly.express as px

from data.load_data import carregar_indicadores


PAGE_STYLE = """
<style>
    .ind_page {
        padding: 0.5rem 0 2rem 0;
    }

    .ind_intro {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: -8px;
        margin-bottom: 22px;
    }

    .ind_section {
        color: #172b4d;
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 28px;
        margin-bottom: 12px;
    }

    .ind_card {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 12px;
        padding: 17px 18px;
        min-height: 112px;
        box-shadow: 0 2px 7px rgba(15, 23, 42, 0.035);
    }

    .ind_card_label {
        color: #64748b;
        font-size: 0.83rem;
        font-weight: 600;
        margin-bottom: 9px;
    }

    .ind_card_value {
        color: #172b4d;
        font-size: 1.45rem;
        font-weight: 750;
        line-height: 1.3;
    }

    .ind_card_caption {
        color: #94a3b8;
        font-size: 0.76rem;
        margin-top: 6px;
    }

    .ind_note {
        background: #f5f8fc;
        border-left: 3px solid #64748b;
        border-radius: 6px;
        padding: 11px 14px;
        color: #475569;
        font-size: 0.86rem;
        margin-top: 12px;
    }
</style>
"""


def _formatar_moeda(valor):
    if pd.isna(valor):
        return "—"

    valor = float(valor)
    formatado = f"{abs(valor):,.2f}"
    formatado = formatado.replace(",", "X").replace(".", ",").replace("X", ".")

    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {formatado}"


def _formatar_percentual(valor):
    if pd.isna(valor):
        return "—"

    valor = float(valor)

    # Identifica percentuais armazenados como decimal ou como número percentual.
    if abs(valor) <= 1.5:
        valor *= 100

    return f"{valor:.2f}%".replace(".", ",")


def _formatar_numero(valor):
    if pd.isna(valor):
        return "—"

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _criar_card(titulo, valor, descricao=""):
    st.markdown(
        f"""
        <div class="ind_card">
            <div class="ind_card_label">{titulo}</div>
            <div class="ind_card_value">{valor}</div>
            <div class="ind_card_caption">{descricao}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _titulo_secao(titulo):
    st.markdown(
        f'<div class="ind_section">{titulo}</div>',
        unsafe_allow_html=True,
    )


def _preparar_serie(df, indicador):
    """
    Quando todos os cenários estão selecionados, calcula a média do indicador
    por ano. Quando um cenário é selecionado, mantém seus valores originais.
    """
    serie = (
        df.groupby(["Ano_Numero", "Ano"], as_index=False)[indicador]
        .mean()
        .sort_values("Ano_Numero")
    )

    return serie


def _grafico_evolucao(df, indicador, titulo, formato="numero"):
    serie = _preparar_serie(df, indicador)

    if serie.empty or serie[indicador].notna().sum() == 0:
        st.info(f"Não há dados disponíveis para {titulo}.")
        return

    fig = px.line(
        serie,
        x="Ano",
        y=indicador,
        markers=True,
        title=titulo,
        labels={
            "Ano": "Ano",
            indicador: titulo,
        },
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7),
        connectgaps=False,
    )

    fig.update_layout(
        template="plotly_white",
        height=330,
        margin=dict(l=15, r=15, t=55, b=15),
        title=dict(font=dict(size=16, color="#172b4d")),
        xaxis=dict(
            categoryorder="array",
            categoryarray=serie["Ano"].tolist(),
        ),
        yaxis=dict(
            tickformat=",.2f",
            separatethousands=True,
        ),
        hovermode="x unified",
    )

    if formato == "moeda":
        fig.update_yaxes(tickprefix="R$ ")

    elif formato == "percentual":
        fig.update_yaxes(ticksuffix="%")

    st.plotly_chart(fig, use_container_width=True)



def render_indicadores():

    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    st.markdown('<div class="ind_page">', unsafe_allow_html=True)

    st.title("Indicadores Financeiros")

    st.markdown(
        """
        <div class="ind_intro">
            Acompanhe os principais indicadores de rentabilidade, liquidez,
            endividamento e geração de valor da empresa.
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = carregar_indicadores().copy()

    except Exception as erro:
        st.error(f"Não foi possível carregar os indicadores: {erro}")
        return

    indicadores_necessarios = [
        "Cenario",
        "Ano",
        "Ano_Numero",
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

    colunas_faltantes = [
        coluna
        for coluna in indicadores_necessarios
        if coluna not in df.columns
    ]

    if colunas_faltantes:
        st.error(
            "A base não possui todas as colunas esperadas: "
            + ", ".join(colunas_faltantes)
        )
        return

    # Ordena os anos cronologicamente.
    anos = (
        df[["Ano", "Ano_Numero"]]
        .drop_duplicates()
        .sort_values("Ano_Numero")["Ano"]
        .tolist()
    )

    cenarios = sorted(df["Cenario"].dropna().unique().tolist())


    _titulo_secao("Filtros")

    col_ano, col_cenario = st.columns(2)

    with col_ano:
        anos_selecionados = st.multiselect(
            "Selecione o(s) ano(s)",
            options=anos,
            default=anos,
            key="indicadores_anos",
        )

    with col_cenario:
        cenario_selecionado = st.selectbox(
            "Selecione o cenário",
            options=["Todos os cenários"] + cenarios,
            key="indicadores_cenario",
        )

    df_filtrado = df[df["Ano"].isin(anos_selecionados)].copy()

    if cenario_selecionado != "Todos os cenários":
        df_filtrado = df_filtrado[
            df_filtrado["Cenario"] == cenario_selecionado
        ]

    if df_filtrado.empty:
        st.warning("Não existem registros para os filtros selecionados.")
        return

    # --------------------------------------------------------
    # INDICADORES EM DESTAQUE
    # --------------------------------------------------------

    _titulo_secao("Resumo dos indicadores")

    indicadores_destaque = [
        ("EBITDA", "EBITDA", "moeda"),
        ("Margem EBITDA", "Margem EBITDA", "percentual"),
        ("Margem Líquida", "Margem Líquida", "percentual"),
        ("ROIC", "ROIC", "percentual"),
    ]

    colunas_cards = st.columns(4)

    for coluna, (nome, campo, formato) in zip(
        colunas_cards,
        indicadores_destaque,
    ):
        media = df_filtrado[campo].mean()

        if formato == "moeda":
            valor_formatado = _formatar_moeda(media)
        else:
            valor_formatado = _formatar_percentual(media)

        with coluna:
            _criar_card(
                nome,
                valor_formatado,
                "Média dos registros filtrados",
            )

    # --------------------------------------------------------
    # RENTABILIDADE
    # --------------------------------------------------------

    _titulo_secao("Rentabilidade")

    col1, col2 = st.columns(2)

    with col1:
        _grafico_evolucao(
            df_filtrado,
            "Margem EBITDA",
            "Evolução da Margem EBITDA",
            "percentual",
        )

    with col2:
        _grafico_evolucao(
            df_filtrado,
            "Margem Líquida",
            "Evolução da Margem Líquida",
            "percentual",
        )

    col1, col2 = st.columns(2)

    with col1:
        _grafico_evolucao(
            df_filtrado,
            "ROIC",
            "Evolução do ROIC",
            "percentual",
        )

    with col2:
        _grafico_evolucao(
            df_filtrado,
            "WACC",
            "Evolução do WACC",
            "percentual",
        )


    _titulo_secao("Liquidez")

    col1, col2 = st.columns(2)

    with col1:
        _grafico_evolucao(
            df_filtrado,
            "LC",
            "Liquidez Corrente (LC)",
        )

    with col2:
        _grafico_evolucao(
            df_filtrado,
            "LS",
            "Liquidez Seca (LS)",
        )

    col1, col2 = st.columns(2)

    with col1:
        _grafico_evolucao(
            df_filtrado,
            "LI",
            "Liquidez Imediata (LI)",
        )

    with col2:
        _grafico_evolucao(
            df_filtrado,
            "LG",
            "Liquidez Geral (LG)",
        )

    # --------------------------------------------------------
    # ENDIVIDAMENTO
    # --------------------------------------------------------

    _titulo_secao("Endividamento e estrutura de capital")

    col1, col2, col3 = st.columns(3)

    for coluna, indicador, titulo in [
        (col1, "PCT", "Participação de Capitais de Terceiros (PCT)"),
        (col2, "CE", "Composição do Endividamento (CE)"),
        (col3, "IPL", "Imobilização do Patrimônio Líquido (IPL)"),
    ]:
        with coluna:
            _grafico_evolucao(
                df_filtrado,
                indicador,
                titulo,
            )


    _titulo_secao("Desempenho e geração de valor")

    col1, col2 = st.columns(2)

    with col1:
        _grafico_evolucao(
            df_filtrado,
            "EBITDA",
            "Evolução do EBITDA",
            "moeda",
        )

    with col2:
        _grafico_evolucao(
            df_filtrado,
            "NOPAT",
            "Evolução do NOPAT",
            "moeda",
        )

    col1, col2 = st.columns(2)

    with col1:
        _grafico_evolucao(
            df_filtrado,
            "EVA",
            "Evolução do EVA",
            "moeda",
        )

    with col2:
        _grafico_evolucao(
            df_filtrado,
            "MVA Aproximado",
            "Evolução do MVA Aproximado",
            "moeda",
        )

    # --------------------------------------------------------
    # CAPITAL INVESTIDO
    # --------------------------------------------------------

    _titulo_secao("Capital investido")

    _grafico_evolucao(
        df_filtrado,
        "Capital Investido",
        "Evolução do Capital Investido",
        "moeda",
    )

    _titulo_secao("Tabela de indicadores")

    colunas_tabela = [
        "Ano",
        "Cenario",
        "EBITDA",
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
    ]

    tabela = (
        df_filtrado[colunas_tabela]
        .sort_values(["Ano", "Cenario"])
        .reset_index(drop=True)
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
    )


    st.markdown(
        """
        <div class="ind_note">
            <strong>Nota metodológica:</strong>
            indicadores sem valores disponíveis permanecem como dados ausentes.
            As médias e os gráficos consideram apenas os valores existentes,
            sem substituir ausências por zero.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)