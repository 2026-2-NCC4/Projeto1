import re

import altair as alt
import pandas as pd
import streamlit as st

from components.como_interpretar import como_interpretar
from data.load_data import carregar_indicadores
from pages.indicadores import INDICADORES


PAGE_STYLE = """
<style>
    .st-key-comp_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .comp-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .comp-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .comp-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .st-key-comp_topo label p,
    .st-key-comp_selecao label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-comp_selecao,
    .st-key-comp_grafico,
    .st-key-comp_tabela_comparacao,
    .st-key-comp_todos {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
        box-sizing: border-box;
    }

    .st-key-comp_grafico,
    .st-key-comp_tabela_comparacao {
        height: 100%;
    }

    .comp-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
        margin-bottom: 4px;
    }

    .comp-card-note {
        font-size: 11px;
        color: #8AA4BF;
        margin-bottom: 12px;
    }

    .st-key-comp_nova_simulacao button {
        background: var(--cti-blue) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 40px;
        font-weight: 600;
        white-space: nowrap;
    }

    .st-key-comp_nova_simulacao button:hover {
        background: var(--cti-dark) !important;
    }
</style>
"""


COLUNAS_COMPARACAO = [
    "EBITDA",
    "Margem EBITDA",
    "Margem Líquida",
    "NOPAT",
    "ROE",
    "ROIC",
    "WACC",
    "EVA",
    "MVA Aproximado",
    "CCL",
    "PMR",
    "PMP",
    "Ciclo Financeiro",
    "Necessidade de Capital de Giro",
    "Taxa de Conversão da Receita em Caixa",
    "FCO",
    "FCO / EBITDA",
    "FCO / Lucro Líquido",
    "FCL",
    "Investimentos / Receita",
    "Investimentos / Depreciação",
    "Cobertura de Juros",
    "FCO / Dívida Bruta",
    "Distribuição / Lucro Líquido",
    "Cobertura de Dividendos",
    "DuPont - Margem Líquida",
    "DuPont - Giro do Ativo",
    "DuPont - Alavancagem",
    "ROE DuPont",
]

COLUNAS_MONETARIAS = {
    "EBITDA", "EVA", "NOPAT", "MVA Aproximado",
    "CCL", "Necessidade de Capital de Giro", "FCO", "FCL",
}

COLUNAS_PERCENTUAIS = {
    "Margem EBITDA", "Margem Líquida", "ROE", "ROIC", "WACC",
    "Taxa de Conversão da Receita em Caixa", "Investimentos / Receita",
    "FCO / Dívida Bruta", "Distribuição / Lucro Líquido",
    "DuPont - Margem Líquida", "ROE DuPont",
}

COLUNAS_EM_DIAS = {"PMR", "PMP", "Ciclo Financeiro"}


def _rotulo_cenario(valor):
    if pd.isna(valor):
        return "Cenário sem identificação"

    texto = str(valor).strip()

    if not texto:
        return "Cenário sem identificação"

    encontrados = re.findall(r"\d+", texto)

    if encontrados:
        return f"Cenário {int(encontrados[-1])}"

    return texto


def _extrair_ano(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    try:
        numero = float(texto)
        if numero.is_integer():
            return int(numero)
    except ValueError:
        pass

    encontrados = re.findall(r"\d+", texto)

    if not encontrados:
        return pd.NA

    return int(encontrados[0])


def _preparar_dados():
    df = carregar_indicadores()

    obrigatorias = {"Cenario", "Ano", "EBITDA", "Margem EBITDA"}
    ausentes = obrigatorias.difference(df.columns)

    if ausentes:
        raise ValueError(
            "A planilha de indicadores não contém as colunas necessárias: "
            + ", ".join(sorted(ausentes))
        )


    if "Ano_Numero" in df.columns:
        anos = pd.to_numeric(df["Ano_Numero"], errors="coerce")
    else:
        anos = pd.Series(pd.NA, index=df.index, dtype="Float64")

    if anos.isna().all() and "Ano" in df.columns:
        anos = df["Ano"].map(_extrair_ano)


    dados = df.copy()
    dados["Ano_Numero"] = pd.to_numeric(anos, errors="coerce")
    dados["Cenario"] = dados["Cenario"].astype("string").str.strip()

    indicadores_existentes = [
        coluna for coluna in COLUNAS_COMPARACAO
        if coluna in dados.columns
    ]

    for coluna in indicadores_existentes:
        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors="coerce",
        )


    return dados.dropna(subset=["Ano_Numero"])


def _moeda_mi(valor):
    if pd.isna(valor):
        return "N/D"

    valor = float(valor) / 1_000_000
    sinal = "−" if valor < 0 else ""

    if abs(valor) >= 1000:
        numero = f"{abs(valor) / 1000:,.2f}"
        unidade = "bi"
    else:
        numero = f"{abs(valor):,.2f}"
        unidade = "mi"

    numero = numero.replace(",", "X").replace(".", ",").replace("X", ".")

    return f"{sinal}R$ {numero} {unidade}"


