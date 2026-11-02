import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from data.load_data import carregar_demonstrativo, carregar_indicadores

# Nome exibido: configuração da fonte, coluna, grupo, unidade e direção favorável.
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
}

PAGE_STYLE = """
<style>
.st-key-tend_page {padding:28px 32px 40px;gap:16px!important;}
.tend-eyebrow {font-size:11px;font-weight:700;letter-spacing:.12em;color:var(--cti-blue);margin-bottom:4px;}
.tend-title {font-size:30px;font-weight:700;color:var(--cti-text);line-height:1.15;}
.tend-subtitle {font-size:13px;color:var(--cti-muted);margin-top:4px;}
.st-key-tend_filtros,.st-key-tend_evolucao,.st-key-tend_variacao,.st-key-tend_distribuicao,.st-key-tend_alertas,.st-key-tend_ajuda {
 background:#fff;border:1px solid #E1ECF7;border-radius:14px;box-shadow:0 2px 10px rgba(0,75,133,.05);padding:18px 22px;
}
.st-key-tend_filtros {padding:14px 22px;}
.st-key-tend_filtros label p {font-size:12px!important;color:var(--cti-muted)!important;}
.tend-card-title {font-size:15px;font-weight:700;color:var(--cti-text);}
.tend-card-note {font-size:12px;color:#8AA4BF;margin:3px 0 12px;line-height:1.5;}
.tend-kpi-label {font-size:12px;color:var(--cti-muted);}
.tend-kpi-value {font-size:clamp(20px,1.9vw,26px);font-weight:700;color:var(--cti-blue);line-height:1.3;}
.tend-kpi-note {font-size:11.5px;color:#8AA4BF;line-height:1.4;}
.tend-alert {border:1px solid #E8EDF3;border-radius:10px;padding:12px 14px;margin:8px 0;background:#FAFCFE;}
.tend-alert-title {font-size:13px;font-weight:700;color:#173B63;margin-bottom:4px;}
.tend-alert-text {font-size:12px;color:#61748A;line-height:1.55;}
.tend-alert.warning {background:#FFF9ED;border-color:#F2E2BC;}
.tend-alert.positive {background:#F1FAF6;border-color:#D4EDE1;}
.tend-alert.info {background:#F5F9FD;border-color:#E1ECF7;}
</style>
"""


def _numero(valor, casas=2):
    if pd.isna(valor):
        return "—"
    texto = f"{abs(float(valor)):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"−{texto}" if float(valor) < 0 else texto


def _formatar(valor, unidade):
    if pd.isna(valor):
        return "—"
    if unidade == "moeda":
        mi = float(valor) / 1_000_000
        return f"R$ {_numero(mi / 1000)} bi" if abs(mi) >= 1000 else f"R$ {_numero(mi)} mi"
    if unidade == "percentual":
        return f"{_numero(valor * 100)}%"
    if unidade == "multiplo":
        return f"{_numero(valor)}x"
    return _numero(valor)


def _nome_cenario(valor):
    return f"Cenário {int(valor)}"


def _carregar_indicador(nome):
    fonte, coluna, _, _, _ = INDICADORES[nome]
    df = carregar_demonstrativo() if fonte == "demonstrativo" else carregar_indicadores()
    faltantes = {"Ano", "Cenario", coluna}.difference(df.columns)
    if faltantes:
        raise ValueError(f"Colunas ausentes na fonte de {nome}: {', '.join(sorted(faltantes))}")

    dados = df[["Ano", "Cenario", coluna]].copy()
    dados["Ano"] = pd.to_numeric(dados["Ano"], errors="coerce")
    dados["Cenario"] = pd.to_numeric(dados["Cenario"], errors="coerce")
    dados["Valor"] = pd.to_numeric(dados[coluna], errors="coerce")
    dados = dados.dropna(subset=["Ano", "Cenario", "Valor"])
    dados["Ano"] = dados["Ano"].astype(int)
    dados["Cenario"] = dados["Cenario"].astype(int)

    # Garante uma observação por cenário/ano caso existam duplicidades na fonte.
    return (dados.groupby(["Ano", "Cenario"], as_index=False)["Valor"]
            .mean().sort_values(["Ano", "Cenario"]))


def _resumo_anual(dados):
    return (dados.groupby("Ano")["Valor"].agg(
        Media="mean", Mediana="median",
        P10=lambda s: s.quantile(.10), P25=lambda s: s.quantile(.25),
        P75=lambda s: s.quantile(.75), P90=lambda s: s.quantile(.90),
        Minimo="min", Maximo="max", Cenarios="count"
    ).reset_index().sort_values("Ano"))


