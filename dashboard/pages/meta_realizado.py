
import streamlit as st
import pandas as pd
import numpy as np

from data.load_data import carregar_demonstrativo


# =========================================================
# CONFIGURAÇÕES
# =========================================================

INDICADORES_PREFERIDOS = [
    "Receita",
    "EBITDA",
    "Resultado Líquido",
    "Geração de Caixa",
    "Margem EBITDA",
]

INDICADORES_EXCLUIR = {
    "ano",
    "cenario",
    "cenário",
    "id",
    "codigo",
    "código",
}

def formatar_valor(valor):
    if pd.isna(valor):
        return "—"

    valor = float(valor)

    if abs(valor) >= 1_000_000:
        return f"R$ {valor / 1_000_000:,.2f} mi".replace(",", "X").replace(".", ",").replace("X", ".")

    if abs(valor) >= 1_000:
        return f"R$ {valor / 1_000:,.1f} mil".replace(",", "X").replace(".", ",").replace("X", ".")

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def nome_coluna(nome):
    return str(nome).strip().lower()


def identificar_colunas(df):
    colunas = []

    for coluna in df.columns:
        nome = nome_coluna(coluna)

        if nome in INDICADORES_EXCLUIR:
            continue

        if pd.api.types.is_numeric_dtype(df[coluna]):
            if df[coluna].nunique(dropna=True) > 1:
                colunas.append(coluna)

    return colunas


def formatar_percentual(valor):
    if pd.isna(valor):
        return "—"
    return f"{valor:.0f}%"


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

