from pathlib import Path

import pandas as pd

import streamlit as st

import plotly.express as px

import plotly.graph_objects as go
from html import escape

from components.como_interpretar import como_interpretar
from data.load_data import carregar_indicadores

from components.auth import usuario_logado


PAGE_STYLE = """

<style>


.st-key-vg_page {

    padding: 22px 26px 32px;

    gap: 20px !important;

}


.vg-eyebrow {
    color: #1677E8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.1px;
    margin-bottom: 8px;
}

.vg-title {

    font-size: clamp(25px, 2vw, 32px);

    font-weight: 750;

    color: var(--cti-text);

    line-height: 1.2;

    letter-spacing: -0.6px;

}

.vg-subtitle {

    font-size: 13px;

    color: var(--cti-muted);

    margin-top: 7px;

    line-height: 1.6;

}


.vg-section-title {

    font-size: 16px;

    font-weight: 700;

    color: var(--cti-text);

    margin: 10px 0 2px;

}


[class*="st-key-vg_kpi_"],

.st-key-vg_grafico_ebitda,

.st-key-vg_grafico_margens,

.st-key-vg_qualidade {

    background: #FFFFFF;

    border: 1px solid #E5ECF4;

    border-radius: 16px;

    box-shadow: 0 4px 16px rgba(22, 55, 90, 0.045);

    padding: 18px;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;

}

[class*="st-key-vg_kpi_"] {
    min-height: 142px;
    height: 142px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
}


[class*="st-key-vg_kpi_"]:hover,

.st-key-vg_grafico_ebitda:hover,

.st-key-vg_grafico_margens:hover {

    border-color: #C6DDF5;

    box-shadow: 0 7px 22px rgba(22, 55, 90, 0.08);

}


.vg-kpi-label {
    font-size: 12px;
    font-weight: 650;
    color: #718096;
    margin-bottom: 10px;
    cursor: help;
    width: fit-content;
    border-bottom: 1px dotted #9BAFC5;
}


.vg-kpi-value {

    font-size: clamp(17px, 1.5vw, 25px);

    font-weight: 750;

    color: #17365D;

    line-height: 1.35;

    overflow-wrap: anywhere;

    font-variant-numeric: tabular-nums;

}


.vg-kpi-trend {
    font-size: 11px;
    font-weight: 700;
    line-height: 1.4;
    margin-top: 10px;
}
.vg-kpi-trend.positive { color: #16845B; }
.vg-kpi-trend.negative { color: #D14343; }
.vg-kpi-trend.neutral { color: #8493A7; }
.st-key-vg_nova_simulacao button {
    background: #12345A !important;
    color: #FFFFFF !important;
    border: 1px solid #12345A !important;
    border-radius: 10px !important;
    font-weight: 650 !important;
    min-height: 42px;
    white-space: nowrap;
}
.st-key-vg_nova_simulacao button:hover {
    background: #0B2542 !important;
    border-color: #0B2542 !important;
    color: #FFFFFF !important;
}


.vg-card-title {

    font-size: 16px;

    font-weight: 700;

    color: #17365D;

}

.vg-card-note {

    font-size: 12px;

    color: #8493A7;

    margin: 5px 0 12px;

    line-height: 1.5;

}

.vg-insight-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFE 100%);
    border: 1px solid #E5ECF4;
    border-radius: 14px;
    padding: 15px 16px;
    min-height: 112px;
}
.vg-insight-label {
    color: #718096;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .3px;
    margin-bottom: 8px;
}
.vg-insight-value {
    color: #17365D;
    font-size: 17px;
    line-height: 1.35;
    font-weight: 750;
}
.vg-insight-note {
    color: #8493A7;
    font-size: 11px;
    line-height: 1.45;
    margin-top: 6px;
}
.vg-chart-wrap {
    background: #FFFFFF;
    border: 1px solid #E5ECF4;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 16px rgba(22, 55, 90, 0.045);
}

    .vg-metodologia {

        font-size: 11.5px;

        color: #8AA4BF;

        line-height: 1.5;

        margin-top: 4px;

    }

</style>

"""