def _variacoes(resumo):
    df = resumo[["Ano", "Media"]].copy()
    anterior = df["Media"].shift(1)
    df["Variacao"] = df["Media"].pct_change()
    df.loc[anterior.abs() < 1e-12, "Variacao"] = np.nan
    return df


def _alertas(resumo, variacoes):
    alertas = []
    validas = variacoes.dropna()
    # Oscilação incomum: mediana +/- 3 MAD robustos, com piso de 10 p.p.
    if len(validas) >= 4:
        mediana = validas["Variacao"].median()
        mad = (validas["Variacao"] - mediana).abs().median()
        limite = max(3 * 1.4826 * mad, .10)
        for _, linha in validas.iterrows():
            if abs(linha["Variacao"] - mediana) > limite:
                alertas.append((
                    "warning",
                    "Oscilação fora do padrão histórico",
                    f"No Ano {int(linha['Ano'])}, a variação da média foi {linha['Variacao']:+.1%}, distante do comportamento habitual."
                ))

    # Dispersão relativa entre P10 e P90 comparada com o próprio histórico.
    temp = resumo.copy()
    temp["Dispersao"] = (temp["P90"] - temp["P10"]) / temp["Media"].abs().replace(0, np.nan)
    serie = temp["Dispersao"].replace([np.inf, -np.inf], np.nan).dropna()
    if len(serie) >= 4:
        q1, q3 = serie.quantile(.25), serie.quantile(.75)
        limite = q3 + 1.5 * (q3 - q1)
        for _, linha in temp.dropna(subset=["Dispersao"]).iterrows():
            if linha["Dispersao"] > limite:
                alertas.append((
                    "warning",
                    "Alta dispersão entre cenários",
                    f"No Ano {int(linha['Ano'])}, a faixa P10–P90 equivale a {linha['Dispersao']:.1%} da média, acima do padrão histórico."
                ))

    return alertas or [(
        "info", "Nenhum sinal estatístico relevante identificado",
        "Os critérios aplicados não identificaram oscilações ou dispersões incomuns no período selecionado."
    )]


def _grafico_evolucao(dados, resumo, cenario):
    destaque = dados.loc[dados["Cenario"] == cenario, ["Ano", "Valor"]].copy()
    destaque["Série"] = "Cenário selecionado"
    media = resumo[["Ano", "Media"]].rename(columns={"Media": "Valor"}).copy()
    media["Série"] = "Média dos cenários"
    linhas = pd.concat([destaque, media], ignore_index=True)

    faixa = alt.Chart(resumo).mark_area(color="#8CBCE5", opacity=.25).encode(
        x=alt.X("Ano:O", title="Ano"),
        y=alt.Y("P10:Q", title="Valor"),
        y2="P90:Q",
        tooltip=["Ano:O", alt.Tooltip("P10:Q", format=",.2f"), alt.Tooltip("P90:Q", format=",.2f")]
    )
    linha = alt.Chart(linhas).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("Ano:O", title="Ano"),
        y=alt.Y("Valor:Q", title="Valor", axis=alt.Axis(format=",.2f")),
        color=alt.Color("Série:N", scale=alt.Scale(
            domain=["Cenário selecionado", "Média dos cenários"],
            range=["#1680DB", "#329879"]
        )),
        tooltip=["Ano:O", "Série:N", alt.Tooltip("Valor:Q", format=",.2f")]
    )
    return (faixa + linha).properties(height=300).configure_view(strokeWidth=0).configure_axis(
        gridColor="#EDF2F7", labelColor="#55799F", titleColor="#55799F"
    )


def _grafico_variacao(variacoes):
    dados = variacoes.dropna(subset=["Variacao"]).copy()
    if dados.empty:
        return None
    dados["Sinal"] = np.where(dados["Variacao"] >= 0, "Positiva", "Negativa")
    return alt.Chart(dados).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("Ano:O", title="Ano"),
        y=alt.Y("Variacao:Q", title="Variação anual", axis=alt.Axis(format=".0%")),
        color=alt.Color("Sinal:N", scale=alt.Scale(
            domain=["Positiva", "Negativa"], range=["#329879", "#D97757"]
        ), legend=None),
        tooltip=["Ano:O", alt.Tooltip("Variacao:Q", title="Variação", format=".2%")]
    ).properties(height=260).configure_view(strokeWidth=0).configure_axis(gridColor="#EDF2F7")


