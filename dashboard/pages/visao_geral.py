import pandas as pd
import streamlit as st

from data.load_data import carregar_indicadores

# Mesmo visual da página de Regressão: topo com filtros, cartões brancos.
PAGE_STYLE = """
<style>
    .st-key-vg_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .vg-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .vg-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .vg-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .st-key-vg_topo label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .vg-referencia {
        font-size: 12px;
        color: var(--cti-muted);
    }

    .vg-section-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
        margin: 6px 0 -6px;
    }

    /* cartões brancos */
    [class*="st-key-vg_kpi_"],
    .st-key-vg_grafico_ebitda,
    .st-key-vg_grafico_margens,
    .st-key-vg_qualidade {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
    }

    /* cartões da mesma linha com a mesma altura */
    .st-key-vg_page [data-testid="stHorizontalBlock"]:has([class*="st-key-vg_kpi_"]) {
        align-items: stretch;
    }

    .st-key-vg_page [data-testid="stColumn"]:has([class*="st-key-vg_kpi_"]) > div,
    .st-key-vg_page [data-testid="stColumn"]:has([class*="st-key-vg_kpi_"]) [data-testid="stVerticalBlock"],
    .st-key-vg_page [data-testid="stColumn"]:has([class*="st-key-vg_kpi_"]) [data-testid="stLayoutWrapper"] {
        height: 100%;
    }

    .vg-kpi-label {
        font-size: 12px;
        color: var(--cti-muted);
    }

    .vg-kpi-value {
        font-size: clamp(15px, 1.35vw, 24px);
        font-weight: 700;
        color: var(--cti-blue);
        line-height: 1.3;
        white-space: nowrap;
    }

    .vg-kpi-note {
        font-size: 11px;
        color: #8AA4BF;
        line-height: 1.4;
        margin-top: 2px;
    }

    .vg-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
    }

    .vg-card-note {
        font-size: 11.5px;
        color: #8AA4BF;
        margin: 2px 0 8px;
    }

    .vg-metodologia {
        font-size: 11.5px;
        color: #8AA4BF;
        line-height: 1.5;
        margin-top: 4px;
    }
</style>
"""


# ---------- Formatação dos valores ----------

def formatar_moeda(valor):
    if pd.isna(valor):
        return "N/D"

    valor = float(valor)
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_percentual(valor):
    if pd.isna(valor):
        return "N/D"

    return f"{valor:.2%}".replace(".", ",")


def formatar_numero(valor):
    if pd.isna(valor):
        return "N/D"

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------- Blocos visuais ----------

def _kpi(key, rotulo, valor, nota):
    # "R$" não pode ficar sozinho numa linha quando o valor quebra
    valor = valor.replace("R$ ", "R$&nbsp;")

    with st.container(key=key):
        st.markdown(f"""
            <div class="vg-kpi-label">{rotulo}</div>
            <div class="vg-kpi-value">{valor}</div>
            <div class="vg-kpi-note">{nota}</div>
        """, unsafe_allow_html=True)


def _titulo_secao(texto):
    st.markdown(f'<div class="vg-section-title">{texto}</div>', unsafe_allow_html=True)


def _titulo_cartao(titulo, nota=None):
    html = f'<div class="vg-card-title">{titulo}</div>'
    if nota:
        html += f'<div class="vg-card-note">{nota}</div>'
    st.markdown(html, unsafe_allow_html=True)


# ---------- Página principal ----------

def render_visao_geral():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="vg_page"):
        _render_conteudo()


