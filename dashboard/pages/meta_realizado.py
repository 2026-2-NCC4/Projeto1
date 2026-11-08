import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from components.como_interpretar import como_interpretar
from data.load_data import carregar_demonstrativo
from pages.regressao import VARIAVEIS

INDICADORES_PREFERIDOS = [
    "Receita",
    "EBITDA",
    "Resultado Líquido",
    "Geração de Caixa",
    "Margem EBITDA",
]

COLUNA_MARGEM = "Margem EBITDA"

CORES_STATUS = {
    "Atingida": "#258B68",
    "Atenção": "#E7A23B",
    "Crítica": "#C65B5B",
}

PAGE_STYLE = """
<style>
    .st-key-meta_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .meta-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .meta-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .meta-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .st-key-meta_filtros label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-meta_filtros,
    .st-key-meta_kpi_total,
    .st-key-meta_kpi_atingidas,
    .st-key-meta_kpi_atencao,
    .st-key-meta_kpi_criticas,
    .st-key-meta_tabela,
    .st-key-meta_grafico {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
        box-sizing: border-box;
    }

    .st-key-meta_tabela,
    .st-key-meta_grafico {
        height: 100%;
    }

    .meta-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
        margin-bottom: 4px;
    }

    .meta-card-note {
        font-size: 11px;
        color: #8AA4BF;
        margin-bottom: 12px;
    }

    .meta-kpi-label {
        font-size: 12px;
        color: var(--cti-muted);
    }

    .meta-kpi-value {
        font-size: 26px;
        font-weight: 700;
        line-height: 1.3;
    }
</style>
"""


def _numero_br(valor, casas=2):
    texto = f"{abs(float(valor)):,.{casas}f}".replace(",", "X")
    texto = texto.replace(".", ",").replace("X", ".")
    sinal = "−" if float(valor) < 0 else ""
    return f"{sinal}{texto}"


def formatar_valor(valor, indicador):
    if pd.isna(valor):
        return "—"

    if indicador == COLUNA_MARGEM:
        return f"{_numero_br(float(valor) * 100)}%"

    valor = float(valor)

    if abs(valor) >= 1_000_000_000:
        return f"R$ {_numero_br(valor / 1_000_000_000)} bi"

    if abs(valor) >= 1_000_000:
        return f"R$ {_numero_br(valor / 1_000_000)} mi"

    if abs(valor) >= 1_000:
        return f"R$ {_numero_br(valor / 1_000, 1)} mil"

    return f"R$ {_numero_br(valor)}"


def formatar_percentual(valor):
    if pd.isna(valor):
        return "—"

    return f"{_numero_br(valor, 0)}%"


def _classificar(atingimento):
    if pd.isna(atingimento):
        return "Indisponível"

    if atingimento >= 100:
        return "Atingida"

    if atingimento >= 90:
        return "Atenção"

    return "Crítica"


def _atingimento(realizado, meta):
    if pd.isna(realizado) or pd.isna(meta) or meta == 0:
        return np.nan

    return 100 + (realizado - meta) / abs(meta) * 100


def _preparar_base(df):
    df = df.copy()

    colunas_base = {
        nome: coluna
        for nome, coluna in VARIAVEIS.items()
        if coluna in df.columns
    }

    precisa = ["DRE - EBITDA", "DRE - Receita", "DRE - Tributos"]

    if all(coluna in df.columns for coluna in precisa):
        receita_liquida = df["DRE - Receita"] + df["DRE - Tributos"]
        df[COLUNA_MARGEM] = (
            df["DRE - EBITDA"]
            .div(receita_liquida.where(receita_liquida != 0))
        )
        colunas_base[COLUNA_MARGEM] = COLUNA_MARGEM

    return df, colunas_base


def indicadores_padrao(colunas_base):
    return [nome for nome in INDICADORES_PREFERIDOS if nome in colunas_base]