def _grafico_boxplot(dados, ano):
    recorte = dados[dados["Ano"] == ano]
    if recorte.empty:
        return None
    return alt.Chart(recorte).mark_boxplot(extent=1.5, size=55).encode(
        x=alt.X("Ano:O", title=None),
        y=alt.Y("Valor:Q", title="Valor", scale=alt.Scale(zero=False)),
        tooltip=["Cenario:Q", alt.Tooltip("Valor:Q", format=",.2f")]
    ).properties(height=260).configure_view(strokeWidth=0).configure_axis(gridColor="#EDF2F7")


def _kpi(coluna, titulo, valor, nota):
    with coluna:
        st.markdown(
            f'<div class="tend-kpi-label">{titulo}</div>'
            f'<div class="tend-kpi-value">{valor}</div>'
            f'<div class="tend-kpi-note">{nota}</div>',
            unsafe_allow_html=True
        )


def render_tendencias():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="tend_page"):
        st.markdown(
            '<div class="tend-eyebrow">PAINEL FINANCEIRO</div>'
            '<div class="tend-title">Tendências</div>'
            '<div class="tend-subtitle">Acompanhe a evolução histórica, a distribuição dos cenários e os principais sinais de atenção.</div>',
            unsafe_allow_html=True
        )

        nomes = list(INDICADORES)
        f1, f2, f3, f4 = st.columns([1, 1.2, 1.35, 1.35], gap="medium")
        with f1:
            indicador = st.selectbox("Indicador principal", nomes, index=1, key="tend_indicador")
        with f2:
            secundarias = ["Nenhum"] + [n for n in nomes if n != indicador]
            secundario = st.selectbox("Indicador secundário", secundarias, key="tend_secundario")

        try:
            dados = _carregar_indicador(indicador)
        except Exception as erro:
            st.error(f"Não foi possível carregar {indicador}: {erro}")
            return

        if dados.empty:
            st.warning(f"Não existem valores válidos para {indicador}.")
            return

        anos = sorted(dados["Ano"].unique().tolist())
        cenarios = sorted(dados["Cenario"].unique().tolist())
        with f3:
            periodo = st.select_slider(
                "Período analisado", options=anos, value=(anos[0], anos[-1]),
                format_func=lambda ano: f"Ano {ano}", key="tend_periodo"
            )
        with f4:
            cenario = st.selectbox(
                "Destacar cenário", cenarios,
                format_func=lambda c: f"Cenário {c}", key="tend_cenario"
            )

        dados = dados[dados["Ano"].between(periodo[0], periodo[1])].copy()
        if dados.empty:
            st.info("Não há dados no período selecionado.")
            return

        resumo = _resumo_anual(dados)
        variacoes = _variacoes(resumo)
        _, _, _, unidade, direcao = INDICADORES[indicador]

        with st.container(key="tend_evolucao"):
            st.markdown('<div class="tend-card-title">Evolução histórica e faixa dos cenários</div>', unsafe_allow_html=True)
            st.markdown('<div class="tend-card-note">A linha destaca o cenário escolhido; a média resume os cenários disponíveis e a faixa mostra os percentis 10 a 90.</div>', unsafe_allow_html=True)
            st.altair_chart(_grafico_evolucao(dados, resumo, cenario), use_container_width=True)

        col_var, col_dist = st.columns(2, gap="medium")
        with col_var:
            with st.container(key="tend_variacao"):
                st.markdown('<div class="tend-card-title">Variação anual</div>', unsafe_allow_html=True)
                st.markdown('<div class="tend-card-note">Variação percentual da média dos cenários em relação ao ano anterior.</div>', unsafe_allow_html=True)
                graf = _grafico_variacao(variacoes)
                if graf is None:
                    st.info("Não há anos consecutivos suficientes para calcular a variação.")
                else:
                    st.altair_chart(graf, use_container_width=True)

        with col_dist:
            with st.container(key="tend_distribuicao"):
                st.markdown('<div class="tend-card-title">Distribuição dos cenários</div>', unsafe_allow_html=True)
                st.markdown('<div class="tend-card-note">Boxplot do indicador no ano selecionado; pontos externos representam possíveis outliers.</div>', unsafe_allow_html=True)
                ano_dist = st.selectbox(
                    "Ano da distribuição", sorted(dados["Ano"].unique()),
                    index=len(sorted(dados["Ano"].unique())) - 1,
                    format_func=lambda a: f"Ano {a}", key="tend_ano_dist"
                )
                boxplot = _grafico_boxplot(dados, ano_dist)
                if boxplot is None:
                    st.info("Não há dados para este ano.")
                else:
                    st.altair_chart(boxplot, use_container_width=True)
                quantidade = dados.loc[dados["Ano"] == ano_dist, "Valor"].count()
                st.caption(f"{quantidade:,} cenários com dados válidos.".replace(",", "."))

        with st.container(key="tend_alertas"):
            st.markdown('<div class="tend-card-title">Alertas automáticos</div>', unsafe_allow_html=True)
            st.markdown('<div class="tend-card-note">Sinais estatísticos do período selecionado. Não são previsões.</div>', unsafe_allow_html=True)
            for tipo, titulo, texto in _alertas(resumo, variacoes)[:6]:
                st.markdown(
                    f'<div class="tend-alert {tipo}"><div class="tend-alert-title">{titulo}</div>'
                    f'<div class="tend-alert-text">{texto}</div></div>',
                    unsafe_allow_html=True
                )

        # Resumo da média anual. CAGR somente quando os extremos são positivos.
        validos = resumo.dropna(subset=["Media"])
        cagr = np.nan
        if len(validos) >= 2:
            inicial, final = validos.iloc[0]["Media"], validos.iloc[-1]["Media"]
            if inicial > 0 and final > 0:
                cagr = (final / inicial) ** (1 / (len(validos) - 1)) - 1

        vv = variacoes.dropna(subset=["Variacao"])
        if not vv.empty:
            maior = vv.loc[vv["Variacao"].abs().idxmax()]
            melhor = vv.loc[vv["Variacao"].idxmax()]
            pior = vv.loc[vv["Variacao"].idxmin()]
            if direcao == "menor":
                melhor, pior = pior, melhor
            maior_txt = f"{maior['Variacao']:+.1%} · Ano {int(maior['Ano'])}"
            melhor_txt, pior_txt = f"Ano {int(melhor['Ano'])}", f"Ano {int(pior['Ano'])}"
        else:
            maior_txt = melhor_txt = pior_txt = "—"

        st.markdown('<div class="tend-card-title">Resumo da evolução</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4, gap="medium")
        _kpi(k1, "Crescimento médio anual (CAGR)", f"{cagr:+.1%}" if pd.notna(cagr) else "N/A", "Não aplicável se os valores inicial/final não forem positivos.")
        _kpi(k2, "Maior variação anual", maior_txt, "Maior oscilação percentual observada.")
        _kpi(k3, "Melhor ano", melhor_txt, "Considera a direção financeira do indicador.")
        _kpi(k4, "Pior ano", pior_txt, "Considera a direção financeira do indicador.")

        if secundario != "Nenhum":
            try:
                sec = _carregar_indicador(secundario)
                sec = sec[sec["Ano"].between(periodo[0], periodo[1])]
                sec_resumo = _resumo_anual(sec)
                comparacao = resumo[["Ano", "Media"]].rename(columns={"Media": indicador}).merge(
                    sec_resumo[["Ano", "Media"]].rename(columns={"Media": secundario}),
                    on="Ano", how="inner"
                ).melt(id_vars="Ano", var_name="Indicador", value_name="Média")
                if not comparacao.empty:
                    st.markdown(f"**Comparação de médias anuais: {indicador} e {secundario}**")
                    st.caption("Cada indicador mantém sua unidade original; compare principalmente a direção das tendências.")
                    graf_sec = alt.Chart(comparacao).mark_line(point=True).encode(
                        x=alt.X("Ano:O", title="Ano"),
                        y=alt.Y("Média:Q", title="Média anual", axis=alt.Axis(format=",.2f")),
                        color=alt.Color("Indicador:N", title="Indicador"),
                        tooltip=["Ano", "Indicador", alt.Tooltip("Média:Q", format=",.2f")]
                    ).properties(height=230).configure_view(strokeWidth=0)
                    st.altair_chart(graf_sec, use_container_width=True)
            except Exception as erro:
                st.warning(f"Não foi possível carregar o indicador secundário: {erro}")

        with st.container(key="tend_ajuda"):
            with st.expander("Como interpretar esta tela"):
                st.markdown(
                    "- **Média dos cenários:** média dos valores válidos de cada ano.\n"
                    "- **Faixa P10–P90:** intervalo que contém os 80% centrais da distribuição.\n"
                    "- **Boxplot:** apresenta mediana, quartis e possíveis valores atípicos pelo critério de 1,5 × IQR.\n"
                    "- **Variação anual:** mudança percentual da média em relação ao ano anterior. Não é calculada quando a média anterior é zero.\n"
                    "- **Alertas:** destacam oscilações e dispersões incomuns em relação ao histórico; são sinais para investigação, não previsões nem provas de causa."
                )