def _percentual(valor):
    if pd.isna(valor):
        return "N/D"

    return f"{float(valor):.2%}".replace(".", ",")


def _formatar_indicador(indicador, valor):
    if pd.isna(valor):
        return "—"

    if indicador in COLUNAS_MONETARIAS:
        return _moeda_mi(valor)

    if indicador in COLUNAS_PERCENTUAIS:
        return _percentual(valor)

    if indicador in COLUNAS_EM_DIAS:
        return f"{float(valor):.1f} dias".replace(".", ",")

    if indicador in {
        "FCO / EBITDA",
        "FCO / Lucro Líquido",
        "Investimentos / Depreciação",
        "Cobertura de Juros",
        "Cobertura de Dividendos",
        "DuPont - Giro do Ativo",
        "DuPont - Alavancagem",
    }:
        return f"{float(valor):.2f}x".replace(".", ",")

    return f"{float(valor):.2f}".replace(".", ",")


def _grafico_cenarios(dados, selecionados):
    dados_grafico = dados.dropna(
        subset=["Cenario", "EBITDA", "Margem EBITDA"]
    ).copy()

    if dados_grafico.empty:
        st.info(
            "Não há valores de EBITDA e Margem EBITDA suficientes "
            "para montar o gráfico neste ano."
        )
        return

    dados_grafico["EBITDA_mi"] = dados_grafico["EBITDA"] / 1_000_000
    dados_grafico["Cenario_label"] = dados_grafico["Cenario"].map(
        _rotulo_cenario
    )
    dados_grafico["Selecionado"] = dados_grafico["Cenario"].isin(
        selecionados
    )

    grafico = (
        alt.Chart(dados_grafico)
        .mark_circle(size=75, opacity=0.8)
        .encode(
            x=alt.X(
                "EBITDA_mi:Q",
                title="EBITDA (R$ mi)",
                axis=alt.Axis(format=",.1f"),
            ),
            y=alt.Y(
                "Margem EBITDA:Q",
                title="Margem EBITDA",
                axis=alt.Axis(format=".0%"),
            ),
            color=alt.condition(
                "datum.Selecionado",
                alt.value("#1677E8"),
                alt.value("#AFC3D8"),
            ),
            tooltip=[
                alt.Tooltip("Cenario_label:N", title="Cenário"),
                alt.Tooltip(
                    "EBITDA_mi:Q",
                    title="EBITDA (R$ mi)",
                    format=",.2f",
                ),
                alt.Tooltip(
                    "Margem EBITDA:Q",
                    title="Margem EBITDA",
                    format=".2%",
                ),
            ],
        )
        .properties(height=340)
    )

    st.altair_chart(grafico, use_container_width=True)


def _indicadores_ordenados(colunas):
    grupos = list(dict.fromkeys(
        config["grupo"] for config in INDICADORES.values()
    ))

    def chave(indicador):
        grupo = INDICADORES.get(indicador, {}).get("grupo", "")
        posicao = grupos.index(grupo) if grupo in grupos else len(grupos)
        return (posicao, colunas.index(indicador))

    return sorted(colunas, key=chave)


def _tabela_comparacao(dados_ano, selecionados):
    selecionados_df = dados_ano.loc[
        dados_ano["Cenario"].isin(selecionados)
    ].copy()

    duplicados = selecionados_df.duplicated(
        subset=["Cenario"],
        keep=False,
    )

    with st.container(key="comp_tabela_comparacao"):
        st.markdown(
            '<div class="comp-card-title">'
            "Comparação lado a lado"
            "</div>",
            unsafe_allow_html=True,
        )

        if len(selecionados) < 2:
            st.markdown(
                '<div class="comp-card-note">'
                "Selecione pelo menos dois cenários para ver os indicadores "
                "lado a lado. O gráfico mostra todos os cenários do ano."
                "</div>",
                unsafe_allow_html=True,
            )
            return

        st.markdown(
            '<div class="comp-card-note">'
            "Indicadores agrupados por tema, para os cenários escolhidos."
            "</div>",
            unsafe_allow_html=True,
        )

        if duplicados.any():
            st.warning(
                "Há mais de um registro para pelo menos um cenário "
                "neste ano. A tabela comparativa foi ocultada para "
                "não agregar valores sem uma regra definida."
            )
            return

        existentes = [
            indicador
            for indicador in COLUNAS_COMPARACAO
            if indicador in selecionados_df.columns
        ]

        linhas = []

        for indicador in _indicadores_ordenados(existentes):
            linha = {
                "Grupo": INDICADORES.get(indicador, {}).get("grupo", ""),
                "Indicador": indicador,
            }

            for cenario in selecionados:
                registro = selecionados_df.loc[
                    selecionados_df["Cenario"] == cenario
                ].iloc[0]

                linha[_rotulo_cenario(cenario)] = _formatar_indicador(
                    indicador,
                    registro[indicador],
                )

            linhas.append(linha)

        st.dataframe(
            pd.DataFrame(linhas),
            hide_index=True,
            use_container_width=True,
            height=340,
        )