def formatar_moeda(valor):
    if pd.isna(valor):
        return "N/D"

    valor = float(valor)
    absoluto = abs(valor)
    sinal = "−" if valor < 0 else ""

    if absoluto >= 1_000_000_000:
        numero, unidade = absoluto / 1_000_000_000, " bi"
    elif absoluto >= 1_000_000:
        numero, unidade = absoluto / 1_000_000, " mi"
    elif absoluto >= 1_000:
        numero, unidade = absoluto / 1_000, " mil"
    else:
        numero, unidade = absoluto, ""

    texto = (
        f"{numero:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"{sinal}R$ {texto}{unidade}"


def formatar_dias(valor):
    if pd.isna(valor):
        return "N/D"

    return (
        f"{float(valor):,.1f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
        + " dias"
    )


def _escala_moeda(valores):
    maximo = pd.Series(valores).abs().max()

    if pd.isna(maximo):
        return 1, "R$"

    if maximo >= 1_000_000_000:
        return 1_000_000_000, "R$ bi"

    if maximo >= 1_000_000:
        return 1_000_000, "R$ mi"

    if maximo >= 1_000:
        return 1_000, "R$ mil"

    return 1, "R$"


def _grafico_evolucao(historico, colunas, cores, tipo, chave, titulo, nota):
    with st.container(key=chave):
        _titulo_cartao(titulo, nota)

        existentes = [c for c in colunas if c in historico.columns]

        if not existentes:
            st.info("A base não contém os indicadores necessários para este gráfico.")
            return

        serie = (
            historico.groupby("Ano_Numero")[existentes]
            .mean()
            .sort_index()
            .dropna(how="all")
        )

        if serie.empty:
            st.info("Não há dados suficientes para montar a evolução.")
            return

        if tipo == "moeda":
            divisor, unidade = _escala_moeda(serie.values.ravel())
            serie = serie / divisor
            rotulo, sufixo = unidade, f" {unidade}"
        elif tipo == "percentual":
            serie = serie * 100
            rotulo, sufixo = "%", "%"
        elif tipo == "dias":
            rotulo, sufixo = "dias", " dias"
        else:
            rotulo, sufixo = "vezes", "x"

        fig = px.line(
            serie.reset_index(),
            x="Ano_Numero",
            y=existentes,
            color_discrete_sequence=cores[:len(existentes)],
            markers=True,
            template="plotly_white",
            labels={"Ano_Numero": "Ano", "value": rotulo, "variable": "Indicador"},
        )

        fig.update_layout(
            separators=",.",
            height=320,
            margin=dict(l=8, r=8, t=18, b=8),
            hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Arial", color="#52647A", size=11),
            xaxis=dict(showgrid=False, dtick=1),
            yaxis=dict(title=rotulo, gridcolor="#EAF0F6", tickformat=",.1f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=6),
            hovertemplate="Ano %{x}<br>%{fullData.name}: %{y:,.2f}" + sufixo + "<extra></extra>",
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})


def formatar_percentual(valor):

    if pd.isna(valor):

        return "N/D"

    return f"{valor:.2%}".replace(".", ",")

def formatar_numero(valor):

    if pd.isna(valor):

        return "N/D"

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------- Cálculos (usados pela tela e pelo relatório em PDF) ----------

TODOS_OS_CENARIOS = "Todos os cenários"


def mapa_cenarios(df):
    """Nome original do cenário na base -> nome exibido ("Cenário 1", ...)."""
    cenarios = sorted(df["Cenario"].dropna().astype(str).unique().tolist())
    return {original: f"Cenário {i + 1}" for i, original in enumerate(cenarios)}


def dados_do_recorte(df, ano, cenario):
    """Linhas do ano e do cenário (nome original) escolhidos."""
    dados = df[df["Ano_Numero"] == ano]
    if cenario != TODOS_OS_CENARIOS:
        dados = dados[dados["Cenario"].astype(str) == cenario]
    return dados


def valor_indicador(df, ano, cenario, coluna):
    """Média dos cenários (ou o valor do cenário escolhido) no ano."""
    dados = dados_do_recorte(df, ano, cenario)

    if coluna not in dados.columns:
        return float("nan")

    valores = pd.to_numeric(dados[coluna], errors="coerce").dropna()

    if valores.empty:
        return float("nan")

    if cenario == TODOS_OS_CENARIOS:
        return valores.mean()

    return valores.iloc[0]


def variacao_anual(df, ano, cenario, coluna, formato="numero"):
    """Comparação com o ano anterior: {"classe": ..., "texto": ...}."""
    anos = sorted(df["Ano_Numero"].dropna().unique().astype(int).tolist())
    anos_anteriores = [a for a in anos if a < ano]
    if not anos_anteriores or coluna not in df.columns:
        return {"classe": "neutral", "texto": "— sem ano anterior"}

    atual = valor_indicador(df, ano, cenario, coluna)
    anterior = valor_indicador(df, max(anos_anteriores), cenario, coluna)

    if pd.isna(atual) or pd.isna(anterior):
        return {"classe": "neutral", "texto": "— dados insuficientes para comparar"}
    diferenca = float(atual) - float(anterior)
    if formato == "percentual":
        # a vírgula decimal só no número, para não virar "p,p,"
        numero = f"{abs(diferenca) * 100:.2f}".replace(".", ",") + " p.p."
    elif abs(float(anterior)) > 1e-12:
        percentual = abs(diferenca / abs(float(anterior))) * 100
        numero = f"{percentual:.1f}%".replace(".", ",")
    elif formato == "moeda":
        numero = formatar_moeda(abs(diferenca))
    else:
        numero = f"{abs(diferenca):.2f}".replace(".", ",")
    sufixo = " vs. ano anterior"

    if abs(diferenca) < 1e-12:
        return {"classe": "neutral", "texto": "• Estável vs. ano anterior"}
    subiu = diferenca > 0
    seta = "↑" if subiu else "↓"

    classe = "positive" if subiu else "negative"
    return {"classe": classe, "texto": f"{seta} {numero}{sufixo}"}


def ultimo_ano_disponivel(df, coluna):
    if coluna not in df.columns:
        return None

    validos = df.loc[df[coluna].notna(), "Ano_Numero"]
    return int(validos.max()) if not validos.empty else None


def avisos_de_qualidade(df, ano, cenario):
    """Indicadores sem valor no recorte e alertas sobre os dados."""
    indicadores_com_ano = ["ROIC", "EVA", "Capital Investido", "MVA Aproximado"]
    ausentes = []

    for coluna in indicadores_com_ano:
        if coluna in df.columns and pd.isna(valor_indicador(df, ano, cenario, coluna)):
            ultimo = ultimo_ano_disponivel(df, coluna)
            if ultimo is None:
                ausentes.append(f"{coluna}: sem valores disponíveis na base.")
            else:
                ausentes.append(
                    f"{coluna}: sem valor no Ano {ano}; "
                    f"último ano disponível na base: Ano {ultimo}."
                )

    margem_acima_de_100 = False
    margem_ebitda = valor_indicador(df, ano, cenario, "Margem EBITDA")
    if pd.notna(margem_ebitda) and margem_ebitda > 1:
        margem_acima_de_100 = True

    return ausentes, margem_acima_de_100


def _kpi(key, rotulo, valor, variacao, explicacao):
    valor = valor.replace("R$ ", "R$&nbsp;")
    rotulo_seguro = escape(rotulo)
    explicacao_segura = escape(explicacao, quote=True)
    with st.container(key=key):
        st.markdown(
            f'<div class="vg-kpi-label" title="{explicacao_segura}">{rotulo_seguro} ⓘ</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="vg-kpi-value">{valor}</div>', unsafe_allow_html=True)
        classe = variacao.get("classe", "neutral")
        texto = variacao.get("texto", "Sem comparação anual")
        st.markdown(
            f'<div class="vg-kpi-trend {classe}">{escape(texto)}</div>',
            unsafe_allow_html=True,
        )

def _titulo_secao(texto):

    st.markdown(f'<div class="vg-section-title">{texto}</div>', unsafe_allow_html=True)

def _titulo_cartao(titulo, nota=None):

    html = f'<div class="vg-card-title">{titulo}</div>'

    if nota:

        html += f'<div class="vg-card-note">{nota}</div>'

    st.markdown(html, unsafe_allow_html=True)


def render_visao_geral():

    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="vg_page"):

        _render_conteudo()

