
import streamlit as st
import pandas as pd
import plotly.express as px

from data.load_data import carregar_indicadores


# ============================================================
# ESTILO DA PÁGINA
# ============================================================

PAGE_STYLE = """
<style>
.st-key-ind_page {
    padding: 28px 32px 40px;
    gap: 18px !important;
}

.ind-eyebrow {
    color: var(--cti-blue);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 7px;
}

.ind-title {
    color: var(--cti-text);
    font-size: 30px;
    font-weight: 750;
    line-height: 1.15;
    margin: 0 0 7px 0;
}

.ind-subtitle {
    color: var(--cti-muted);
    font-size: 13px;
    margin-bottom: 8px;
}

.ind-card {
    background: #FFFFFF;
    border: 1px solid #E1ECF7;
    border-radius: 14px;
    padding: 18px 22px;
    box-shadow: 0 2px 10px rgba(0,75,133,.05);
    min-height: 115px;
}

.ind-kpi-label {
    color: #718096;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .7px;
    margin-bottom: 10px;
}

.ind-kpi-value {
    color: #173B63;
    font-size: 25px;
    font-weight: 750;
    line-height: 1.2;
}

.ind-kpi-note {
    color: #8293A7;
    font-size: 11px;
    margin-top: 7px;
}

.ind-section-title {
    color: #173B63;
    font-size: 17px;
    font-weight: 750;
    margin: 8px 0 2px 0;
}

.ind-section-subtitle {
    color: #8293A7;
    font-size: 12px;
    margin-bottom: 10px;
}

.ind-chart-card {
    background: #FFFFFF;
    border: 1px solid #E1ECF7;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 2px 10px rgba(0,75,133,.05);
}
</style>
"""


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def _num(valor, casas=2):
    if pd.isna(valor):
        return "—"

    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _moeda(valor):
    if pd.isna(valor):
        return "—"

    return "R$ " + _num(valor)


def _percentual(valor):
    if pd.isna(valor):
        return "—"

    # Indicadores armazenados como proporção são convertidos para %
    if abs(valor) <= 1.5:
        valor = valor * 100

    return f"{_num(valor)}%"