def _tabela_todos_os_cenarios(dados_ano):
    with st.container(key="comp_todos"):
        st.markdown(
            '<div class="comp-card-title">Todos os cenários</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="comp-card-note">'
            "Tabela completa, ordenada pelo EBITDA. Marque a opção abaixo "
            "para carregá-la."
            "</div>",
            unsafe_allow_html=True,
        )

        if not st.checkbox(
            "Mostrar a tabela de todos os cenários",
            key="comp_mostrar_todos",
        ):
            return

        indicadores_existentes = [
            coluna
            for coluna in COLUNAS_COMPARACAO
            if coluna in dados_ano.columns
        ]

        tabela = dados_ano.dropna(subset=["Cenario"]).copy()
        tabela["Cenário"] = tabela["Cenario"].map(_rotulo_cenario)

        tabela = tabela[
            ["Cenário", *indicadores_existentes]
        ].copy()

        tabela = tabela.sort_values(
            by="EBITDA",
            ascending=False,
        )

        for indicador in indicadores_existentes:
            tabela[indicador] = tabela[indicador].map(
                lambda valor, nome=indicador: _formatar_indicador(nome, valor)
            )

        st.dataframe(
            tabela,
            hide_index=True,
            use_container_width=True,
            height=420,
        )


def render_comparacao():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="comp_page"):
        try:
            df = _preparar_dados()
        except Exception as erro:
            st.error(f"Não foi possível carregar os indicadores: {erro}")
            return

        if df.empty:
            st.warning(
                "A planilha foi carregada, mas não encontrei anos válidos. "
                "Verifique os valores das colunas 'Ano' e 'Ano_Numero' "
                "na aba _Indicadores."
            )
            st.caption(
                f"Linhas carregadas: {len(df)}. "
                f"Colunas disponíveis: {', '.join(df.columns.astype(str))}"
            )
            return

        anos = sorted(df["Ano_Numero"].dropna().astype(int).unique().tolist())

        if not anos:
            st.warning(
                "Não encontrei anos válidos na aba _Indicadores. "
                "Confira se a coluna 'Ano' contém valores como 'Ano 1'."
            )
            return

        with st.container(key="comp_topo"):
            titulo, coluna_ano, coluna_botao = st.columns(
                [3.2, 1, 1.3],
                vertical_alignment="bottom",
            )

            with titulo:
                st.markdown(
                    """
                    <div class="comp-eyebrow">PAINEL FINANCEIRO</div>
                    <div class="comp-title">Comparação de cenários</div>
                    <div class="comp-subtitle">
                        Compare indicadores financeiros no mesmo ano.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with coluna_ano:
                ano = st.selectbox(
                    "Ano",
                    options=anos,
                    index=len(anos) - 1,
                    key="comp_ano",
                )

            with coluna_botao:
                if st.button(
                    "Nova simulação",
                    icon=":material/add:",
                    key="comp_nova_simulacao",
                    use_container_width=True,
                ):
                    st.session_state.pagina_atual = "Simular novo cenário"
                    st.rerun()

        dados_ano = df.loc[df["Ano_Numero"] == ano].copy()

        if dados_ano.empty:
            st.warning(f"Não há indicadores disponíveis para o ano {ano}.")
            return

        cenarios = (
            dados_ano["Cenario"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        with st.container(key="comp_selecao"):
            selecionados = st.multiselect(
                "Cenários para comparar",
                options=cenarios,
                format_func=_rotulo_cenario,
                key="comp_cenarios",
                placeholder="Selecione pelo menos dois cenários",
            )

        col_grafico, col_tabela = st.columns([1.1, 1], gap="medium")

        with col_grafico:
            with st.container(key="comp_grafico"):
                st.markdown(
                    '<div class="comp-card-title">EBITDA × Margem EBITDA</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="comp-card-note">'
                    "Cada ponto é um cenário do ano escolhido. Os cenários "
                    "selecionados aparecem em azul."
                    "</div>",
                    unsafe_allow_html=True,
                )

                _grafico_cenarios(dados_ano, selecionados)

        with col_tabela:
            _tabela_comparacao(dados_ano, selecionados)

        _tabela_todos_os_cenarios(dados_ano)

        como_interpretar(
            "comp",
            [
                "**Gráfico:** cada ponto é um cenário. Quanto mais à direita, "
                "maior o EBITDA; quanto mais acima, maior a margem.",
                "**Comparação lado a lado:** escolha dois ou mais cenários para "
                "ver todos os indicadores do mesmo ano, agrupados por tema.",
                "**Vazio ou N/D:** indicadores que usam o ano anterior (ROE, "
                "FCO, FCL e coberturas) não existem no Ano 1.",
                "**Unidades:** valores em reais aparecem em milhões (mi) ou "
                "bilhões (bi); percentuais em %; prazos em dias; coberturas "
                "e giros em vezes (x).",
            ],
        )

        st.caption(
            "Fonte: aba _Indicadores da planilha Analise_Financeira.xlsx. "
            "O gráfico e as tabelas usam a mesma unidade: valores em reais "
            "exibidos em milhões ou bilhões."
        )