def calcular_metas(df_ano, cenario, percentil, escolhidos, colunas_base):
    """Realizado do cenário × meta (percentil dos cenários do ano), por indicador.

    Usado pela tela e pelo relatório em PDF. Devolve um DataFrame (vazio se
    nenhum indicador puder ser calculado).
    """
    df_cenario = df_ano[df_ano["Cenario"] == cenario]
    resultados = []

    for nome in escolhidos:
        coluna = colunas_base[nome]

        valores = pd.to_numeric(df_ano[coluna], errors="coerce").dropna()
        realizado = pd.to_numeric(df_cenario[coluna], errors="coerce").dropna()

        if valores.empty or realizado.empty:
            continue

        meta = valores.quantile(percentil / 100)
        valor_realizado = realizado.mean()
        atingimento = _atingimento(valor_realizado, meta)

        resultados.append({
            "Indicador": nome,
            "Realizado": valor_realizado,
            "Meta analítica": meta,
            "% Atingimento": atingimento,
            "Status": _classificar(atingimento),
        })

    return pd.DataFrame(resultados)


def _grafico_atingimento(resultado):
    dados = resultado.dropna(subset=["% Atingimento"]).copy()

    if dados.empty:
        st.info("Não há indicadores com atingimento calculável.")
        return

    escala = alt.Scale(
        domain=list(CORES_STATUS.keys()),
        range=list(CORES_STATUS.values()),
    )

    barras = (
        alt.Chart(dados)
        .mark_bar(cornerRadiusEnd=4, size=22)
        .encode(
            x=alt.X(
                "% Atingimento:Q",
                title="Atingimento da meta (%)",
                axis=alt.Axis(labelAngle=0, format=",.0f"),
            ),
            y=alt.Y("Indicador:N", sort="-x", title=None),
            color=alt.Color(
                "Status:N",
                scale=escala,
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("Indicador:N"),
                alt.Tooltip("% Atingimento:Q", title="Atingimento (%)", format=",.1f"),
                alt.Tooltip("Status:N"),
            ],
        )
    )

    regua = (
        alt.Chart(pd.DataFrame({"meta": [100]}))
        .mark_rule(color="#52677D", strokeDash=[4, 3])
        .encode(x="meta:Q")
    )

    st.altair_chart(
        (barras + regua).properties(height=max(220, 48 * len(dados))),
        use_container_width=True,
    )