def render_meta_realizado():

    st.markdown("""
    <style>
    .meta-card {
        background: white;
        border: 1px solid #E5EAF2;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .meta-subtitle {
        color: #718096;
        font-size: 13px;
    }

    .meta-title {
        color: #17365D;
        font-size: 23px;
        font-weight: 700;
    }

    .status-atingida {
        color: #16834A;
        background: #E5F7EC;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: 600;
    }

    .status-atencao {
        color: #A66B00;
        background: #FFF3D6;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: 600;
    }

    .status-critica {
        color: #C0392B;
        background: #FDE8E7;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: 600;
    }

    div[data-testid="stProgressBar"] > div > div {
        background-color: #2463A6;
    }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # CARREGAMENTO
    # -----------------------------------------------------

    try:
        df = carregar_demonstrativo()
    except Exception as erro:
        st.error(f"Não foi possível carregar a base: {erro}")
        return

    if df is None or df.empty:
        st.warning("Não existem dados disponíveis na base.")
        return

    df = df.copy()

    # -----------------------------------------------------
    # IDENTIFICAÇÃO DAS COLUNAS
    # -----------------------------------------------------

    coluna_ano = next(
        (c for c in df.columns if nome_coluna(c) in ["ano", "exercicio", "exercício"]),
        None
    )

    coluna_cenario = next(
        (c for c in df.columns if nome_coluna(c) in ["cenario", "cenário"]),
        None
    )

    if coluna_ano is None or coluna_cenario is None:
        st.error("A base precisa conter as colunas Ano e Cenario.")
        return

    indicadores = identificar_colunas(df)

    if not indicadores:
        st.warning("Não foram encontrados indicadores numéricos para análise.")
        return

    # -----------------------------------------------------
    # CABEÇALHO
    # -----------------------------------------------------

    st.caption("PAINEL FINANCEIRO")
    st.markdown(
        '<div class="meta-title">Meta x Realizado</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="meta-subtitle">Explore dados, cenários e recomendações para apoiar decisões.</div>',
        unsafe_allow_html=True
    )

    st.write("")

    # -----------------------------------------------------
    # FILTROS
    # -----------------------------------------------------

    col1, col2, col3 = st.columns([1, 1.5, 1.3])

    anos = sorted(df[coluna_ano].dropna().unique(), reverse=True)

    with col1:
        ano = st.selectbox("Ano", anos)

    df_ano = df[df[coluna_ano] == ano].copy()

    cenarios = sorted(
        df_ano[coluna_cenario].dropna().unique(),
        key=lambda x: str(x)
    )

    with col2:
        cenario = st.selectbox("Cenário", cenarios)

    with col3:
        percentil = st.selectbox(
            "Percentil da meta",
            [50, 60, 75, 90],
            index=2,
            format_func=lambda x: f"Percentil {x}"
        )

    st.markdown("---")

    # -----------------------------------------------------
    # CONFIGURAÇÃO DA META
    # -----------------------------------------------------

    st.markdown("### Como a meta foi definida")

    st.info(
        f"A meta analítica corresponde ao percentil {percentil} "
        f"dos valores dos cenários disponíveis para cada indicador no ano de {ano}."
    )

    # -----------------------------------------------------
    # CÁLCULOS
    # -----------------------------------------------------

    df_cenario = df_ano[
        df_ano[coluna_cenario] == cenario
    ]

    if df_cenario.empty:
        st.warning("Não existem dados para o cenário selecionado.")
        return

    resultados = []

    for indicador in indicadores:

        valores = pd.to_numeric(
            df_ano[indicador],
            errors="coerce"
        ).dropna()

        realizado = pd.to_numeric(
            df_cenario[indicador],
            errors="coerce"
        ).dropna()

        if valores.empty or realizado.empty:
            continue

        meta = valores.quantile(percentil / 100)
        valor_realizado = realizado.mean()

        # Indicadores em que valores menores são melhores
        nome = nome_coluna(indicador)

        menor_melhor = any(
            palavra in nome
            for palavra in ["custo", "despesa", "divida", "dívida", "endividamento"]
        )

        if meta == 0:
            atingimento = np.nan
        elif menor_melhor:
            atingimento = (meta / valor_realizado) * 100 if valor_realizado != 0 else np.nan
        else:
            atingimento = (valor_realizado / meta) * 100

        if pd.isna(atingimento):
            status = "Indisponível"
        elif atingimento >= 100:
            status = "Atingida"
        elif atingimento >= 90:
            status = "Atenção"
        else:
            status = "Crítica"

        resultados.append({
            "Indicador": indicador,
            "Realizado": valor_realizado,
            "Meta analítica": meta,
            "% Atingimento": atingimento,
            "Status": status,
        })

    if not resultados:
        st.warning("Não foi possível calcular os indicadores deste cenário.")
        return

    resultado = pd.DataFrame(resultados)

    # -----------------------------------------------------
    # CARDS E TABELA
    # -----------------------------------------------------

    esquerda, direita = st.columns([1.7, 1])

    with esquerda:
        st.markdown("### Meta x Realizado")

        tabela = resultado.copy()

        tabela["Realizado"] = tabela["Realizado"].apply(formatar_valor)
        tabela["Meta analítica"] = tabela["Meta analítica"].apply(formatar_valor)
        tabela["% Atingimento"] = tabela["% Atingimento"].apply(formatar_percentual)

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True,
            height=300
        )

    with direita:
        st.markdown("### Atingimento")
        st.caption("Progresso por indicador")

        for _, linha in resultado.iterrows():

            indicador = linha["Indicador"]
            atingimento = linha["% Atingimento"]

            st.markdown(f"**{indicador}**")

            if pd.isna(atingimento):
                st.caption("Não foi possível calcular o atingimento.")
                continue

            progresso = max(0, min(atingimento / 100, 1))

            st.progress(progresso)

            if atingimento >= 100:
                st.markdown(
                    f'<span class="status-atingida">{atingimento:.0f}% · Atingida</span>',
                    unsafe_allow_html=True
                )
            elif atingimento >= 90:
                st.markdown(
                    f'<span class="status-atencao">{atingimento:.0f}% · Atenção</span>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<span class="status-critica">{atingimento:.0f}% · Crítica</span>',
                    unsafe_allow_html=True
                )

            st.write("")

    # -----------------------------------------------------
    # RESUMO
    # -----------------------------------------------------

    st.markdown("---")
    st.markdown("### Resumo da análise")

    total = len(resultado)
    atingidas = (resultado["Status"] == "Atingida").sum()
    atencao = (resultado["Status"] == "Atenção").sum()
    criticas = (resultado["Status"] == "Crítica").sum()

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Indicadores analisados", total)
    k2.metric("Metas atingidas", int(atingidas))
    k3.metric("Em atenção", int(atencao))
    k4.metric("Críticas", int(criticas))

    st.caption(
        "Nota: esta é uma meta analítica calculada a partir da distribuição "
        "dos cenários disponíveis. Ela não representa uma meta orçamentária "
        "aprovada nem um resultado contábil realizado, a menos que a base "
        "contenha dados reais identificados dessa forma."
    )