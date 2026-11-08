import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from data.load_data import carregar_demonstrativo, carregar_indicadores


INDICADORES = {
    "Receita": ("demonstrativo", "DRE - Receita", "Resultados", "moeda", "maior"),
    "EBITDA": ("demonstrativo", "DRE - EBITDA", "Resultados", "moeda", "maior"),
    "Resultado Líquido": ("demonstrativo", "DRE - Resultado Líquido", "Resultados", "moeda", "maior"),
    "Geração de Caixa": ("demonstrativo", "FLU - Geração de Caixa", "Resultados", "moeda", "maior"),
    "NOPAT": ("indicadores", "NOPAT", "Resultados", "moeda", "maior"),
    "Margem EBITDA": ("indicadores", "Margem EBITDA", "Rentabilidade", "percentual", "maior"),
    "Margem Líquida": ("indicadores", "Margem Líquida", "Rentabilidade", "percentual", "maior"),
    "ROIC": ("indicadores", "ROIC", "Rentabilidade", "percentual", "maior"),
    "WACC": ("indicadores", "WACC", "Custo de capital", "percentual", "menor"),
    "EVA": ("indicadores", "EVA", "Geração de valor", "moeda", "maior"),
    "MVA Aproximado": ("indicadores", "MVA Aproximado", "Geração de valor", "moeda", "maior"),
    "LC": ("indicadores", "LC", "Liquidez", "multiplo", "maior"),
    "LS": ("indicadores", "LS", "Liquidez", "multiplo", "maior"),
    "ROE": ("indicadores", "ROE", "Rentabilidade", "percentual", "maior"),
    "ROE DuPont": ("indicadores", "ROE DuPont", "Rentabilidade", "percentual", "maior"),
    "DuPont - Margem Líquida": ("indicadores", "DuPont - Margem Líquida", "Rentabilidade", "percentual", "maior"),
    "DuPont - Giro do Ativo": ("indicadores", "DuPont - Giro do Ativo", "Rentabilidade", "multiplo", "maior"),
    "DuPont - Alavancagem": ("indicadores", "DuPont - Alavancagem", "Rentabilidade", "multiplo", "menor"),
    "CCL": ("indicadores", "CCL", "Capital de giro", "moeda", "maior"),
    "PMR": ("indicadores", "PMR", "Capital de giro", "dias", "menor"),
    "PMP": ("indicadores", "PMP", "Capital de giro", "dias", "maior"),
    "Ciclo Financeiro": ("indicadores", "Ciclo Financeiro", "Capital de giro", "dias", "menor"),
    "Necessidade de Capital de Giro": ("indicadores", "Necessidade de Capital de Giro", "Capital de giro", "moeda", "menor"),
    "Taxa de Conversão da Receita em Caixa": ("indicadores", "Taxa de Conversão da Receita em Caixa", "Fluxo de caixa", "percentual", "maior"),
    "FCO": ("indicadores", "FCO", "Fluxo de caixa", "moeda", "maior"),
    "FCO / EBITDA": ("indicadores", "FCO / EBITDA", "Fluxo de caixa", "multiplo", "maior"),
    "FCO / Lucro Líquido": ("indicadores", "FCO / Lucro Líquido", "Fluxo de caixa", "multiplo", "maior"),
    "FCL": ("indicadores", "FCL", "Fluxo de caixa", "moeda", "maior"),
    "Investimentos / Receita": ("indicadores", "Investimentos / Receita", "Investimentos", "percentual", "menor"),
    "Investimentos / Depreciação": ("indicadores", "Investimentos / Depreciação", "Investimentos", "multiplo", "maior"),
    "Cobertura de Juros": ("indicadores", "Cobertura de Juros", "Cobertura", "multiplo", "maior"),
    "FCO / Dívida Bruta": ("indicadores", "FCO / Dívida Bruta", "Cobertura", "percentual", "maior"),
    "Distribuição / Lucro Líquido": ("indicadores", "Distribuição / Lucro Líquido", "Distribuição", "percentual", "menor"),
    "Cobertura de Dividendos": ("indicadores", "Cobertura de Dividendos", "Distribuição", "multiplo", "maior"),
}


