import streamlit as st
import pandas as pd
from data.load_data import carregar_indicadores

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
.ind-section-title {
    color: #173B63;
    font-size: 18px;
    font-weight: 750;
    margin: 12px 0 3px 0;
}
.ind-section-subtitle {
    color: #8293A7;
    font-size: 12px;
    margin-bottom: 14px;
}
.ind-card {
    background: #FFFFFF;
    border: 1px solid #E1ECF7;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(0,75,133,.05);
    min-height: 112px;
}
.ind-kpi-label {
    color: #718096;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .6px;
    margin-bottom: 10px;
}
.ind-kpi-value {
    color: #173B63;
    font-size: 24px;
    font-weight: 750;
}
.ind-kpi-note {
    color: #8293A7;
    font-size: 11px;
    margin-top: 7px;
}

/* Estética dos insights */
.ind-insight {
    background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFE 100%);
    border: 1px solid #E3ECF5;
    border-radius: 14px;
    padding: 19px 20px;
    min-height: 125px;
    margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(23, 59, 99, 0.045);
    transition: all 0.2s ease;
}
.ind-insight:hover {
    border-color: #B9D2E8;
    box-shadow: 0 5px 16px rgba(23, 59, 99, 0.09);
    transform: translateY(-2px);
}
.ind-insight-title {
    color: #173B63;
    font-size: 13px;
    font-weight: 750;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.ind-insight-text {
    color: #61748A;
    font-size: 12px;
    line-height: 1.7;
}
.ind-insight-title::before {
    content: "";
    display: inline-block;
    width: 7px;
    height: 7px;
    min-width: 7px;
    border-radius: 50%;
    background: #2585C5;
}
.ind-info {
    background: #F4F8FC;
    border: 1px solid #E1ECF7;
    border-radius: 10px;
    padding: 13px 16px;
    color: #52677D;
    font-size: 12px;
    margin: 8px 0 14px 0;
}
</style>
"""

# ============================================================
# CONFIGURAÇÕES DOS INDICADORES
# ============================================================

INDICADORES = {
    "EBITDA": {
        "grupo": "Rentabilidade e resultado",
        "formato": "moeda",
        "descricao": "Resultado antes de juros, impostos, depreciação e amortização."
    },
    "Margem EBITDA": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Representa a parcela da receita convertida em EBITDA."
    },
    "Margem Líquida": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Representa a parcela da receita que se transforma em lucro líquido."
    },
    "NOPAT": {
        "grupo": "Rentabilidade e resultado",
        "formato": "moeda",
        "descricao": "Lucro operacional líquido após impostos."
    },
    "ROIC": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Mede o retorno obtido sobre o capital investido."
    },
    "WACC": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Representa o custo médio ponderado de capital."
    },
    "LC": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez corrente: capacidade de pagamento das obrigações de curto prazo."
    },
    "LS": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez seca: capacidade de pagamento sem considerar os estoques."
    },
    "LI": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez imediata: capacidade de pagamento com recursos disponíveis imediatamente."
    },
    "LG": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez geral: capacidade de pagamento considerando curto e longo prazo."
    },
    "PCT": {
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Participação do capital de terceiros na estrutura de capital."
    },
    "CE": {
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Indica a composição do endividamento."
    },
    "IPL": {
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Indica o nível de imobilização do patrimônio líquido."
    },
    "Capital Investido": {
        "grupo": "Valor econômico",
        "formato": "moeda",
        "descricao": "Capital aplicado nas operações da empresa."
    },
    "EVA": {
        "grupo": "Valor econômico",
        "formato": "moeda",
        "descricao": "Valor econômico agregado após considerar o custo do capital."
    },
    "MVA Aproximado": {
        "grupo": "Valor econômico",
        "formato": "moeda",
        "descricao": "Estimativa do valor agregado pelo mercado."
    },

    "ROE": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Mede o retorno gerado sobre o patrimônio líquido médio."
    },
    "DuPont - Margem Líquida": {
        "grupo": "Análise DuPont",
        "formato": "percentual",
        "descricao": "Representa a parcela da receita convertida em lucro líquido."
    },
    "DuPont - Giro do Ativo": {
        "grupo": "Análise DuPont",
        "formato": "numero",
        "descricao": "Mede a capacidade dos ativos de gerar receita."
    },
    "DuPont - Alavancagem": {
        "grupo": "Análise DuPont",
        "formato": "numero",
        "descricao": "Relaciona os ativos médios ao patrimônio líquido médio."
    },
    "ROE DuPont": {
        "grupo": "Análise DuPont",
        "formato": "percentual",
        "descricao": "Resultado do ROE calculado pela decomposição DuPont."
    },

    "CCL": {
        "grupo": "Capital de giro e prazos",
        "formato": "moeda",
        "descricao": "Capital circulante líquido: diferença entre ativo e passivo circulantes."
    },
    "PMR": {
        "grupo": "Capital de giro e prazos",
        "formato": "dias",
        "descricao": "Prazo médio de recebimento das vendas."
    },
    "PMP": {
        "grupo": "Capital de giro e prazos",
        "formato": "dias",
        "descricao": "Prazo médio de pagamento aos fornecedores."
    },
    "Ciclo Financeiro": {
        "grupo": "Capital de giro e prazos",
        "formato": "dias",
        "descricao": "Diferença entre o prazo médio de recebimento e o de pagamento."
    },
    "Necessidade de Capital de Giro": {
        "grupo": "Capital de giro e prazos",
        "formato": "moeda",
        "descricao": "Estimativa dos recursos necessários para financiar o ciclo financeiro."
    },

    "Taxa de Conversão da Receita em Caixa": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Relaciona os recebimentos de caixa à receita operacional."
    },
    "FCO": {
        "grupo": "Fluxo de caixa",
        "formato": "moeda",
        "descricao": "Fluxo de caixa operacional."
    },
    "FCO / EBITDA": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa operacional ao EBITDA."
    },
    "FCO / Lucro Líquido": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa operacional ao lucro líquido."
    },
    "FCL": {
        "grupo": "Fluxo de caixa",
        "formato": "moeda",
        "descricao": "Fluxo de caixa livre após os investimentos."
    },
    "Capex / Receita": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Representa os investimentos em relação à receita."
    },
    "Capex / D&A": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona os investimentos à depreciação e amortização."
    },
    "Cobertura de Juros": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa operacional às despesas financeiras utilizadas como referência."
    },
    "FCO / Dívida Bruta": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Relaciona o fluxo de caixa operacional à dívida bruta."
    },
    "Payout em Caixa": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Relaciona a distribuição de caixa aos acionistas ao lucro líquido."
    },
    "Cobertura de Dividendos": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa livre à distribuição de caixa aos acionistas."
    }
}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def _numero(valor, casas=2):
    if pd.isna(valor):
        return "—"

    return (
        f"{valor:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def _moeda(valor):
    if pd.isna(valor):
        return "—"

    absoluto = abs(valor)

    if absoluto >= 1_000_000_000:
        return f"R$ {_numero(valor / 1_000_000_000)} bi"

    if absoluto >= 1_000_000:
        return f"R$ {_numero(valor / 1_000_000)} mi"

    if absoluto >= 1_000:
        return f"R$ {_numero(valor / 1_000)} mil"

    return f"R$ {_numero(valor)}"


def _percentual(valor, serie=None):
    if pd.isna(valor):
        return "—"

    if serie is not None:
        valores = pd.to_numeric(serie, errors="coerce").dropna()

        if not valores.empty and valores.abs().median() <= 1.5:
            valor = valor * 100

    elif abs(valor) <= 1.5:
        valor = valor * 100

    return f"{_numero(valor)}%"


def _formatar_indicador(coluna, valor, serie=None):
    if pd.isna(valor):
        return "—"

    formato = INDICADORES.get(coluna, {}).get("formato")

    if formato == "moeda":
        return _moeda(valor)

    if formato == "percentual":
        return _percentual(valor, serie)

    return _numero(valor)


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


def _card(coluna, titulo, valor, observacao):
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


def _insight(titulo, texto):
    st.markdown(
        f"""
        <div class="ind-insight">
            <div class="ind-insight-title">{titulo}</div>
            <div class="ind-insight-text">{texto}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _numero_ano(valor):
    resultado = pd.Series([str(valor)]).str.extract(
        r"(\d+)",
        expand=False
    ).iloc[0]

    return int(resultado) if pd.notna(resultado) else 0


# ============================================================
# ORGANIZAÇÃO DOS CENÁRIOS
# ============================================================

def _mapear_cenarios(df):
    cenarios_originais = sorted(
        df["Cenario"].dropna().unique(),
        key=lambda x: (
            _numero_ano(x),
            str(x)
        )
    )

    mapa = {
        cenario: f"Cenário {i + 1}"
        for i, cenario in enumerate(cenarios_originais)
    }

    return mapa


# ============================================================
# ANÁLISE DO ANO SELECIONADO
# ============================================================

def _gerar_insights(
    df_ano,
    df_anterior=None,
    cenario_selecionado=None
):
    if df_ano.empty:
        st.info("Não há dados disponíveis para gerar insights.")
        return

    if cenario_selecionado == "Todos":
        contexto = "considerando todos os cenários"
    else:
        contexto = f"para {cenario_selecionado}"

    ebitda = (
        pd.to_numeric(df_ano["EBITDA"], errors="coerce").mean()
        if "EBITDA" in df_ano.columns else None
    )

    margem = (
        pd.to_numeric(df_ano["Margem EBITDA"], errors="coerce").mean()
        if "Margem EBITDA" in df_ano.columns else None
    )

    margem_liquida = (
        pd.to_numeric(df_ano["Margem Líquida"], errors="coerce").mean()
        if "Margem Líquida" in df_ano.columns else None
    )

    roic = (
        pd.to_numeric(df_ano["ROIC"], errors="coerce").mean()
        if "ROIC" in df_ano.columns else None
    )

    wacc = (
        pd.to_numeric(df_ano["WACC"], errors="coerce").mean()
        if "WACC" in df_ano.columns else None
    )

    lc = (
        pd.to_numeric(df_ano["LC"], errors="coerce").mean()
        if "LC" in df_ano.columns else None
    )

    # Resultados principais
    col1, col2 = st.columns(2)

    with col1:
        if ebitda is not None and pd.notna(ebitda):
            _insight(
                "Resultado operacional",
                f"A média do EBITDA foi de {_moeda(ebitda)} {contexto}."
            )

        if margem is not None and pd.notna(margem):
            _insight(
                "Margem EBITDA",
                f"A margem EBITDA média foi de "
                f"{_percentual(margem, df_ano['Margem EBITDA'])}, "
                "indicando a participação do resultado operacional "
                "em relação à receita."
            )

    with col2:
        if margem_liquida is not None and pd.notna(margem_liquida):
            _insight(
                "Margem líquida",
                f"A margem líquida média foi de "
                f"{_percentual(margem_liquida, df_ano['Margem Líquida'])}."
            )

        if lc is not None and pd.notna(lc):
            if lc > 1:
                interpretacao = (
                    "a média está acima de 1, indicando maior cobertura "
                    "das obrigações de curto prazo pelos ativos circulantes."
                )
            elif lc < 1:
                interpretacao = (
                    "a média está abaixo de 1, indicando que os ativos "
                    "circulantes são inferiores às obrigações de curto prazo."
                )
            else:
                interpretacao = (
                    "a média está em 1, indicando equilíbrio entre "
                    "ativos e obrigações de curto prazo."
                )

            _insight(
                "Liquidez corrente",
                f"A liquidez corrente média foi de {_numero(lc)}; {interpretacao}"
            )

    # ROIC x WACC
    if "ROIC" in df_ano.columns and "WACC" in df_ano.columns:
        comparacao = df_ano[["ROIC", "WACC"]].apply(
            pd.to_numeric,
            errors="coerce"
        ).dropna()

        if not comparacao.empty:
            acima = (comparacao["ROIC"] > comparacao["WACC"]).sum()
            total = len(comparacao)
            proporcao = (acima / total) * 100

            if roic > wacc:
                leitura = (
                    "Na média, o retorno sobre o capital investido "
                    "superou o custo de capital."
                )
            elif roic < wacc:
                leitura = (
                    "Na média, o retorno sobre o capital investido "
                    "ficou abaixo do custo de capital."
                )
            else:
                leitura = (
                    "Na média, o retorno sobre o capital investido "
                    "ficou igual ao custo de capital."
                )

            _insight(
                "Retorno sobre o capital x custo de capital",
                f"{leitura} Em {proporcao:.1f}% dos registros com dados "
                "disponíveis, o ROIC ficou acima do WACC."
            )

    # Comparação com o ano anterior
    if df_anterior is not None and not df_anterior.empty:

        if "EBITDA" in df_ano.columns and "EBITDA" in df_anterior.columns:
            atual = pd.to_numeric(
                df_ano["EBITDA"], errors="coerce"
            ).mean()

            anterior = pd.to_numeric(
                df_anterior["EBITDA"], errors="coerce"
            ).mean()

            if pd.notna(atual) and pd.notna(anterior) and anterior != 0:
                variacao = ((atual - anterior) / abs(anterior)) * 100

                if variacao > 0:
                    texto = (
                        f"O EBITDA médio aumentou {_numero(variacao)}% "
                        "em relação ao ano anterior."
                    )
                elif variacao < 0:
                    texto = (
                        f"O EBITDA médio diminuiu {_numero(abs(variacao))}% "
                        "em relação ao ano anterior."
                    )
                else:
                    texto = (
                        "O EBITDA médio permaneceu estável em relação "
                        "ao ano anterior."
                    )

                _insight("Evolução do EBITDA", texto)

        if (
            "Margem EBITDA" in df_ano.columns
            and "Margem EBITDA" in df_anterior.columns
        ):
            atual = pd.to_numeric(
                df_ano["Margem EBITDA"], errors="coerce"
            ).mean()

            anterior = pd.to_numeric(
                df_anterior["Margem EBITDA"], errors="coerce"
            ).mean()

            if pd.notna(atual) and pd.notna(anterior):
                diferenca = atual - anterior

                _insight(
                    "Variação da margem EBITDA",
                    f"A diferença entre a margem EBITDA média do ano selecionado "
                    f"e a do ano anterior foi de {_numero(diferenca)} "
                    "ponto(s) na escala original dos dados."
                )

    # Melhor cenário por EBITDA
    if (
        cenario_selecionado == "Todos"
        and "Cenario" in df_ano.columns
        and "EBITDA" in df_ano.columns
    ):
        ranking = (
            df_ano.groupby("Cenario")["EBITDA"]
            .mean()
            .dropna()
            .sort_values(ascending=False)
        )

        if not ranking.empty:
            melhor = ranking.index[0]
            pior = ranking.index[-1]
            mapa = _mapear_cenarios(df_ano)

            _insight(
                "Destaque entre os cenários",
                f"{mapa.get(melhor, melhor)} apresentou o maior EBITDA médio "
                f"({_moeda(ranking.iloc[0])}). "
                f"{mapa.get(pior, pior)} apresentou o menor "
                f"({_moeda(ranking.iloc[-1])})."
            )


# ============================================================
# TABELA PERSONALIZADA
# ============================================================

def _tabela_indicadores(df, mapa_cenarios):
    _titulo_secao(
        "Explore os indicadores",
        "Escolha quais informações deseja consultar. "
        "A tabela será atualizada conforme sua seleção."
    )

    indicadores_disponiveis = [
        indicador
        for indicador in INDICADORES
        if indicador in df.columns
    ]

    grupos = {}

    for indicador in indicadores_disponiveis:
        grupo = INDICADORES[indicador]["grupo"]
        grupos.setdefault(grupo, []).append(indicador)

    opcoes = []

    for grupo, indicadores in grupos.items():
        opcoes.extend(indicadores)

    padrao = [
        "EBITDA",
        "Margem EBITDA",
        "Margem Líquida",
        "ROIC",
        "WACC"
    ]

    padrao = [
        item for item in padrao
        if item in indicadores_disponiveis
    ]

    selecionados = st.multiselect(
        "Indicadores que deseja visualizar",
        options=opcoes,
        default=padrao,
        key="ind_selecao_indicadores",
        help="Você pode selecionar um ou vários indicadores."
    )

    if not selecionados:
        st.info("Selecione pelo menos um indicador para montar a tabela.")
        return

    tabela = df.copy()
    tabela["Cenário"] = tabela["Cenario"].map(mapa_cenarios)
    tabela["Ano"] = tabela["Ano"].astype(str)

    colunas = ["Cenário", "Ano"] + selecionados
    tabela = tabela[colunas].copy()

    tabela = tabela.sort_values(["Cenário", "Ano"])

    nomes = {
        "Margem EBITDA": "Margem EBITDA (%)",
        "Margem Líquida": "Margem Líquida (%)",
        "PCT": "Participação de Capital de Terceiros",
        "CE": "Composição do Endividamento",
        "IPL": "Imobilização do Patrimônio Líquido",
        "LC": "Liquidez Corrente",
        "LS": "Liquidez Seca",
        "LI": "Liquidez Imediata",
        "LG": "Liquidez Geral",
        "Capital Investido": "Capital Investido (R$)",
        "EBITDA": "EBITDA (R$)",
        "NOPAT": "NOPAT (R$)",
        "EVA": "EVA (R$)",
        "MVA Aproximado": "MVA Aproximado (R$)"
    }

    tabela = tabela.rename(columns=nomes)

    configuracao = {
        "Cenário": st.column_config.TextColumn(
            "Cenário",
            width="medium"
        ),
        "Ano": st.column_config.TextColumn(
            "Ano",
            width="small"
        )
    }

    for indicador in selecionados:
        nome = nomes.get(indicador, indicador)
        formato = INDICADORES[indicador]["formato"]

        if formato == "moeda":
            formato_numero = "R$ %.2f"
        elif formato == "percentual":
            formato_numero = "%.2%%"
        elif formato == "dias":
            formato_numero = "%.1f dias"
        elif formato == "multiplo":
            formato_numero = "%.2fx"
        else:
            formato_numero = "%.2f"

        configuracao[nome] = st.column_config.NumberColumn(
            nome,
            format=formato_numero,
            help=INDICADORES[indicador]["descricao"]
        )

    col1, col2 = st.columns([1, 4])

    with col1:
        st.metric(
            "Registros",
            f"{len(tabela):,}".replace(",", ".")
        )

    with col2:
        st.caption(
            f"{len(selecionados)} indicador(es) selecionado(s)."
        )

    st.dataframe(
        tabela,
        column_config=configuracao,
        use_container_width=True,
        hide_index=True,
        height=480
    )

    st.caption(
        "Os valores são apresentados conforme os dados disponíveis "
        "na base de indicadores. Campos sem informação permanecem vazios."
    )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

def render_indicadores():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="ind_page"):

        # Carregamento
        try:
            df = carregar_indicadores()

        except Exception as erro:
            st.error(f"Não foi possível carregar os indicadores: {erro}")
            return

        if df is None or df.empty:
            st.warning("A base de indicadores está vazia.")
            return

        df = df.copy()

        if "Ano_Numero" not in df.columns:
            df["Ano_Numero"] = (
                df["Ano"]
                .astype(str)
                .str.extract(r"(\d+)", expand=False)
                .astype(int)
            )

        # Converte colunas numéricas
        for coluna in INDICADORES:
            if coluna in df.columns:
                df[coluna] = pd.to_numeric(
                    df[coluna],
                    errors="coerce"
                )

        # Cenários e anos
        mapa_cenarios = _mapear_cenarios(df)

        anos_disponiveis = (
            df[["Ano", "Ano_Numero"]]
            .drop_duplicates()
            .sort_values("Ano_Numero")["Ano"]
            .tolist()
        )

        cenarios_originais = list(mapa_cenarios.keys())

        # Cabeçalho e filtros
        col_titulo, col_ano, col_cenario = st.columns(
            [2.6, 1, 1.2],
            vertical_alignment="bottom"
        )

        with col_titulo:
            st.markdown(
                """
                <div>
                    <div class="ind-eyebrow">PAINEL FINANCEIRO</div>
                    <div class="ind-title">Indicadores Financeiros</div>
                    <div class="ind-subtitle">
                        Explore os resultados, identifique tendências
                        e analise o desempenho dos cenários.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_ano:
            ano_selecionado = st.selectbox(
                "Ano de análise",
                options=anos_disponiveis,
                index=len(anos_disponiveis) - 1,
                key="ind_filtro_ano"
            )

        with col_cenario:
            cenario_selecionado = st.selectbox(
                "Cenário",
                options=["Todos"] + cenarios_originais,
                format_func=lambda x: (
                    x if x == "Todos"
                    else mapa_cenarios.get(x, x)
                ),
                key="ind_filtro_cenario"
            )

        st.write("")

        # Filtro do ano
        df_ano = df[
            df["Ano"] == ano_selecionado
        ].copy()

        if cenario_selecionado != "Todos":
            df_ano = df_ano[
                df_ano["Cenario"] == cenario_selecionado
            ]

        if df_ano.empty:
            st.warning("Não existem dados para essa seleção.")
            return

        # Ano anterior para comparação
        ano_numero = _numero_ano(ano_selecionado)

        df_anterior = df[
            df["Ano_Numero"] == ano_numero - 1
        ].copy()

        if cenario_selecionado != "Todos":
            df_anterior = df_anterior[
                df_anterior["Cenario"] == cenario_selecionado
            ]

        # Resumo do ano
        _titulo_secao(
            f"Resumo de {ano_selecionado}",
            "Indicadores médios do recorte selecionado."
        )

        def media(coluna):
            if coluna not in df_ano.columns:
                return None

            valores = df_ano[coluna].dropna()

            return valores.mean() if not valores.empty else None

        ebitda = media("EBITDA")
        margem_ebitda = media("Margem EBITDA")
        margem_liquida = media("Margem Líquida")
        roic = media("ROIC")

        col1, col2, col3, col4 = st.columns(4)

        _card(
            col1,
            "EBITDA médio",
            _moeda(ebitda) if ebitda is not None else "—",
            "Resultado operacional"
        )

        _card(
            col2,
            "Margem EBITDA",
            _percentual(margem_ebitda, df_ano["Margem EBITDA"])
            if margem_ebitda is not None else "—",
            "Rentabilidade operacional"
        )

        _card(
            col3,
            "Margem líquida",
            _percentual(margem_liquida, df_ano["Margem Líquida"])
            if margem_liquida is not None else "—",
            "Rentabilidade líquida"
        )

        _card(
            col4,
            "ROIC médio",
            _percentual(roic, df_ano["ROIC"])
            if roic is not None else "—",
            "Retorno sobre o capital investido"
        )

        st.write("")

        # Insights automáticos
        _titulo_secao(
            "Insights do período",
            "Leituras automáticas dos indicadores do ano selecionado."
        )

        _gerar_insights(
            df_ano,
            df_anterior,
            cenario_selecionado
        )

        st.write("")

        # Explorador de indicadores
        _tabela_indicadores(
            df_ano,
            mapa_cenarios
        )