def _render_conteudo():
    # 1. Carrega os dados reais.
    try:
        df = carregar_indicadores()
    except Exception as erro:
        st.error(f"Não foi possível carregar a base financeira: {erro}")
        return

    colunas_obrigatorias = {"Ano", "Ano_Numero", "Cenario"}

    if not colunas_obrigatorias.issubset(df.columns):
        st.error(
            "A base não contém todas as colunas necessárias: "
            "Ano, Ano_Numero e Cenario."
        )
        return

    if df.empty:
        st.warning("A base financeira está vazia.")
        return

    anos = sorted(df["Ano_Numero"].dropna().unique().astype(int).tolist())
    cenarios = sorted(
        df["Cenario"].dropna().astype(str).unique().tolist()
    )

    if not anos or not cenarios:
        st.warning("Não há anos ou cenários disponíveis para selecionar.")
        return

    # 2. Topo: título à esquerda, filtros de ano e cenário à direita.
    with st.container(key="vg_topo"):
        titulo, filtro_ano, filtro_cenario = st.columns(
            [2.6, 1, 1.4], vertical_alignment="bottom"
        )

        with titulo:
            st.markdown("""
                <div class="vg-eyebrow">PAINEL FINANCEIRO</div>
                <div class="vg-title">Visão Geral</div>
                <div class="vg-subtitle">
                    Acompanhe os indicadores financeiros da CTI, compare cenários
                    e identifique pontos que merecem atenção.
                </div>
            """, unsafe_allow_html=True)

        with filtro_ano:
            ano_selecionado = st.selectbox(
                "Ano de referência",
                options=anos,
                index=len(anos) - 1,
                format_func=lambda ano: f"Ano {ano}",
            )

        with filtro_cenario:
            cenario_selecionado = st.selectbox(
                "Cenário",
                options=["Todos os cenários"] + cenarios,
            )

    # 3. Aplica os filtros escolhidos.
    dados_ano = df[df["Ano_Numero"] == ano_selecionado].copy()

    if cenario_selecionado != "Todos os cenários":
        dados_ano = dados_ano[
            dados_ano["Cenario"].astype(str) == cenario_selecionado
        ]

    if dados_ano.empty:
        st.warning("Não existem registros para os filtros selecionados.")
        return

    if cenario_selecionado == "Todos os cenários":
        descricao_calculo = "Média dos cenários com valores disponíveis."
    else:
        descricao_calculo = "Valores do cenário selecionado."

    st.markdown(
        f'<div class="vg-referencia">Referência: Ano {ano_selecionado} | '
        f"{cenario_selecionado} | {descricao_calculo}</div>",
        unsafe_allow_html=True,
    )

    # 4. Calcula os valores apresentados nos cards.
    def obter_valor(coluna):
        if coluna not in dados_ano.columns:
            return float("nan")

        valores = pd.to_numeric(dados_ano[coluna], errors="coerce").dropna()

        if valores.empty:
            return float("nan")

        if cenario_selecionado == "Todos os cenários":
            return valores.mean()

        return valores.iloc[0]

    def obter_ultimo_ano_disponivel(coluna):
        if coluna not in df.columns:
            return None

        validos = df.loc[
            df[coluna].notna(),
            "Ano_Numero",
        ]

        return int(validos.max()) if not validos.empty else None

    # 5. Primeira linha de indicadores.
    _titulo_secao("Desempenho financeiro")

    cards_1 = st.columns(4)

    with cards_1[0]:
        _kpi(
            "vg_kpi_ebitda",
            "EBITDA médio",
            formatar_moeda(obter_valor("EBITDA")),
            "Resultado antes de juros, impostos, depreciação e amortização.",
        )

    with cards_1[1]:
        _kpi(
            "vg_kpi_margem_ebitda",
            "Margem EBITDA",
            formatar_percentual(obter_valor("Margem EBITDA")),
            "Margem conforme calculada na base.",
        )

    with cards_1[2]:
        _kpi(
            "vg_kpi_margem_liquida",
            "Margem Líquida",
            formatar_percentual(obter_valor("Margem Líquida")),
            "Margem conforme calculada na base.",
        )

    with cards_1[3]:
        _kpi(
            "vg_kpi_nopat",
            "NOPAT",
            formatar_moeda(obter_valor("NOPAT")),
            "Lucro operacional após impostos, conforme a base.",
        )

    # 6. Segunda linha de indicadores.
    _titulo_secao("Retorno, liquidez e custo de capital")

    cards_2 = st.columns(4)

    with cards_2[0]:
        _kpi(
            "vg_kpi_lc",
            "Liquidez Corrente (LC)",
            formatar_numero(obter_valor("LC")),
            "Indicador de liquidez disponível na base.",
        )

    with cards_2[1]:
        _kpi(
            "vg_kpi_roic",
            "ROIC",
            formatar_percentual(obter_valor("ROIC")),
            "Retorno sobre o capital investido, conforme a base.",
        )

    with cards_2[2]:
        _kpi(
            "vg_kpi_eva",
            "EVA",
            formatar_moeda(obter_valor("EVA")),
            "Valor econômico agregado, conforme a base.",
        )

    with cards_2[3]:
        _kpi(
            "vg_kpi_wacc",
            "WACC",
            formatar_percentual(obter_valor("WACC")),
            "Custo médio ponderado de capital, conforme a base.",
        )

    historico = df.copy()

    if cenario_selecionado != "Todos os cenários":
        historico = historico[
            historico["Cenario"].astype(str) == cenario_selecionado
        ]

    col_ebitda, col_margens = st.columns(2, gap="medium")

    # 7. Evolução do EBITDA médio por ano.
    with col_ebitda, st.container(key="vg_grafico_ebitda"):
        _titulo_cartao(
            "Evolução do EBITDA",
            "Média anual do EBITDA entre os cenários disponíveis, "
            "ou a evolução do cenário selecionado.",
        )

        if "EBITDA" in historico.columns:
            serie_ebitda = (
                historico.groupby("Ano_Numero")["EBITDA"]
                .mean()
                .dropna()
                .sort_index()
            )

            if not serie_ebitda.empty:
                # O ano fica numérico: como texto ("Ano 10") o gráfico
                # ordenaria alfabeticamente (Ano 1, Ano 10, Ano 11, Ano 2...)
                st.line_chart(
                    serie_ebitda, height=280, x_label="Ano", y_label="EBITDA (R$)"
                )
            else:
                st.info("Não há valores disponíveis de EBITDA para o gráfico.")
        else:
            st.info("A coluna EBITDA não está disponível na base.")

    # 8. Evolução das margens.
    with col_margens, st.container(key="vg_grafico_margens"):
        _titulo_cartao(
            "Evolução das margens",
            "Valores percentuais conforme registrados na base; "
            "não representam necessariamente a margem de uma única empresa.",
        )

        colunas_margens = ["Margem EBITDA", "Margem Líquida"]

        if all(coluna in historico.columns for coluna in colunas_margens):
            serie_margens = (
                historico.groupby("Ano_Numero")[colunas_margens]
                .mean()
                .sort_index()
                * 100
            )

            serie_margens = serie_margens.dropna(how="all")

            if not serie_margens.empty:
                serie_margens = serie_margens.rename(
                    columns={
                        "Margem EBITDA": "Margem EBITDA (%)",
                        "Margem Líquida": "Margem Líquida (%)",
                    }
                )
                st.line_chart(
                    serie_margens, height=280, x_label="Ano", y_label="Percentual (%)"
                )
            else:
                st.info("Não há dados de margens disponíveis para o gráfico.")
        else:
            st.info("As colunas necessárias para o gráfico de margens não existem.")

    # 9. Ressalvas e transparência dos dados.
    with st.container(key="vg_qualidade"):
        _titulo_cartao("Qualidade e disponibilidade dos dados")

        indicadores_com_ano = {
            "ROIC": "ROIC",
            "EVA": "EVA",
            "Capital Investido": "Capital Investido",
            "MVA Aproximado": "MVA Aproximado",
        }

        ausentes = []

        for coluna, nome in indicadores_com_ano.items():
            if coluna in df.columns and obter_valor(coluna) != obter_valor(coluna):
                ultimo_ano = obter_ultimo_ano_disponivel(coluna)

                if ultimo_ano is None:
                    ausentes.append(f"{nome}: sem valores disponíveis na base.")
                else:
                    ausentes.append(
                        f"{nome}: sem valor no Ano {ano_selecionado}; "
                        f"último ano disponível na base: Ano {ultimo_ano}."
                    )

        if ausentes:
            # Um único aviso em lista ocupa bem menos espaço que vários
            st.warning("\n".join(f"- {aviso}" for aviso in ausentes))
        else:
            st.success(
                "Os indicadores verificados possuem valores disponíveis "
                "para o período e cenário selecionados."
            )

        margem_ebitda = obter_valor("Margem EBITDA")

        if pd.notna(margem_ebitda) and margem_ebitda > 1:
            st.warning(
                "A Margem EBITDA ultrapassa 100% neste recorte. "
                "É necessário validar a fórmula e a origem desse indicador "
                "antes de interpretar o resultado."
            )

        st.markdown(
            '<div class="vg-metodologia">'
            "Metodologia: os indicadores não são recalculados a partir de "
            "fórmulas contábeis nesta tela; são exibidos conforme a base. "
            "Quando todos os cenários estão selecionados, os cards mostram "
            "a média dos valores disponíveis. Dados ausentes não são imputados."
            "</div>",
            unsafe_allow_html=True,
        )
