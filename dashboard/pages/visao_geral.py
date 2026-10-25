import pandas as pd
import streamlit as st

from data.load_data import carregar_indicadores


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


# ---------- Página principal ----------

def render_visao_geral():
    st.title("Visão Geral")
    st.caption(
        "Acompanhe os indicadores financeiros da CTI, "
        "compare cenários e identifique pontos que merecem atenção."
    )

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

    # 2. Filtros de ano e cenário.
    st.subheader("Filtros")

    anos = sorted(df["Ano_Numero"].dropna().unique().astype(int).tolist())
    cenarios = sorted(
        df["Cenario"].dropna().astype(str).unique().tolist()
    )

    if not anos or not cenarios:
        st.warning("Não há anos ou cenários disponíveis para selecionar.")
        return

    filtro_ano, filtro_cenario = st.columns(2)

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

    st.caption(
        f"Referência: Ano {ano_selecionado} | "
        f"{cenario_selecionado} | {descricao_calculo}"
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
    st.subheader("Desempenho financeiro")

    cards_1 = st.columns(4)

    with cards_1[0]:
        st.metric("EBITDA médio", formatar_moeda(obter_valor("EBITDA")))
        st.caption("Resultado antes de juros, impostos, depreciação e amortização.")

    with cards_1[1]:
        st.metric(
            "Margem EBITDA",
            formatar_percentual(obter_valor("Margem EBITDA")),
        )
        st.caption("Margem conforme calculada na base.")

    with cards_1[2]:
        st.metric(
            "Margem Líquida",
            formatar_percentual(obter_valor("Margem Líquida")),
        )
        st.caption("Margem conforme calculada na base.")

    with cards_1[3]:
        st.metric("NOPAT", formatar_moeda(obter_valor("NOPAT")))
        st.caption("Lucro operacional após impostos, conforme a base.")

    # 6. Segunda linha de indicadores.
    st.subheader("Retorno, liquidez e custo de capital")

    cards_2 = st.columns(4)

    with cards_2[0]:
        st.metric("Liquidez Corrente (LC)", formatar_numero(obter_valor("LC")))
        st.caption("Indicador de liquidez disponível na base.")

    with cards_2[1]:
        st.metric("ROIC", formatar_percentual(obter_valor("ROIC")))
        st.caption("Retorno sobre o capital investido, conforme a base.")

    with cards_2[2]:
        st.metric("EVA", formatar_moeda(obter_valor("EVA")))
        st.caption("Valor econômico agregado, conforme a base.")

    with cards_2[3]:
        st.metric("WACC", formatar_percentual(obter_valor("WACC")))
        st.caption("Custo médio ponderado de capital, conforme a base.")

    st.divider()

    # 7. Evolução do EBITDA médio por ano.
    st.subheader("Evolução do EBITDA")
    st.caption(
        "Mostra a média anual do EBITDA entre os cenários disponíveis, "
        "ou a evolução do cenário selecionado."
    )

    historico = df.copy()

    if cenario_selecionado != "Todos os cenários":
        historico = historico[
            historico["Cenario"].astype(str) == cenario_selecionado
        ]

    if "EBITDA" in historico.columns:
        serie_ebitda = (
            historico.groupby("Ano_Numero")["EBITDA"]
            .mean()
            .dropna()
            .sort_index()
        )

        if not serie_ebitda.empty:
            serie_ebitda.index = [f"Ano {ano}" for ano in serie_ebitda.index]
            st.line_chart(serie_ebitda, height=300, y_label="EBITDA (R$)")
        else:
            st.info("Não há valores disponíveis de EBITDA para o gráfico.")
    else:
        st.info("A coluna EBITDA não está disponível na base.")

    # 8. Evolução das margens.
    st.subheader("Evolução das margens")
    st.caption(
        "Valores percentuais conforme registrados na base; "
        "não representam necessariamente a margem de uma única empresa."
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
        serie_margens.index = [
            f"Ano {ano}" for ano in serie_margens.index
        ]

        if not serie_margens.empty:
            serie_margens = serie_margens.rename(
                columns={
                    "Margem EBITDA": "Margem EBITDA (%)",
                    "Margem Líquida": "Margem Líquida (%)",
                }
            )
            st.line_chart(serie_margens, height=300, y_label="Percentual (%)")
        else:
            st.info("Não há dados de margens disponíveis para o gráfico.")
    else:
        st.info("As colunas necessárias para o gráfico de margens não existem.")

    # 9. Ressalvas e transparência dos dados.
    st.subheader("Qualidade e disponibilidade dos dados")

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
        for aviso in ausentes:
            st.warning(aviso)
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

    st.caption(
        "Metodologia: os indicadores não são recalculados a partir de "
        "fórmulas contábeis nesta tela; são exibidos conforme a base. "
        "Quando todos os cenários estão selecionados, os cards mostram "
        "a média dos valores disponíveis. Dados ausentes não são imputados."
    )