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


GRUPOS_GRAFICO = {
    "Resultado e caixa (R$)": ["EBITDA", "NOPAT", "EVA", "FCO", "FCL"],
    "Capital de giro e valor (R$)": [
        "CCL",
        "Necessidade de Capital de Giro",
        "MVA Aproximado",
    ],
    "Margens e retornos (%)": [
        "Margem EBITDA",
        "Margem Líquida",
        "ROIC",
        "ROE",
    ],
    "Conversão e investimentos (%)": [
        "Taxa de Conversão da Receita em Caixa",
        "FCO / Dívida Bruta",
        "Investimentos / Receita",
        "Distribuição / Lucro Líquido",
    ],
    "Prazos (dias)": ["PMR", "PMP", "Ciclo Financeiro"],
    "Coberturas e giro (vezes)": [
        "FCO / EBITDA",
        "FCO / Lucro Líquido",
        "Cobertura de Juros",
        "Cobertura de Dividendos",
        "Investimentos / Depreciação",
        "DuPont - Giro do Ativo",
        "DuPont - Alavancagem",
    ],
}

CORES_CENARIOS = [
    "#1677E8",
    "#F59E0B",
    "#10B981",
    "#8B5CF6",
    "#EF4444",
    "#06B6D4",
    "#EC4899",
    "#84CC16",
]


def _escala_grupo(valores, formato):
    if formato == "moeda":
        if valores.abs().max() >= 1_000_000_000:
            return 1 / 1_000_000_000, "R$ bilhões"

        return 1 / 1_000_000, "R$ milhões"

    if formato == "percentual":
        return 100, "%"

    if formato == "dias":
        return 1, "dias"

    if formato == "multiplo":
        return 1, "vezes"

    return 1, ""