PAGE_STYLE = """
<style>

.st-key-tend_page {
    padding: 28px 32px 40px;
    gap: 20px !important;
}

.st-key-tend_filtros,
.st-key-tend_evolucao,
.st-key-tend_variacao,
.st-key-tend_distribuicao,
.st-key-tend_alertas,
.st-key-tend_ajuda {
    background: #FFFFFF;
    border: 1px solid #DCE7F1;
    border-radius: 16px;
    box-shadow: 0 3px 12px rgba(0,55,100,.06);
    padding: 22px 24px;
}

.st-key-tend_filtros {
    padding: 18px 22px;
}

.st-key-tend_filtros label p {
    font-size: 15px !important;
    color: #49647E !important;
}

.st-key-tend_page p,
.st-key-tend_page label,
.st-key-tend_page .stCaption {
    font-size: 15px;
}

.st-key-tend_page h1,
.st-key-tend_page h2,
.st-key-tend_page h3 {
    color: #173B63;
}

</style>
"""


def _numero(valor, casas=2):

    if pd.isna(valor):
        return "—"

    texto = (
        f"{abs(float(valor)):,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"−{texto}" if float(valor) < 0 else texto


def _formatar(valor, unidade):

    if pd.isna(valor):
        return "—"

    if unidade == "moeda":

        mi = float(valor) / 1_000_000

        if abs(mi) >= 1000:
            return f"R$ {_numero(mi / 1000)} bi"

        return f"R$ {_numero(mi)} mi"

    if unidade == "percentual":
        return f"{_numero(valor * 100)}%"

    if unidade == "multiplo":
        return f"{_numero(valor)}x"

    if unidade == "dias":
        return f"{_numero(valor, 1)} dias"

    return _numero(valor)


def _carregar_indicador(nome):

    fonte, coluna, _, _, _ = INDICADORES[nome]

    df = (
        carregar_demonstrativo()
        if fonte == "demonstrativo"
        else carregar_indicadores()
    )

    faltantes = {"Ano", "Cenario", coluna}.difference(df.columns)

    if faltantes:
        raise ValueError(
            f"Colunas ausentes na fonte de {nome}: "
            f"{', '.join(sorted(faltantes))}"
        )

    if fonte == "indicadores" and "Ano_Numero" in df.columns:

        dados = df[
            ["Ano", "Ano_Numero", "Cenario", coluna]
        ].copy()

        dados["Ano"] = pd.to_numeric(
            dados["Ano_Numero"],
            errors="coerce"
        )

    else:

        dados = df[
            ["Ano", "Cenario", coluna]
        ].copy()

        dados["Ano"] = pd.to_numeric(
            dados["Ano"].astype(str).str.extract(
                r"(\d+)",
                expand=False
            ),
            errors="coerce"
        )

    dados["Cenario"] = pd.to_numeric(
        dados["Cenario"].astype(str).str.extract(
            r"(\d+)(?:\.0+)?\s*$",
            expand=False
        ),
        errors="coerce"
    )

    dados["Valor"] = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    )

    dados = dados.dropna(
        subset=["Ano", "Cenario", "Valor"]
    )

    dados["Ano"] = dados["Ano"].astype(int)
    dados["Cenario"] = dados["Cenario"].astype(int)


    dados = (
        dados.groupby(
            ["Ano", "Cenario"],
            as_index=False
        )["Valor"]
        .mean()
        .sort_values(["Ano", "Cenario"])
    )

    return dados


def _resumo_anual(dados):

    return (
        dados.groupby("Ano")["Valor"]
        .agg(
            Media="mean",
            Mediana="median",
            P10=lambda s: s.quantile(.10),
            P25=lambda s: s.quantile(.25),
            P75=lambda s: s.quantile(.75),
            P90=lambda s: s.quantile(.90),
            Minimo="min",
            Maximo="max",
            Cenarios="count"
        )
        .reset_index()
        .sort_values("Ano")
    )


def _variacoes(resumo):

    df = resumo[["Ano", "Media"]].copy()

    anterior = df["Media"].shift(1)

    df["Variacao"] = df["Media"].pct_change()

    df.loc[
        anterior.abs() < 1e-12,
        "Variacao"
    ] = np.nan

    return df