def _titulo_secao(titulo, subtitulo=None):
    st.markdown(
        f"""
        <div>
            <div class="ind-section-title">{titulo}</div>
            <div class="ind-section-subtitle">{subtitulo or ""}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _criar_card(coluna, titulo, valor, observacao=""):
    with coluna:
        st.markdown(
            f"""
            <div class="ind-card">
                <div class="ind-kpi-label">{titulo}</div>
                <div class="ind-kpi-value">{valor}</div>
                <div class="ind-kpi-note">{observacao}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def _topo():
    st.markdown(
        """
        <div>
            <div class="ind-eyebrow">PAINEL FINANCEIRO</div>
            <div class="ind-title">Indicadores Financeiros</div>
            <div class="ind-subtitle">
                Acompanhamento dos principais indicadores de desempenho
                e estrutura financeira dos cenários.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

def _preparar_serie(df, cenario):
    serie = df[df["Cenario"] == cenario].copy()

    serie = serie.sort_values("Ano_Numero")

    return serie


# ============================================================
# FUNÇÃO DE GRÁFICOS
# ============================================================

def _grafico_evolucao(
    df,
    indicador,
    titulo,
    formato="numero",
    cor="#1976B9"
):
    if indicador not in df.columns:
        st.warning(f"Indicador '{indicador}' não encontrado na base.")
        return

    dados = df[["Ano", "Ano_Numero", indicador]].copy()

    dados[indicador] = pd.to_numeric(
        dados[indicador],
        errors="coerce"
    )

    dados = dados.dropna(subset=[indicador])
    dados = dados.sort_values("Ano_Numero")

    if dados.empty:
        st.info("Não existem dados disponíveis para este indicador.")
        return

    fig = px.line(
        dados,
        x="Ano",
        y=indicador,
        markers=True,
        title=titulo
    )

    fig.update_traces(
        line=dict(color=cor, width=3),
        marker=dict(size=8),
        hovertemplate="%{x}<br>Valor: %{y:,.2f}<extra></extra>"
    )

    fig.update_layout(
        height=320,
        margin=dict(l=15, r=15, t=45, b=15),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            color="#52677D",
            size=11
        ),
        title=dict(
            font=dict(size=15, color="#173B63")
        ),
        xaxis=dict(
            title="Ano",
            showgrid=False
        ),
        yaxis=dict(
            title="Valor",
            gridcolor="#EDF2F7",
            zeroline=False
        ),
        hovermode="x unified"
    )

    if formato == "percentual":
        fig.update_yaxes(ticksuffix="%")

    elif formato == "moeda":
        fig.update_yaxes(tickprefix="R$ ")

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

def render_indicadores():

    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="ind_page"):

        # ----------------------------------------------------
        # CARREGAMENTO DA BASE
        # ----------------------------------------------------

        try:
            df = carregar_indicadores()

        except Exception as erro:
            st.error(f"Não foi possível carregar os indicadores: {erro}")
            return

        if df is None or df.empty:
            st.warning("A base de indicadores está vazia.")
            return

        df = df.copy()

        # Garante a ordenação numérica dos anos
        if "Ano_Numero" not in df.columns:
            df["Ano_Numero"] = (
                df["Ano"]
                .astype(str)
                .str.extract(r"(\d+)", expand=False)
                .astype(int)
            )

        # ----------------------------------------------------
        # CABEÇALHO E FILTROS
        # ----------------------------------------------------

        with st.container(key="ind_topo"):

            col_titulo, col_ano, col_cenario = st.columns(
                [2.6, 1, 1.2],
                vertical_alignment="bottom"
            )

            with col_titulo:
                _topo()

            anos_disponiveis = sorted(
                df["Ano"].dropna().unique(),
                key=lambda x: int(
                    pd.Series([str(x)]).str.extract(r"(\d+)").iloc[0, 0]
                )
            )

            cenarios_disponiveis = sorted(
                df["Cenario"].dropna().unique()
            )

            with col_ano:
                ano_selecionado = st.selectbox(
                    "Ano",
                    options=["Todos"] + list(anos_disponiveis),
                    key="ind_filtro_ano"
                )

            with col_cenario:
                cenario_selecionado = st.selectbox(
                    "Cenário",
                    options=["Todos"] + list(cenarios_disponiveis),
                    key="ind_filtro_cenario"
                )

        # ----------------------------------------------------
        # APLICAÇÃO DOS FILTROS
        # ----------------------------------------------------

        df_filtrado = df.copy()

        if ano_selecionado != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["Ano"] == ano_selecionado
            ]

        if cenario_selecionado != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["Cenario"] == cenario_selecionado
            ]

        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
            return

        # ----------------------------------------------------
        # INDICADORES PRINCIPAIS
        # ----------------------------------------------------

        _titulo_secao(
            "Visão geral dos indicadores",
            "Resumo dos principais resultados financeiros do recorte selecionado."
        )

        # Se houver um cenário específico, utiliza seus dados.
        # Caso contrário, apresenta a média dos cenários disponíveis.
        if cenario_selecionado != "Todos":
            base_kpi = df_filtrado.copy()
        else:
            base_kpi = df_filtrado.copy()

        def media_coluna(coluna):
            if coluna not in base_kpi.columns:
                return None

            valores = pd.to_numeric(
                base_kpi[coluna],
                errors="coerce"
            ).dropna()

            if valores.empty:
                return None

            return valores.mean()

        ebitda = media_coluna("EBITDA")
        margem_ebitda = media_coluna("Margem EBITDA")
        margem_liquida = media_coluna("Margem Líquida")
        roic = media_coluna("ROIC")

        col1, col2, col3, col4 = st.columns(4)

        _criar_card(
            col1,
            "EBITDA médio",
            _moeda(ebitda) if ebitda is not None else "—",
            "Resultado operacional médio"
        )

        _criar_card(
            col2,
            "Margem EBITDA",
            _percentual(margem_ebitda)
            if margem_ebitda is not None else "—",
            "Rentabilidade operacional"
        )

        _criar_card(
            col3,
            "Margem Líquida",
            _percentual(margem_liquida)
            if margem_liquida is not None else "—",
            "Rentabilidade após os resultados"
        )

        _criar_card(
            col4,
            "ROIC",
            _percentual(roic) if roic is not None else "—",
            "Retorno sobre o capital investido"
        )

        st.write("")

        # ----------------------------------------------------
        # GRÁFICOS DE RENTABILIDADE
        # ----------------------------------------------------

        _titulo_secao(
            "Rentabilidade",
            "Evolução dos indicadores de margem e retorno."
        )

        if cenario_selecionado != "Todos":
            df_grafico = _preparar_serie(
                df,
                cenario_selecionado
            )
        else:
            df_grafico = (
                df.groupby(["Ano", "Ano_Numero"], as_index=False)
                .mean(numeric_only=True)
                .sort_values("Ano_Numero")
            )

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "Margem EBITDA",
                    "Evolução da Margem EBITDA",
                    formato="percentual"
                )

        with col2:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "Margem Líquida",
                    "Evolução da Margem Líquida",
                    formato="percentual",
                    cor="#269B85"
                )

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "ROIC",
                    "Evolução do ROIC",
                    formato="percentual",
                    cor="#7657B5"
                )

        with col2:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "WACC",
                    "Evolução do WACC",
                    formato="percentual",
                    cor="#D18B35"
                )

        st.write("")

        # ----------------------------------------------------
        # GRÁFICOS DE LIQUIDEZ
        # ----------------------------------------------------

        _titulo_secao(
            "Liquidez",
            "Indicadores relacionados à capacidade de pagamento."
        )

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "LC",
                    "Liquidez Corrente",
                    cor="#1976B9"
                )

        with col2:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "LS",
                    "Liquidez Seca",
                    cor="#269B85"
                )

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "LI",
                    "Liquidez Imediata",
                    cor="#7657B5"
                )

        with col2:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "LG",
                    "Liquidez Geral",
                    cor="#D18B35"
                )

        st.write("")

        # ----------------------------------------------------
        # ESTRUTURA DE CAPITAL
        # ----------------------------------------------------

        _titulo_secao(
            "Estrutura de capital",
            "Indicadores de endividamento e composição do capital."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "PCT",
                    "Participação de Capital de Terceiros",
                    formato="percentual"
                )

        with col2:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "CE",
                    "Composição do Endividamento",
                    formato="percentual",
                    cor="#269B85"
                )

        with col3:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "IPL",
                    "Imobilização do Patrimônio Líquido",
                    formato="percentual",
                    cor="#7657B5"
                )

        st.write("")

        # ----------------------------------------------------
        # RESULTADO E VALOR ECONÔMICO
        # ----------------------------------------------------

        _titulo_secao(
            "Resultado e valor econômico",
            "Evolução dos resultados operacionais e da geração de valor."
        )

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "EBITDA",
                    "Evolução do EBITDA",
                    formato="moeda"
                )

        with col2:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "NOPAT",
                    "Evolução do NOPAT",
                    formato="moeda",
                    cor="#269B85"
                )

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "EVA",
                    "Evolução do EVA",
                    formato="moeda",
                    cor="#7657B5"
                )

        with col2:
            with st.container():
                _grafico_evolucao(
                    df_grafico,
                    "MVA Aproximado",
                    "Evolução do MVA Aproximado",
                    formato="moeda",
                    cor="#D18B35"
                )

        st.write("")

        # ----------------------------------------------------
        # CAPITAL INVESTIDO
        # ----------------------------------------------------

        _titulo_secao(
            "Capital investido",
            "Acompanhamento do capital aplicado ao longo dos anos."
        )

        with st.container():
            _grafico_evolucao(
                df_grafico,
                "Capital Investido",
                "Evolução do Capital Investido",
                formato="moeda"
            )

        st.write("")

        # ----------------------------------------------------
        # TABELA COMPLETA DE INDICADORES
        # ----------------------------------------------------

        _titulo_secao(
            "Tabela de indicadores",
            "Visualização dos valores disponíveis na base para os filtros selecionados."
        )

        colunas_exibicao = [
            "Cenario",
            "Ano",
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
            "EBITDA"
        ]

        colunas_existentes = [
            coluna
            for coluna in colunas_exibicao
            if coluna in df_filtrado.columns
        ]

        tabela = df_filtrado.copy()

        tabela = tabela.sort_values(
            ["Ano_Numero", "Cenario"]
        )

        tabela = tabela[colunas_existentes]

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True,
            height=450
        )

        st.caption(
            f"Exibindo {len(tabela):,} registros.".replace(",", ".")
        )