def _render_conteudo():

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
    cenarios = sorted(df["Cenario"].dropna().astype(str).unique().tolist())


    nomes_cenarios = mapa_cenarios(df)
    mapa_cenarios_inverso = {nome_exibicao: original for original, nome_exibicao in nomes_cenarios.items()}

    if not anos or not cenarios:
        st.warning("Não há anos ou cenários disponíveis para selecionar.")
        return

    usuario = usuario_logado() or {}
    nome = str(usuario.get("nome") or "").strip()
    primeiro_nome = escape(nome.split()[0]) if nome else ""
    saudacao = f"Olá, {primeiro_nome}! 👋" if primeiro_nome else "Olá! 👋"


    opcoes_cenario = ["Todos os cenários"] + list(nomes_cenarios.values())
    indice_cenario = 0

    with st.container(key="vg_topo"):
        titulo, filtro_ano, filtro_cenario, botao = st.columns(
            [2.6, 1, 1.2, 1], vertical_alignment="bottom"
        )

        with titulo:
            st.markdown(
                f"""
                <div class="vg-eyebrow">PAINEL FINANCEIRO</div>
                <div class="vg-title">{saudacao}</div>
                <div class="vg-subtitle">
                    Acompanhe os principais números e a saúde financeira do negócio.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with filtro_ano:
            ano = st.selectbox(
                "Ano",
                options=anos,
                index=len(anos) - 1,
                format_func=lambda a: str(a),
                key="vg_ano",
            )

        with filtro_cenario:
            cenario = st.selectbox(
                "Cenário",
                options=opcoes_cenario,
                index=indice_cenario,
                key="vg_cenario",
            )

        with botao:
            if st.button("＋  Nova simulação", key="vg_nova_simulacao", use_container_width=True):
                caminho_simulador = Path(__file__).resolve().parent / "simulador.py"
                if caminho_simulador.is_file():
                    st.switch_page("pages/simulador.py")
                else:
                    st.error(
                        "Não encontrei pages/simulador.py. Ajuste o caminho do botão "
                        "para o arquivo real da página de simulação."
                    )


    ano_selecionado = ano

    cenario_selecionado = mapa_cenarios_inverso.get(cenario, cenario)
    cenario_exibicao = cenario


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

        f"{escape(cenario_exibicao)} | {descricao_calculo}</div>",

        unsafe_allow_html=True,

    )


    # Os cálculos ficam em funções de módulo, compartilhadas com o relatório em PDF
    def obter_valor(coluna):
        return valor_indicador(df, ano_selecionado, cenario_selecionado, coluna)

    def obter_variacao_anual(coluna, explicacao, formato="numero", maior_eh_melhor=True):
        return variacao_anual(df, ano_selecionado, cenario_selecionado, coluna, formato)

    def obter_ultimo_ano_disponivel(coluna):
        return ultimo_ano_disponivel(df, coluna)


    _titulo_secao("Desempenho financeiro")

    cards_1 = st.columns(4)

    with cards_1[0]:

        _kpi(

            "vg_kpi_ebitda",

            "EBITDA médio",

            formatar_moeda(obter_valor("EBITDA")),
            obter_variacao_anual("EBITDA", "", "moeda"),
            "EBITDA: resultado operacional antes de juros, impostos, depreciação e amortização.",

        )

    with cards_1[1]:

        _kpi(

            "vg_kpi_margem_ebitda",

            "Margem EBITDA",

            formatar_percentual(obter_valor("Margem EBITDA")),
            obter_variacao_anual("Margem EBITDA", "", "percentual"),
            "Margem EBITDA: percentual da receita que resta após os custos e despesas operacionais considerados no cálculo do EBITDA.",

        )

    with cards_1[2]:

        _kpi(

            "vg_kpi_margem_liquida",

            "Margem Líquida",

            formatar_percentual(obter_valor("Margem Líquida")),
            obter_variacao_anual("Margem Líquida", "", "percentual"),
            "Margem líquida: parcela da receita que permanece como lucro líquido após despesas, resultado financeiro e impostos.",

        )

    with cards_1[3]:

        _kpi(

            "vg_kpi_nopat",

            "NOPAT",

            formatar_moeda(obter_valor("NOPAT")),
            obter_variacao_anual("NOPAT", "", "moeda"),
            "NOPAT: lucro operacional após impostos, antes dos efeitos do financiamento.",

        )


    _titulo_secao("Retorno, liquidez e custo de capital")

    cards_2 = st.columns(4)

    with cards_2[0]:

        _kpi(

            "vg_kpi_lc",

            "Liquidez Corrente (LC)",

            formatar_numero(obter_valor("LC")),
            obter_variacao_anual("LC", "", "numero"),
            "Liquidez corrente: relação entre ativos circulantes e passivos circulantes; indica a cobertura das obrigações de curto prazo.",

        )

    with cards_2[1]:

        _kpi(

            "vg_kpi_roic",

            "ROIC",

            formatar_percentual(obter_valor("ROIC")),
            obter_variacao_anual("ROIC", "", "percentual"),
            "ROIC: retorno sobre o capital investido; avalia o retorno operacional gerado pelo capital empregado no negócio.",

        )

    with cards_2[2]:

        _kpi(

            "vg_kpi_eva",

            "EVA",

            formatar_moeda(obter_valor("EVA")),
            obter_variacao_anual("EVA", "", "moeda"),
            "EVA: valor econômico agregado, que estima a riqueza gerada após considerar o custo do capital investido.",

        )

    with cards_2[3]:

        _kpi(

            "vg_kpi_wacc",

            "WACC",

            formatar_percentual(obter_valor("WACC")),
            obter_variacao_anual("WACC", "", "percentual"),
            "WACC: custo médio ponderado de capital; representa o custo médio das fontes de financiamento da empresa.",

        )

    _titulo_secao("Rentabilidade, caixa e capital de giro")

    cards_3 = st.columns(4)

    with cards_3[0]:
        _kpi(
            "vg_kpi_roe",
            "ROE",
            formatar_percentual(obter_valor("ROE")),
            obter_variacao_anual("ROE", "", "percentual"),
            "ROE: retorno sobre o patrimônio líquido médio; mostra quanto o lucro rende para o acionista.",
        )

    with cards_3[1]:
        _kpi(
            "vg_kpi_fco",
            "FCO",
            formatar_moeda(obter_valor("FCO")),
            obter_variacao_anual("FCO", "", "moeda"),
            "FCO: fluxo de caixa operacional estimado a partir da receita, da variação de clientes e dos pagamentos de custos, tributos e imposto de renda.",
        )

    with cards_3[2]:
        _kpi(
            "vg_kpi_fcl",
            "FCL",
            formatar_moeda(obter_valor("FCL")),
            obter_variacao_anual("FCL", "", "moeda"),
            "FCL: fluxo de caixa livre; é o FCO depois de descontar os investimentos.",
        )

    with cards_3[3]:
        _kpi(
            "vg_kpi_ciclo",
            "Ciclo Financeiro",
            formatar_dias(obter_valor("Ciclo Financeiro")),
            obter_variacao_anual("Ciclo Financeiro", "", "numero"),
            "Ciclo financeiro: prazo médio de recebimento menos prazo médio de pagamento, em dias.",
        )


    _titulo_secao("Leitura executiva")
    st.caption("Destaques calculados automaticamente para o período e cenário selecionados; são comparações descritivas, não metas nem previsões.")

    metricas_destaque = [
        ("EBITDA", "EBITDA", "moeda"),
        ("Margem EBITDA", "Margem EBITDA", "percentual"),
        ("ROIC", "ROIC", "percentual"),
        ("EVA", "EVA", "moeda"),
        ("FCL", "FCL", "moeda"),
    ]
    destaques = []
    for coluna, nome_indicador, formato in metricas_destaque:
        if coluna not in df.columns:
            continue
        atual = obter_valor(coluna)
        variacao = obter_variacao_anual(coluna, "", formato)
        if pd.isna(atual):
            valor_texto = "Sem dados"
            nota = "Não há valor disponível no recorte atual."
        else:
            valor_texto = formatar_percentual(atual) if formato == "percentual" else formatar_moeda(atual)
            nota = variacao.get("texto", "Sem comparação anual")
        destaques.append((nome_indicador, valor_texto, nota))

    if destaques:
        colunas_destaque = st.columns(len(destaques), gap="medium")
        for coluna_ui, (rotulo, valor_texto, nota) in zip(colunas_destaque, destaques):
            with coluna_ui:
                st.markdown(
                    '<div class="vg-insight-card">'
                    f'<div class="vg-insight-label">{escape(rotulo)}</div>'
                    f'<div class="vg-insight-value">{escape(valor_texto)}</div>'
                    f'<div class="vg-insight-note">{escape(nota)}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )


    _titulo_secao("Visão da base")
    anos_base = sorted(df["Ano_Numero"].dropna().astype(int).unique().tolist())
    cenarios_base = sorted(df["Cenario"].dropna().astype(str).unique().tolist())
    cobertura_cols = st.columns(3, gap="medium")
    with cobertura_cols[0]:
        st.metric("Anos disponíveis", len(anos_base))
    with cobertura_cols[1]:
        st.metric("Cenários disponíveis", len(cenarios_base))
    with cobertura_cols[2]:
        st.metric("Registros na base", f"{len(df):,}".replace(",", "."))


    historico_base = df.copy()
    if cenario_selecionado != "Todos os cenários":
        historico_base = historico_base[historico_base["Cenario"].astype(str) == cenario_selecionado]

    _titulo_secao("Evolução anual do desempenho")
    st.caption(
        "Compare como os indicadores mudaram ao longo dos anos. "
        "Com 'Todos os cenários', cada ponto representa a média dos valores disponíveis entre os cenários. "
        "Ao selecionar um cenário, o gráfico mostra apenas esse cenário."
    )
    col_ebitda_ano, col_margem_ano = st.columns(2, gap="medium")

    with col_ebitda_ano, st.container(key="vg_grafico_ebitda_anos"):
        _titulo_cartao("Evolução do EBITDA", "Resultado operacional por ano (R$).")
        if "EBITDA" in historico_base.columns:
            serie_ebitda = historico_base.groupby("Ano_Numero")["EBITDA"].mean().dropna().sort_index()
            if not serie_ebitda.empty:
                divisor_ebitda, unidade_ebitda = _escala_moeda(serie_ebitda.values)
                serie_ebitda = serie_ebitda / divisor_ebitda
                fig_ebitda_anos = px.line(
                    x=serie_ebitda.index.astype(int), y=serie_ebitda.values,
                    markers=True, template="plotly_white",
                    labels={"x": "Ano", "y": f"EBITDA ({unidade_ebitda})"},
                )
                fig_ebitda_anos.update_traces(
                    line=dict(color="#1677E8", width=3), marker=dict(size=7),
                    hovertemplate="Ano %{x}<br>EBITDA: %{y:,.2f} " + unidade_ebitda + "<extra></extra>",
                )
                fig_ebitda_anos.update_layout(
                    separators=",.", height=320, margin=dict(l=8, r=8, t=18, b=8),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Arial", color="#52647A", size=11),
                    xaxis=dict(title="Ano", showgrid=False, dtick=1),
                    yaxis=dict(title=f"EBITDA ({unidade_ebitda})", gridcolor="#EAF0F6", tickformat=",.1f"),
                )
                st.plotly_chart(fig_ebitda_anos, use_container_width=True, config={"displayModeBar": False, "responsive": True})
            else:
                st.info("Não há dados de EBITDA suficientes para comparar os anos.")
        else:
            st.info("A base não contém a coluna EBITDA.")

    with col_margem_ano, st.container(key="vg_grafico_margem_anos"):
        _titulo_cartao("Evolução da Margem EBITDA", "Percentual da receita que corresponde ao EBITDA.")
        if "Margem EBITDA" in historico_base.columns:
            serie_margem = historico_base.groupby("Ano_Numero")["Margem EBITDA"].mean().dropna().sort_index() * 100
            if not serie_margem.empty:
                fig_margem_anos = px.line(
                    x=serie_margem.index.astype(int), y=serie_margem.values,
                    markers=True, template="plotly_white",
                    labels={"x": "Ano", "y": "Margem EBITDA (%)"},
                )
                fig_margem_anos.update_traces(
                    line=dict(color="#58B99A", width=3), marker=dict(size=7),
                    hovertemplate="Ano %{x}<br>Margem EBITDA: %{y:.2f}%<extra></extra>",
                )
                fig_margem_anos.update_layout(
                    separators=",.", height=320, margin=dict(l=8, r=8, t=18, b=8),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Arial", color="#52647A", size=11),
                    xaxis=dict(title="Ano", showgrid=False, dtick=1),
                    yaxis=dict(title="Margem EBITDA (%)", gridcolor="#EAF0F6", ticksuffix="%"),
                )
                st.plotly_chart(fig_margem_anos, use_container_width=True, config={"displayModeBar": False, "responsive": True})
            else:
                st.info("Não há dados de Margem EBITDA suficientes para comparar os anos.")
        else:
            st.info("A base não contém a coluna Margem EBITDA.")


    _titulo_secao("Retorno e custo de capital ao longo do tempo")
    col_retorno, col_valor = st.columns(2, gap="medium")
    with col_retorno, st.container(key="vg_grafico_retorno"):
        _titulo_cartao("ROIC, ROE e WACC", "Retorno do capital, retorno do acionista e custo de financiamento, em %.")
        if all(c in historico_base.columns for c in ["ROIC", "WACC"]):
            colunas_retorno = [c for c in ["ROIC", "ROE", "WACC"] if c in historico_base.columns]
            retorno = historico_base.groupby("Ano_Numero")[colunas_retorno].mean().sort_index() * 100
            retorno = retorno.rename(columns={c: f"{c} (%)" for c in colunas_retorno}).dropna(how="all")
            if not retorno.empty:
                fig_retorno = px.line(retorno.reset_index(), x="Ano_Numero", y=list(retorno.columns), color_discrete_map={"ROIC (%)": "#1677E8", "ROE (%)": "#6D6AE8", "WACC (%)": "#E7A23B"}, markers=True, template="plotly_white", labels={"Ano_Numero":"Ano", "value":"Percentual", "variable":"Indicador"})
                fig_retorno.update_layout(separators=",.", height=320, margin=dict(l=8,r=8,t=18,b=8), hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial",color="#52647A",size=11), xaxis=dict(showgrid=False,dtick=1), yaxis=dict(gridcolor="#EAF0F6",ticksuffix="%"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
                fig_retorno.update_traces(line=dict(width=3), marker=dict(size=6), hovertemplate="Ano %{x}<br>%{fullData.name}: %{y:.2f}%<extra></extra>")
                st.plotly_chart(fig_retorno, use_container_width=True, config={"displayModeBar": False, "responsive": True})
            else:
                st.info("Não há dados suficientes de ROIC e WACC para montar a evolução.")
        else:
            st.info("A base não contém as colunas ROIC e WACC necessárias para este gráfico.")
    with col_valor, st.container(key="vg_grafico_eva_nopat"):
        _titulo_cartao("EVA e NOPAT", "Indicadores monetários para acompanhar resultado operacional após impostos e valor econômico agregado.")
        if all(c in historico_base.columns for c in ["EVA", "NOPAT"]):
            valores = historico_base.groupby("Ano_Numero")[["EVA", "NOPAT"]].mean().sort_index()
            valores = valores.rename(columns={"EVA": "EVA", "NOPAT": "NOPAT"}).dropna(how="all")
            if not valores.empty:
                divisor_valores, unidade_valores = _escala_moeda(valores.values.ravel())
                valores = valores / divisor_valores
                fig_valores = px.line(valores.reset_index(), x="Ano_Numero", y=["EVA", "NOPAT"], color_discrete_sequence=["#58B99A", "#6D6AE8"], markers=True, template="plotly_white", labels={"Ano_Numero":"Ano", "value":unidade_valores, "variable":"Indicador"})
                fig_valores.update_layout(separators=",.", height=320, margin=dict(l=8,r=8,t=18,b=8), hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial",color="#52647A",size=11), xaxis=dict(showgrid=False,dtick=1), yaxis=dict(title=unidade_valores,gridcolor="#EAF0F6",tickformat=",.1f"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
                fig_valores.update_traces(line=dict(width=3), marker=dict(size=6), hovertemplate="Ano %{x}<br>%{fullData.name}: %{y:,.2f} " + unidade_valores + "<extra></extra>")
                st.plotly_chart(fig_valores, use_container_width=True, config={"displayModeBar": False, "responsive": True})
            else:
                st.info("Não há dados suficientes de EVA e NOPAT para montar a evolução.")
        else:
            st.info("A base não contém as colunas EVA e NOPAT necessárias para este gráfico.")


    _titulo_secao("Caixa e capital de giro ao longo do tempo")

    col_caixa, col_giro = st.columns(2, gap="medium")

    with col_caixa:
        _grafico_evolucao(
            historico_base, ["FCO", "FCL"], ["#1677E8", "#58B99A"], "moeda",
            "vg_grafico_caixa", "FCO e FCL",
            "Caixa gerado pela operação e caixa livre depois dos investimentos.",
        )

    with col_giro:
        _grafico_evolucao(
            historico_base, ["PMR", "PMP", "Ciclo Financeiro"], ["#1677E8", "#E7A23B", "#C65B5B"], "dias",
            "vg_grafico_giro", "Prazos e ciclo financeiro",
            "Dias para receber (PMR), dias para pagar (PMP) e ciclo financeiro.",
        )

    col_conversao, col_cobertura = st.columns(2, gap="medium")

    with col_conversao:
        _grafico_evolucao(
            historico_base, ["FCO / EBITDA", "Taxa de Conversão da Receita em Caixa"], ["#58B99A", "#6D6AE8"], "percentual",
            "vg_grafico_conversao", "Conversão em caixa",
            "Quanto do EBITDA e da receita vira caixa, em %.",
        )

    with col_cobertura:
        _grafico_evolucao(
            historico_base, ["Cobertura de Juros", "Cobertura de Dividendos"], ["#1677E8", "#E7A23B"], "vezes",
            "vg_grafico_cobertura", "Coberturas",
            "Quantas vezes o caixa cobre os juros e a distribuição aos acionistas.",
        )

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

    como_interpretar(
        "vg",
        [
            "**Seta e variação:** comparam com o ano anterior. A cor indica só "
            "a direção da mudança, não se ela é boa ou ruim.",
            "**Rentabilidade, caixa e capital de giro:** ROE é o retorno ao "
            "acionista; FCO e FCL mostram o caixa gerado antes e depois dos "
            "investimentos; o ciclo financeiro mostra quantos dias o caixa fica "
            "preso entre pagar e receber.",
            "**Gráficos de evolução:** mostram a média dos cenários por ano ou o "
            "cenário escolhido. Linhas que começam no Ano 2 usam o ano anterior.",
            "**N/D:** indicadores que usam o ano anterior não existem no Ano 1.",
        ],
        "os valores vêm da planilha de indicadores e não são recalculados nesta "
        "tela. Dados ausentes não são preenchidos.",
    )