def _alertas(resumo, variacoes):

    alertas = []

    validas = variacoes.dropna()


    if len(validas) >= 4:

        mediana = validas["Variacao"].median()

        mad = (
            validas["Variacao"] - mediana
        ).abs().median()

        limite = max(3 * 1.4826 * mad, .10)

        for _, linha in validas.iterrows():

            if abs(linha["Variacao"] - mediana) > limite:

                alertas.append((
                    "warning",
                    "Oscilação fora do padrão histórico",
                    (
                        f"No Ano {int(linha['Ano'])}, a variação "
                        f"da média foi {linha['Variacao']:+.1%}, "
                        "distante do comportamento habitual."
                    )
                ))


    temp = resumo.copy()

    temp["Dispersao"] = (
        (temp["P90"] - temp["P10"])
        / temp["Media"].abs().replace(0, np.nan)
    )

    serie = (
        temp["Dispersao"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if len(serie) >= 4:

        q1 = serie.quantile(.25)
        q3 = serie.quantile(.75)

        limite = q3 + 1.5 * (q3 - q1)

        for _, linha in temp.dropna(
            subset=["Dispersao"]
        ).iterrows():

            if linha["Dispersao"] > limite:

                alertas.append((
                    "warning",
                    "Alta dispersão entre cenários",
                    (
                        f"No Ano {int(linha['Ano'])}, a faixa "
                        f"P10–P90 equivale a "
                        f"{linha['Dispersao']:.1%} da média, "
                        "acima do padrão histórico."
                    )
                ))

    if not alertas:

        return [(
            "info",
            "Nenhum sinal estatístico relevante identificado",
            (
                "Os critérios aplicados não identificaram "
                "oscilações ou dispersões incomuns no período selecionado."
            )
        )]

    return alertas


def _grafico_evolucao(dados, resumo, cenario):

    destaque = dados.loc[
        dados["Cenario"] == cenario,
        ["Ano", "Valor"]
    ].copy()

    destaque["Série"] = "Cenário selecionado"

    media = resumo[
        ["Ano", "Media"]
    ].rename(
        columns={"Media": "Valor"}
    ).copy()

    media["Série"] = "Média dos cenários"

    linhas = pd.concat(
        [destaque, media],
        ignore_index=True
    )

    faixa = alt.Chart(resumo).mark_area(
        color="#8CBCE5",
        opacity=.25
    ).encode(
        x=alt.X("Ano:O", title="Ano", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("P10:Q", title="Valor"),
        y2="P90:Q",
        tooltip=[
            "Ano:O",
            alt.Tooltip("P10:Q", format=",.2f"),
            alt.Tooltip("P90:Q", format=",.2f")
        ]
    )

    linha = alt.Chart(linhas).mark_line(
        point=True,
        strokeWidth=3
    ).encode(
        x=alt.X("Ano:O", title="Ano", axis=alt.Axis(labelAngle=0)),
        y=alt.Y(
            "Valor:Q",
            title="Valor",
            axis=alt.Axis(format=",.2f")
        ),
        color=alt.Color(
            "Série:N",
            scale=alt.Scale(
                domain=[
                    "Cenário selecionado",
                    "Média dos cenários"
                ],
                range=[
                    "#1680DB",
                    "#329879"
                ]
            )
        ),
        tooltip=[
            "Ano:O",
            "Série:N",
            alt.Tooltip("Valor:Q", format=",.2f")
        ]
    )

    return (
        (faixa + linha)
        .properties(height=320)
        .configure_view(strokeWidth=0)
        .configure_axis(
            gridColor="#EDF2F7",
            labelColor="#526B83",
            titleColor="#294A68",
            labelFontSize=13,
            titleFontSize=14
        )
    )


def _grafico_variacao(variacoes):

    dados = variacoes.dropna(
        subset=["Variacao"]
    ).copy()

    if dados.empty:
        return None

    dados["Sinal"] = np.where(
        dados["Variacao"] >= 0,
        "Positiva",
        "Negativa"
    )

    return (
        alt.Chart(dados)
        .mark_bar(
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        )
        .encode(
            x=alt.X("Ano:O", title="Ano", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "Variacao:Q",
                title="Variação anual",
                axis=alt.Axis(format=".0%")
            ),
            color=alt.Color(
                "Sinal:N",
                scale=alt.Scale(
                    domain=["Positiva", "Negativa"],
                    range=["#329879", "#D92D20"]
                ),
                legend=None
            ),
            tooltip=[
                "Ano:O",
                alt.Tooltip(
                    "Variacao:Q",
                    title="Variação",
                    format=".2%"
                )
            ]
        )
        .properties(height=290)
        .configure_view(strokeWidth=0)
        .configure_axis(
            gridColor="#EDF2F7",
            labelFontSize=13,
            titleFontSize=14
        )
    )


def _grafico_distribuicao(dados, ano):

    recorte = dados.loc[
        dados["Ano"] == ano,
        ["Valor"]
    ].dropna().copy()

    if recorte.empty:
        return None

    media = recorte["Valor"].mean()
    mediana = recorte["Valor"].median()

    histograma = alt.Chart(recorte).mark_bar(
        color="#4C91C6",
        opacity=.85,
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        x=alt.X(
            "Valor:Q",
            bin=alt.Bin(maxbins=25),
            title="Faixas de valores"
        ),
        y=alt.Y(
            "count():Q",
            title="Quantidade de cenários"
        ),
        tooltip=[
            alt.Tooltip(
                "count():Q",
                title="Quantidade de cenários"
            )
        ]
    )

    linha_media = alt.Chart(
        pd.DataFrame({"referencia": [media]})
    ).mark_rule(
        color="#D97706",
        strokeWidth=3,
        strokeDash=[6, 4]
    ).encode(
        x="referencia:Q"
    )

    linha_mediana = alt.Chart(
        pd.DataFrame({"referencia": [mediana]})
    ).mark_rule(
        color="#16805D",
        strokeWidth=3
    ).encode(
        x="referencia:Q"
    )

    return (
        (histograma + linha_media + linha_mediana)
        .properties(height=300)
        .configure_view(strokeWidth=0)
        .configure_axis(
            gridColor="#EAF0F6",
            labelColor="#526B83",
            titleColor="#294A68",
            labelFontSize=13,
            titleFontSize=14
        )
    )


def _kpi(coluna, titulo, valor, nota):

    with coluna:

        with st.container(border=True):

            st.markdown(f"**{titulo}**")

            st.markdown(
                f"<h2 style='color:#176BA8; margin: 8px 0;'>{valor}</h2>",
                unsafe_allow_html=True
            )

            st.caption(nota)


def resumo_evolucao(resumo, variacoes, direcao):
    """CAGR, maior variação, melhor e pior ano (usado pela tela e pelo PDF).

    Devolve (cagr, maior_txt, melhor_txt, pior_txt); cagr pode ser NaN.
    """
    validos = resumo.dropna(
        subset=["Media"]
    )

    cagr = np.nan

    if len(validos) >= 2:

        inicial = validos.iloc[0]["Media"]
        final = validos.iloc[-1]["Media"]

        if inicial > 0 and final > 0:

            cagr = (
                (final / inicial)
                ** (1 / (len(validos) - 1))
            ) - 1

    vv = variacoes.dropna(
        subset=["Variacao"]
    )

    if vv.empty:
        return cagr, "—", "—", "—"

    maior = vv.loc[
        vv["Variacao"].abs().idxmax()
    ]

    melhor = vv.loc[
        vv["Variacao"].idxmax()
    ]

    pior = vv.loc[
        vv["Variacao"].idxmin()
    ]

    if direcao == "menor":
        melhor, pior = pior, melhor

    maior_txt = (
        f"{maior['Variacao']:+.1%} "
        f"· Ano {int(maior['Ano'])}"
    )

    return cagr, maior_txt, f"Ano {int(melhor['Ano'])}", f"Ano {int(pior['Ano'])}"


def render_tendencias():

    st.markdown(
        PAGE_STYLE,
        unsafe_allow_html=True
    )

    with st.container(key="tend_page"):


        st.markdown(
            "##### PAINEL FINANCEIRO"
        )

        st.title("Tendências")

        st.caption(
            "Acompanhe a evolução histórica, a distribuição "
            "dos cenários e os principais sinais de atenção."
        )


        nomes = list(INDICADORES)

        f1, f2, f3, f4 = st.columns(
            [1, 1.2, 1.35, 1.35],
            gap="medium"
        )

        with f1:

            indicador = st.selectbox(
                "Indicador principal",
                nomes,
                index=1,
                key="tend_indicador"
            )

        with f2:

            secundarias = (
                ["Nenhum"]
                + [n for n in nomes if n != indicador]
            )

            if (
                st.session_state.get("tend_secundario")
                not in secundarias
            ):
                st.session_state["tend_secundario"] = "Nenhum"

            secundario = st.selectbox(
                "Indicador secundário",
                secundarias,
                key="tend_secundario"
            )

        try:

            dados = _carregar_indicador(indicador)

        except Exception as erro:

            st.error(
                f"Não foi possível carregar {indicador}: {erro}"
            )
            return

        if dados.empty:

            st.warning(
                f"Não existem valores válidos para {indicador}."
            )
            return

        anos = sorted(
            dados["Ano"].unique().tolist()
        )

        cenarios = sorted(
            dados["Cenario"].unique().tolist()
        )

        with f3:

            periodo = st.select_slider(
                "Período analisado",
                options=anos,
                value=(anos[0], anos[-1]),
                format_func=lambda ano: f"Ano {ano}",
                key="tend_periodo"
            )

        with f4:

            if (
                st.session_state.get("tend_cenario")
                not in cenarios
            ):
                st.session_state["tend_cenario"] = cenarios[0]

            cenario = st.selectbox(
                "Destacar cenário",
                cenarios,
                format_func=lambda c: f"Cenário {c}",
                key="tend_cenario"
            )


        dados = dados[
            dados["Ano"].between(
                periodo[0],
                periodo[1]
            )
        ].copy()

        if dados.empty:

            st.info(
                "Não há dados no período selecionado."
            )
            return

        resumo = _resumo_anual(dados)
        variacoes = _variacoes(resumo)

        _, _, _, unidade, direcao = INDICADORES[indicador]


        with st.container(key="tend_evolucao"):

            st.subheader(
                "Evolução histórica e faixa dos cenários"
            )

            st.caption(
                "A linha destaca o cenário escolhido; a média resume "
                "os cenários disponíveis e a faixa mostra os percentis "
                "10 a 90."
            )

            st.altair_chart(
                _grafico_evolucao(
                    dados,
                    resumo,
                    cenario
                ),
                use_container_width=True
            )

            with st.expander(
                "Entenda a faixa P10–P90",
                expanded=True
            ):

                st.markdown("**P10 — 10º percentil**")

                st.write(
                    "10% dos cenários apresentam valores iguais "
                    "ou inferiores a esse ponto."
                )

                st.markdown("**P90 — 90º percentil**")

                st.write(
                    "90% dos cenários apresentam valores iguais "
                    "ou inferiores a esse ponto."
                )

                st.markdown(
                    "**O que significa a faixa P10–P90?**"
                )

                st.write(
                    "Ela representa os 80% centrais dos cenários. "
                    "É útil para visualizar a variação dos resultados "
                    "sem deixar que valores extremos dominem a análise."
                )


        col_var, col_dist = st.columns(
            2,
            gap="medium"
        )

        with col_var:

            with st.container(key="tend_variacao"):

                st.subheader("Variação anual")

                st.caption(
                    "Variação percentual da média dos cenários "
                    "em relação ao ano anterior."
                )

                graf = _grafico_variacao(variacoes)

                if graf is None:

                    st.info(
                        "Não há anos consecutivos suficientes "
                        "para calcular a variação."
                    )

                else:

                    st.altair_chart(
                        graf,
                        use_container_width=True
                    )

        with col_dist:

            with st.container(key="tend_distribuicao"):

                st.subheader("Distribuição dos cenários")

                st.caption(
                    "Veja como os resultados dos cenários estão "
                    "concentrados em diferentes faixas de valores."
                )

                anos_disponiveis = sorted(
                    dados["Ano"].unique()
                )

                ano_dist = st.selectbox(
                    "Ano da distribuição",
                    anos_disponiveis,
                    index=len(anos_disponiveis) - 1,
                    format_func=lambda a: f"Ano {a}",
                    key="tend_ano_dist"
                )

                distribuicao = _grafico_distribuicao(
                    dados,
                    ano_dist
                )

                if distribuicao is None:

                    st.info(
                        "Não há dados disponíveis para este ano."
                    )

                else:

                    st.altair_chart(
                        distribuicao,
                        use_container_width=True
                    )

                recorte_dist = dados.loc[
                    dados["Ano"] == ano_dist,
                    "Valor"
                ]

                quantidade = recorte_dist.count()
                media_dist = recorte_dist.mean()
                mediana_dist = recorte_dist.median()

                st.caption(
                    f"{quantidade:,} cenários com dados válidos."
                    .replace(",", ".")
                )

                st.markdown(
                    f"**Média:** {_formatar(media_dist, unidade)}"
                    f"  |  **Mediana:** {_formatar(mediana_dist, unidade)}"
                )

                st.caption(
                    "Linha verde: mediana | Linha laranja: média."
                )


        with st.container(key="tend_alertas"):

            st.subheader("Alertas automáticos")

            st.caption(
                "Sinais estatísticos do período selecionado. "
                "Não são previsões."
            )

            alertas = _alertas(
                resumo,
                variacoes
            )

            for tipo, titulo, texto in alertas[:6]:

                st.error(
                    f"**{titulo}**\n\n{texto}"
                )


        cagr, maior_txt, melhor_txt, pior_txt = resumo_evolucao(
            resumo, variacoes, direcao
        )

        st.subheader("Resumo da evolução")

        st.caption(
            "Indicadores calculados com base na média anual "
            "dos cenários válidos."
        )

        k1, k2, k3, k4 = st.columns(
            4,
            gap="medium"
        )

        _kpi(
            k1,
            "Crescimento médio anual (CAGR)",
            f"{cagr:+.1%}" if pd.notna(cagr) else "N/A",
            "Taxa composta de crescimento entre o primeiro e o último ano."
        )

        _kpi(
            k2,
            "Maior variação anual",
            maior_txt,
            "Maior oscilação percentual observada no período."
        )

        _kpi(
            k3,
            "Melhor ano",
            melhor_txt,
            "Considera a direção financeira do indicador."
        )

        _kpi(
            k4,
            "Pior ano",
            pior_txt,
            "Considera a direção financeira do indicador."
        )


        if secundario != "Nenhum":

            try:

                sec = _carregar_indicador(secundario)

                sec = sec[
                    sec["Ano"].between(
                        periodo[0],
                        periodo[1]
                    )
                ]

                sec_resumo = _resumo_anual(sec)

                comparacao = (
                    resumo[["Ano", "Media"]]
                    .rename(columns={"Media": indicador})
                    .merge(
                        sec_resumo[["Ano", "Media"]].rename(
                            columns={"Media": secundario}
                        ),
                        on="Ano",
                        how="inner"
                    )
                    .melt(
                        id_vars="Ano",
                        var_name="Indicador",
                        value_name="Média"
                    )
                )

                if not comparacao.empty:

                    st.subheader(
                        f"Comparação de médias anuais: "
                        f"{indicador} e {secundario}"
                    )

                    st.caption(
                        "Cada indicador mantém sua unidade original. "
                        "Compare principalmente a direção das tendências."
                    )

                    graf_sec = (
                        alt.Chart(comparacao)
                        .mark_line(
                            point=True,
                            strokeWidth=3
                        )
                        .encode(
                            x=alt.X(
                                "Ano:O",
                                title="Ano",
                                axis=alt.Axis(labelAngle=0)
                            ),
                            y=alt.Y(
                                "Média:Q",
                                title="Média anual",
                                axis=alt.Axis(format=",.2f")
                            ),
                            color=alt.Color(
                                "Indicador:N",
                                title="Indicador"
                            ),
                            tooltip=[
                                "Ano",
                                "Indicador",
                                alt.Tooltip(
                                    "Média:Q",
                                    format=",.2f"
                                )
                            ]
                        )
                        .properties(height=280)
                        .configure_view(strokeWidth=0)
                    )

                    st.altair_chart(
                        graf_sec,
                        use_container_width=True
                    )

            except Exception as erro:

                st.warning(
                    f"Não foi possível carregar o indicador secundário: {erro}"
                )


        with st.container(key="tend_ajuda"):

            with st.expander(
                "Como interpretar esta tela"
            ):

                st.markdown(
                    """
                    - **Média dos cenários:** média dos valores válidos de cada ano.
                    - **P10:** valor abaixo ou igual ao de 10% dos cenários.
                    - **P90:** valor abaixo ou igual ao de 90% dos cenários.
                    - **Faixa P10–P90:** representa os 80% centrais dos resultados.
                    - **Histograma:** mostra a quantidade de cenários em cada faixa de valores.
                    - **Média e mediana:** ajudam a comparar o centro da distribuição e identificar possíveis assimetrias.
                    - **Variação anual:** mudança percentual da média em relação ao ano anterior.
                    - **Alertas:** identificam oscilações e dispersões incomuns em relação ao histórico. São sinais para investigação, não previsões.
                    """
                )