def render_meta_realizado():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="meta_page"):
        try:
            df = carregar_demonstrativo()
        except Exception as erro:
            st.error(f"Não foi possível carregar a base: {erro}")
            return

        if df is None or df.empty:
            st.warning("Não existem dados disponíveis na base.")
            return

        if "Ano" not in df.columns or "Cenario" not in df.columns:
            st.error("A base precisa conter as colunas Ano e Cenario.")
            return

        df, colunas_base = _preparar_base(df)

        if not colunas_base:
            st.warning("Não foram encontrados indicadores para análise.")
            return

        st.markdown(
            """
            <div class="meta-eyebrow">PAINEL FINANCEIRO</div>
            <div class="meta-title">Metas x Realizado</div>
            <div class="meta-subtitle">
                Compare o resultado de um cenário com uma meta analítica
                calculada a partir de todos os cenários do mesmo ano.
            </div>
            """,
            unsafe_allow_html=True,
        )

        anos = sorted(df["Ano"].dropna().astype(int).unique().tolist())

        with st.container(key="meta_filtros"):
            col_ano, col_cenario, col_percentil = st.columns([1, 1.5, 1.3])

            with col_ano:
                ano = st.selectbox(
                    "Ano",
                    options=anos,
                    index=len(anos) - 1,
                    format_func=lambda valor: f"Ano {valor}",
                    key="meta_ano",
                )

            df_ano = df[df["Ano"] == ano].copy()

            cenarios = sorted(df_ano["Cenario"].dropna().astype(int).unique().tolist())

            with col_cenario:
                cenario = st.selectbox(
                    "Cenário",
                    options=cenarios,
                    format_func=lambda valor: f"Cenário {valor}",
                    key="meta_cenario",
                )

            with col_percentil:
                percentil = st.selectbox(
                    "Percentil da meta",
                    options=[50, 60, 75, 90],
                    index=2,
                    format_func=lambda valor: f"Percentil {valor}",
                    key="meta_percentil",
                )

            escolhidos = st.multiselect(
                "Indicadores analisados",
                options=list(colunas_base.keys()),
                default=indicadores_padrao(colunas_base),
                key="meta_indicadores",
            )

        if not escolhidos:
            st.info("Selecione pelo menos um indicador para a análise.")
            return

        if df_ano[df_ano["Cenario"] == cenario].empty:
            st.warning("Não existem dados para o cenário selecionado.")
            return

        resultado = calcular_metas(df_ano, cenario, percentil, escolhidos, colunas_base)

        if resultado.empty:
            st.warning("Não foi possível calcular os indicadores deste cenário.")
            return

        total = len(resultado)
        atingidas = int((resultado["Status"] == "Atingida").sum())
        atencao = int((resultado["Status"] == "Atenção").sum())
        criticas = int((resultado["Status"] == "Crítica").sum())

        kpis = [
            ("meta_kpi_total", "Indicadores analisados", total, "var(--cti-blue)"),
            ("meta_kpi_atingidas", "Metas atingidas", atingidas, CORES_STATUS["Atingida"]),
            ("meta_kpi_atencao", "Em atenção", atencao, CORES_STATUS["Atenção"]),
            ("meta_kpi_criticas", "Críticas", criticas, CORES_STATUS["Crítica"]),
        ]

        for coluna, (chave, rotulo, valor, cor) in zip(st.columns(4, gap="medium"), kpis):
            with coluna:
                with st.container(key=chave):
                    st.markdown(
                        f'<div class="meta-kpi-label">{rotulo}</div>'
                        f'<div class="meta-kpi-value" style="color:{cor}">{valor}</div>',
                        unsafe_allow_html=True,
                    )

        col_tabela, col_grafico = st.columns([1.35, 1], gap="medium")

        with col_tabela:
            with st.container(key="meta_tabela"):
                st.markdown(
                    '<div class="meta-card-title">Meta x Realizado</div>'
                    f'<div class="meta-card-note">Cenário {cenario} · Ano {ano} · '
                    f"meta = percentil {percentil} dos cenários do ano</div>",
                    unsafe_allow_html=True,
                )

                tabela = resultado.copy()
                tabela["Realizado"] = [
                    formatar_valor(valor, nome)
                    for valor, nome in zip(resultado["Realizado"], resultado["Indicador"])
                ]
                tabela["Meta analítica"] = [
                    formatar_valor(valor, nome)
                    for valor, nome in zip(resultado["Meta analítica"], resultado["Indicador"])
                ]
                tabela["% Atingimento"] = tabela["% Atingimento"].apply(formatar_percentual)

                st.dataframe(
                    tabela,
                    use_container_width=True,
                    hide_index=True,
                    height=min(460, 40 + 36 * len(tabela)),
                )

        with col_grafico:
            with st.container(key="meta_grafico"):
                st.markdown(
                    '<div class="meta-card-title">Atingimento por indicador</div>'
                    '<div class="meta-card-note">A linha tracejada marca 100% da meta.</div>',
                    unsafe_allow_html=True,
                )

                _grafico_atingimento(resultado)

        como_interpretar(
            "meta",
            [
                "**Meta analítica:** é o percentil escolhido dos valores de todos "
                "os cenários no mesmo ano. Não é uma meta orçamentária aprovada.",
                "**Realizado:** valor do cenário escolhido no ano.",
                "**% Atingimento:** 100% significa estar exatamente na meta; "
                "acima de 100%, o cenário está melhor que a meta; abaixo, pior.",
                "**Custos e despesas:** ficam na base como valores negativos. "
                "Quanto mais perto de zero, menor o custo e melhor o resultado.",
                "**Status:** Atingida a partir de 100%, Atenção de 90% a 99% e "
                "Crítica abaixo de 90%.",
                "**Margem EBITDA:** calculada como EBITDA dividido pela receita "
                "líquida (receita menos tributos).",
            ],
            "como a meta vem dos próprios cenários, no percentil 75 apenas "
            "cerca de 25% deles atingem 100% por construção. O status mostra a "
            "posição relativa do cenário, não um desempenho bom ou ruim em "
            "termos absolutos.",
        )