def _numero_curto(valor):
    return (
        f"{valor:,.1f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def _grafico_comparacao(dados, selecionados, indicadores):
    if not selecionados:
        st.info("Selecione pelo menos um cenário no filtro acima.")
        return

    existentes = [
        indicador
        for indicador in indicadores
        if indicador in dados.columns
    ]

    base = dados.loc[dados["Cenario"].isin(selecionados)].copy()

    registros = []

    for _, linha in base.iterrows():
        for indicador in existentes:
            registros.append({
                "Cenário": _rotulo_cenario(linha["Cenario"]),
                "Indicador": indicador,
                "bruto": linha[indicador],
            })

    longo = pd.DataFrame(registros)

    if longo.empty:
        st.info("Não há valores para os cenários e indicadores escolhidos.")
        return

    sem_valor = sorted(
        longo.loc[longo["bruto"].isna(), "Indicador"].unique().tolist()
    )

    longo = longo.dropna(subset=["bruto"]).copy()

    if longo.empty:
        st.info(
            "Os indicadores escolhidos não têm valores neste ano. "
            "Os que usam o ano anterior começam no Ano 2."
        )
        return

    formato = INDICADORES.get(existentes[0], {}).get("formato", "numero")
    fator, unidade = _escala_grupo(longo["bruto"], formato)

    longo["Valor"] = longo["bruto"] * fator
    longo["Rótulo"] = longo["Valor"].map(_numero_curto)

    ordem_cenarios = [_rotulo_cenario(c) for c in selecionados]
    cores = [
        CORES_CENARIOS[i % len(CORES_CENARIOS)]
        for i in range(len(ordem_cenarios))
    ]

    altura = max(260, len(existentes) * len(ordem_cenarios) * 26 + 70)

    base_grafico = alt.Chart(longo).encode(
        y=alt.Y(
            "Indicador:N",
            sort=existentes,
            title=None,
            axis=alt.Axis(labelLimit=260),
        ),
        yOffset=alt.YOffset("Cenário:N", sort=ordem_cenarios),
    )

    barras = base_grafico.mark_bar(cornerRadiusEnd=3).encode(
        x=alt.X(
            "Valor:Q",
            title=unidade,
            axis=alt.Axis(labelAngle=0, format=",.1f"),
        ),
        color=alt.Color(
            "Cenário:N",
            sort=ordem_cenarios,
            scale=alt.Scale(domain=ordem_cenarios, range=cores),
            legend=alt.Legend(title=None, orient="bottom"),
        ),
        tooltip=[
            alt.Tooltip("Cenário:N"),
            alt.Tooltip("Indicador:N"),
            alt.Tooltip("Valor:Q", title=unidade or "Valor", format=",.2f"),
        ],
    )

    rotulos_positivos = (
        base_grafico
        .transform_filter("datum.Valor >= 0")
        .mark_text(align="left", dx=4, fontSize=11, color="#2B3A4E")
        .encode(x="Valor:Q", text="Rótulo:N")
    )

    rotulos_negativos = (
        base_grafico
        .transform_filter("datum.Valor < 0")
        .mark_text(align="right", dx=-4, fontSize=11, color="#2B3A4E")
        .encode(x="Valor:Q", text="Rótulo:N")
    )

    st.altair_chart(
        (barras + rotulos_positivos + rotulos_negativos).properties(
            height=altura
        ),
        use_container_width=True,
    )

    if sem_valor:
        st.caption(
            "Sem valor neste ano: " + ", ".join(sem_valor) + "."
        )


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
                "Selecione pelo menos dois cenários para ver todos os "
                "indicadores lado a lado."
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


def cenarios_padrao(dados_ano):
    """Na primeira visita, compara os dois cenários de maior EBITDA do ano."""
    return (
        dados_ano.dropna(subset=["EBITDA"])
        .nlargest(2, "EBITDA")["Cenario"]
        .tolist()
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

        if "comp_cenarios" not in st.session_state:
            st.session_state["comp_cenarios"] = cenarios_padrao(dados_ano)

        st.session_state["comp_cenarios"] = [
            cenario
            for cenario in st.session_state["comp_cenarios"]
            if cenario in cenarios
        ]

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
                grupos_disponiveis = {
                    nome: [
                        indicador
                        for indicador in indicadores
                        if indicador in dados_ano.columns
                        and dados_ano[indicador].notna().any()
                    ]
                    for nome, indicadores in GRUPOS_GRAFICO.items()
                }
                grupos_disponiveis = {
                    nome: indicadores
                    for nome, indicadores in grupos_disponiveis.items()
                    if indicadores
                }

                st.markdown(
                    '<div class="comp-card-title">'
                    "Comparação dos cenários selecionados"
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="comp-card-note">'
                    "Cada cor é um cenário. Escolha o grupo e os indicadores "
                    "para ver os cenários lado a lado."
                    "</div>",
                    unsafe_allow_html=True,
                )

                if not grupos_disponiveis:
                    st.info("Não há indicadores suficientes para montar o gráfico.")
                else:
                    escolha_grupo, escolha_indicadores = st.columns([1, 1.4])

                    with escolha_grupo:
                        nome_grupo = st.selectbox(
                            "Grupo de indicadores",
                            options=list(grupos_disponiveis.keys()),
                            key="comp_grupo_grafico",
                        )

                    opcoes_grupo = grupos_disponiveis[nome_grupo]

                    with escolha_indicadores:
                        indicadores_escolhidos = st.multiselect(
                            "Indicadores no gráfico",
                            options=opcoes_grupo,
                            default=opcoes_grupo,
                            key=f"comp_indicadores_{nome_grupo}",
                        )

                    if indicadores_escolhidos:
                        _grafico_comparacao(
                            dados_ano, selecionados, indicadores_escolhidos
                        )
                    else:
                        st.info("Selecione pelo menos um indicador.")

        with col_tabela:
            _tabela_comparacao(dados_ano, selecionados)

        _tabela_todos_os_cenarios(dados_ano)

        como_interpretar(
            "comp",
            [
                "**Gráfico:** cada cor é um cenário escolhido no filtro. As barras "
                "mostram o valor de cada indicador no ano selecionado, com o "
                "número ao lado.",
                "**Grupos:** os indicadores são agrupados pela mesma unidade "
                "(reais, %, dias ou vezes) para que as barras possam ser "
                "comparadas entre si.",
                "**Barras para a esquerda:** valores negativos, como um FCL "
                "negativo.",
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
            "Valores em reais aparecem em milhões ou bilhões; percentuais "
            "em %, prazos em dias e coberturas em vezes."
        )