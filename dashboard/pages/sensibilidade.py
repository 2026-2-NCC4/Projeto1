import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from components.como_interpretar import como_interpretar
from data.load_data import carregar_demonstrativo
from pages.regressao import (
    FATORES,
    VARIAVEIS,
    RESULTADO,
    VARIACAO_IMPACTO,
    ajustar_ols,
    remover_colineares,
    _moeda_mi,
)


PAGE_STYLE = """
<style>
    .st-key-sens_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .sens-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .sens-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .sens-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
        line-height: 1.5;
    }

    .st-key-sens_topo label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-sens_card_grafico,
    .st-key-sens_card_tabela {
        background: #FFFFFF;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        height: 100%;
        box-sizing: border-box;
    }

    .sens-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
        margin-bottom: 4px;
    }

    .sens-card-note {
        font-size: 12px;
        color: var(--cti-muted);
        line-height: 1.5;
        margin-bottom: 14px;
    }

    .sens-note {
        background: #F4F8FC;
        border: 1px solid #E1ECF7;
        border-radius: 10px;
        padding: 13px 16px;
        color: #52677D;
        font-size: 12px;
        line-height: 1.6;
        margin-top: 16px;
    }

    .sens-kpi {
        background: #FFFFFF;
        border: 1px solid #E1ECF7;
        border-radius: 12px;
        padding: 14px 17px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .04);
    }

    .sens-kpi-label {
        color: var(--cti-muted);
        font-size: 11px;
        font-weight: 650;
    }

    .sens-kpi-value {
        color: var(--cti-blue);
        font-size: 23px;
        font-weight: 750;
        margin-top: 5px;
    }

    .sens-kpi-note {
        color: #8AA4BF;
        font-size: 11px;
        margin-top: 4px;
    }
</style>
"""


def _formatar_numero(valor, casas=2):
    if pd.isna(valor):
        return "—"

    return (
        f"{valor:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def _formatar_moeda(valor):
    if pd.isna(valor):
        return "—"

    return _moeda_mi(valor)


def _calcular_sensibilidade(df, ano):

    coluna_resultado = VARIAVEIS[RESULTADO]
    nomes = list(FATORES.keys())
    colunas_fatores = [VARIAVEIS[nome] for nome in nomes]

    colunas = ["Cenario", coluna_resultado, *colunas_fatores]

    dados = (
        df.loc[df["Ano"].eq(ano), colunas]
        .copy()
        .dropna()
    )

    if len(dados) <= len(nomes) + 1:
        return None, "Não há cenários suficientes com dados completos."

    y = dados[coluna_resultado].to_numpy(dtype=float) / 1_000_000
    X = dados[colunas_fatores].to_numpy(dtype=float) / 1_000_000

    mantidos, removidos = remover_colineares(X, nomes)

    if not mantidos:
        return None, "Não foi possível identificar fatores com variação suficiente."

    X_modelo = X[:, mantidos]

    try:
        modelo = ajustar_ols(y, X_modelo)
    except Exception as erro:
        return None, f"Não foi possível ajustar o modelo: {erro}"

    fatores = []

    for posicao_modelo, indice_original in enumerate(mantidos):
        nome = nomes[indice_original]
        media_fator = float(X[:, indice_original].mean())
        coeficiente = float(modelo["coef"][posicao_modelo])

        impacto = (
            coeficiente
            * VARIACAO_IMPACTO
            * media_fator
        )

        fatores.append({
            "Variável": nome,
            "Descrição": FATORES[nome],
            "Coeficiente": coeficiente,
            "Média do fator": media_fator,
            "Impacto": impacto,
        })

    resultado = pd.DataFrame(fatores)

    media_resultado = float(np.mean(y))

    if media_resultado != 0:
        resultado["Impacto percentual"] = (
            resultado["Impacto"] / media_resultado
        ) * 100
    else:
        resultado["Impacto percentual"] = np.nan

    resultado = (
        resultado
        .sort_values(
            "Impacto",
            key=lambda coluna: coluna.abs(),
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return {
        "fatores": resultado,
        "modelo": modelo,
        "dados": dados,
        "media_resultado": media_resultado,
        "removidos": removidos,
    }, None

def _simular_indicador(df, ano, cenario, fator, variacao):

    dados = df.loc[
        (df["Ano"] == ano) &
        (df["Cenario"] == cenario)
    ]

    if dados.empty:
        return None, "Não foram encontrados dados para esse cenário e ano."

    linha = dados.iloc[0]

    def normalizar(nome):
        return " ".join(str(nome).split())

    colunas = {normalizar(coluna): coluna for coluna in df.columns}

    def valor_em(registro, conta):
        coluna = colunas.get(normalizar(conta))

        if coluna is None:
            return np.nan

        resultado = pd.to_numeric(
            pd.Series([registro.get(coluna, np.nan)]),
            errors="coerce",
        ).iloc[0]

        return float(resultado) if pd.notna(resultado) else np.nan

    def valor(conta):
        return valor_em(linha, conta)

    anterior = df.loc[
        (df["Ano"] == ano - 1) &
        (df["Cenario"] == cenario)
    ]

    clientes_anterior = (
        abs(valor_em(anterior.iloc[0], "BAL - Contas a Receber - Clientes"))
        if not anterior.empty else np.nan
    )

    def dividir(a, b):
        if pd.isna(a) or pd.isna(b) or b == 0:
            return np.nan
        return a / b

    receita = valor("DRE - Receita")
    tributos = valor("DRE - Tributos")
    custos = abs(valor("DRE - Custos"))
    ebitda = valor("DRE - EBITDA")
    ebit = valor("DRE - Resultado Operacional")
    resultado_antes_ir = valor("DRE - Resultado Antes do Imposto de Renda")
    imposto_ir = abs(valor("DRE - Imposto de Renda e Contribuição Social"))

    ativo = abs(valor("BAL - Total do Ativo"))
    caixa = abs(valor("BAL - Disponível"))
    patrimonio = abs(valor("BAL - Patrimônio Líquido"))
    divida_cp = abs(valor("BAL - Emprést"))
    divida_lp = abs(valor("BAL - Empréstimos"))

    clientes = abs(valor("BAL - Contas a Receber - Clientes"))
    fornecedores = abs(valor("BAL - Fornecedores"))

    capex = abs(valor("FLU - Investimentos"))

    recebimentos = receita - (clientes - clientes_anterior)

    fco = (
        recebimentos
        + valor("FLU - Tributos")
        + valor("FLU - Custos")
        + valor("FLU - Imposto de Renda e Contribuição Social")
    )

    receita_liquida = receita + tributos
    capital_investido = patrimonio + divida_cp + divida_lp - caixa

    aliquota_ir = dividir(imposto_ir, resultado_antes_ir)
    if pd.isna(aliquota_ir):
        aliquota_ir = 0.0

    aliquota_ir = min(max(aliquota_ir, 0), 1)

    nopat = ebit * (1 - aliquota_ir)
    roic = dividir(nopat, capital_investido)

    wacc_base = 0.08
    eva = nopat - capital_investido * wacc_base

    margem_ebitda = dividir(ebitda, receita_liquida)
    pmr = dividir(clientes * 360, receita)
    pmp = dividir(fornecedores * 360, custos)

    ciclo = pmr - pmp if pd.notna(pmr) and pd.notna(pmp) else np.nan
    ncg = ciclo * custos / 360 if pd.notna(ciclo) else np.nan

    fcl = fco - capex if pd.notna(fco) else np.nan


    if fator == "WACC":
        wacc_novo = wacc_base * (1 + variacao)
        original = eva
        simulado = nopat - capital_investido * wacc_novo
        unidade = "R$"

    elif fator == "ROIC":
        roic_novo = roic * (1 + variacao)
        original = eva
        nopat_novo = roic_novo * capital_investido
        simulado = nopat_novo - capital_investido * wacc_base
        unidade = "R$"

    elif fator == "Margem EBITDA":
        margem_nova = margem_ebitda * (1 + variacao)
        original = ebitda
        simulado = margem_nova * receita_liquida
        unidade = "R$"

    elif fator == "Receita":
        receita_nova = receita * (1 + variacao)
        receita_liquida_nova = receita_liquida * (1 + variacao)
        original = ebitda
        simulado = margem_ebitda * receita_liquida_nova
        unidade = "R$"

    elif fator == "PMR":
        pmr_novo = pmr * (1 + variacao)
        ciclo_novo = pmr_novo - pmp
        ncg_nova = ciclo_novo * custos / 360

        original = ncg
        simulado = ncg_nova
        unidade = "R$"

    elif fator == "PMP":
        pmp_novo = pmp * (1 + variacao)
        ciclo_novo = pmr - pmp_novo
        ncg_nova = ciclo_novo * custos / 360

        original = ncg
        simulado = ncg_nova
        unidade = "R$"

    elif fator == "Investimentos":
        capex_novo = capex * (1 + variacao)
        original = fcl
        simulado = fco - capex_novo
        unidade = "R$"

    else:
        return None, "Fator de sensibilidade não reconhecido."

    if pd.isna(original) or pd.isna(simulado):
        return None, (
            "Não há dados suficientes para calcular essa simulação "
            "no cenário e ano selecionados."
        )

    return {
        "fator": fator,
        "original": original,
        "simulado": simulado,
        "impacto": simulado - original,
        "variacao": variacao,
        "unidade": unidade,
    }, None


def _renderizar_simulacao(df, ano, cenario):

    st.markdown(
        """
        <div class="sens-card-title">
            Simulação de indicadores financeiros
        </div>
        <div class="sens-card-note">
            Altere um fator e observe o impacto estimado
            sobre o indicador relacionado.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fatores_disponiveis = [
        "WACC",
        "ROIC",
        "Margem EBITDA",
        "Receita",
        "PMR",
        "PMP",
        "Investimentos",
    ]

    fator = st.selectbox(
        "Fator que deseja alterar",
        options=fatores_disponiveis,
        key="sens_fator_simulacao",
    )

    variacao = st.slider(
        "Variação aplicada (%)",
        min_value=-50,
        max_value=50,
        value=10,
        step=5,
        key="sens_variacao_simulacao",
    ) / 100

    resultado, erro = _simular_indicador(
        df,
        ano,
        cenario,
        fator,
        variacao,
    )

    if erro:
        st.warning(erro)
        return

    original = resultado["original"]
    simulado = resultado["simulado"]
    impacto = resultado["impacto"]

    def formatar(valor):
        return (
            "R$ "
            + _formatar_numero(valor / 1_000_000)
            + " mi"
        )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="sens-kpi">
                <div class="sens-kpi-label">Valor original</div>
                <div class="sens-kpi-value">{formatar(original)}</div>
                <div class="sens-kpi-note">Cenário de referência</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="sens-kpi">
                <div class="sens-kpi-label">Valor simulado</div>
                <div class="sens-kpi-value">{formatar(simulado)}</div>
                <div class="sens-kpi-note">
                    Variação de {variacao * 100:+.0f}% em {fator}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        cor = "#258B68" if impacto >= 0 else "#C65B5B"

        st.markdown(
            f"""
            <div class="sens-kpi">
                <div class="sens-kpi-label">Impacto estimado</div>
                <div class="sens-kpi-value" style="color:{cor}">
                    {formatar(impacto)}
                </div>
                <div class="sens-kpi-note">
                    Diferença entre os dois valores
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    grafico = pd.DataFrame({
        "Situação": ["Original", "Simulado"],
        "Valor (R$ mi)": [
            original / 1_000_000,
            simulado / 1_000_000,
        ],
    })

    chart = (
        alt.Chart(grafico)
        .mark_bar(
            cornerRadiusEnd=5,
            color="#2E91C9",
        )
        .encode(
            x=alt.X(
                "Situação:N",
                title=None,
                sort=["Original", "Simulado"],
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y(
                "Valor (R$ mi):Q",
                title="Valor (R$ milhões)",
                axis=alt.Axis(format=",.2f"),
            ),
            tooltip=[
                alt.Tooltip("Situação:N"),
                alt.Tooltip(
                    "Valor (R$ mi):Q",
                    format=",.2f",
                ),
            ],
        )
        .properties(height=300)
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

    como_interpretar(
        "sens_simulacao",
        [
            "**Valor original:** indicador calculado com os dados do cenário "
            "e do ano escolhidos.",
            "**Valor simulado:** o mesmo indicador depois de aplicar a "
            "variação escolhida em um único fator, mantendo os demais iguais.",
            "**Impacto estimado:** diferença entre o simulado e o original. "
            "Verde indica aumento e vermelho indica redução.",
            "**Indicador afetado por cada fator:** WACC e ROIC alteram o EVA; "
            "Margem EBITDA e Receita alteram o EBITDA; PMR e PMP alteram a "
            "necessidade de capital de giro; Investimentos alteram o fluxo de caixa livre.",
        ],
        "os resultados são estimativas matemáticas, não previsões, e não "
        "provam causa e efeito. As simulações de PMR e PMP usam uma "
        "estimativa simplificada da necessidade de capital de giro.",
    )


def _cabecalho(anos, cenarios):

    with st.container(key="sens_topo"):

        titulo, col_ano, col_cenario = st.columns(
            [2.8, 1, 1.2],
            vertical_alignment="bottom",
        )

        with titulo:
            st.markdown(
                """
                <div class="sens-eyebrow">PAINEL FINANCEIRO</div>
                <div class="sens-title">Sensibilidade</div>
                <div class="sens-subtitle">
                    Avalie como variações nos fatores financeiros
                    se relacionam com a geração de caixa.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_ano:
            ano = st.selectbox(
                "Ano",
                options=anos,
                index=len(anos) - 1,
                format_func=lambda valor: f"Ano {valor}",
                key="sens_ano",
            )

        with col_cenario:
            cenario = st.selectbox(
                "Cenário de referência",
                options=cenarios,
                format_func=lambda valor: f"Cenário {valor}",
                key="sens_cenario",
            )

    return ano, cenario


def _grafico_sensibilidade(fatores):

    dados_grafico = fatores.copy()

    dados_grafico["Cor"] = np.where(
        dados_grafico["Impacto"] >= 0,
        "Positivo",
        "Negativo",
    )

    ordem = (
        dados_grafico
        .sort_values("Impacto", ascending=True)["Variável"]
        .tolist()
    )

    barras = (
        alt.Chart(dados_grafico)
        .mark_bar(
            size=27,
            cornerRadiusEnd=4,
        )
        .encode(
            x=alt.X(
                "Impacto:Q",
                title="Impacto estimado na geração de caixa (R$ mi)",
                axis=alt.Axis(format=",.2f"),
            ),
            y=alt.Y(
                "Variável:N",
                sort=ordem,
                title=None,
            ),
            color=alt.Color(
                "Cor:N",
                scale=alt.Scale(
                    domain=["Positivo", "Negativo"],
                    range=["#258B68", "#C65B5B"],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Variável:N", title="Variável"),
                alt.Tooltip(
                    "Impacto:Q",
                    title="Impacto (R$ mi)",
                    format=",.2f",
                ),
                alt.Tooltip(
                    "Impacto percentual:Q",
                    title="Impacto sobre a média (%)",
                    format="+.2f",
                ),
            ],
        )
    )

    linha_zero = (
        alt.Chart(pd.DataFrame({"zero": [0]}))
        .mark_rule(
            color="#8B9BAD",
            strokeDash=[4, 3],
        )
        .encode(x="zero:Q")
    )

    return (
        (barras + linha_zero)
        .properties(
            height=max(190, len(dados_grafico) * 65),
        )
        .configure_view(stroke=None)
        .configure_axis(
            labelColor="#52677D",
            titleColor="#52677D",
            gridColor="#EEF3F9",
        )
    )


def _tabela_impactos(fatores):

    tabela = fatores[
        ["Variável", "Impacto", "Impacto percentual"]
    ].copy()

    tabela["Impacto"] = tabela["Impacto"].apply(
        lambda valor: (
            "—"
            if pd.isna(valor)
            else (
                ("+" if valor > 0 else "")
                + _formatar_numero(valor)
                + " mi"
            )
        )
    )

    tabela["Impacto percentual"] = tabela[
        "Impacto percentual"
    ].apply(
        lambda valor: (
            "—"
            if pd.isna(valor)
            else (
                ("+" if valor > 0 else "")
                + _formatar_numero(valor)
                + "%"
            )
        )
    )

    tabela = tabela.rename(
        columns={
            "Impacto": "Impacto (R$ mi)",
            "Impacto percentual": "Variação (%)",
        }
    )

    st.dataframe(
        tabela,
        use_container_width=True,
        hide_index=True,
        height=min(400, 85 + len(tabela) * 42),
    )


def _card_grafico(fatores):

    with st.container(key="sens_card_grafico"):

        st.markdown(
            """
            <div class="sens-card-title">
                Análise de sensibilidade
            </div>
            <div class="sens-card-note">
                Impacto estimado na geração de caixa após
                uma variação de 10% em cada fator.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.altair_chart(
            _grafico_sensibilidade(fatores),
            use_container_width=True,
        )


def _card_tabela(fatores):

    with st.container(key="sens_card_tabela"):

        st.markdown(
            """
            <div class="sens-card-title">
                Impacto calculado
            </div>
            <div class="sens-card-note">
                Valores estimados pelo modelo de regressão.
            </div>
            """,
            unsafe_allow_html=True,
        )

        _tabela_impactos(fatores)


def _indicadores_ajuste(modelo, quantidade):

    r2 = modelo["r2_ajustado"]

    if pd.isna(r2):
        qualidade = "Não disponível"
        percentual = "—"
    else:
        percentual = _formatar_numero(r2 * 100, 1) + "%"

        if r2 >= 0.7:
            qualidade = "Explica bem"
        elif r2 >= 0.4:
            qualidade = "Explica em parte"
        else:
            qualidade = "Explica pouco"

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            f"""
            <div class="sens-kpi">
                <div class="sens-kpi-label">Poder explicativo</div>
                <div class="sens-kpi-value">{percentual}</div>
                <div class="sens-kpi-note">{qualidade}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="sens-kpi">
                <div class="sens-kpi-label">Cenários analisados</div>
                <div class="sens-kpi-value">{quantidade}</div>
                <div class="sens-kpi-note">Com dados completos</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="sens-kpi">
                <div class="sens-kpi-label">Variação aplicada</div>
                <div class="sens-kpi-value">
                    {_formatar_numero(VARIACAO_IMPACTO * 100, 0)}%
                </div>
                <div class="sens-kpi-note">Em cada fator analisado</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sensibilidade():

    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="sens_page"):

        try:
            df = carregar_demonstrativo()

        except Exception as erro:
            st.error(
                "Não foi possível carregar a base do demonstrativo: "
                f"{erro}"
            )
            return

        colunas_necessarias = [
            "Ano",
            "Cenario",
            VARIAVEIS[RESULTADO],
            *[VARIAVEIS[nome] for nome in FATORES],
        ]

        faltantes = [
            coluna
            for coluna in colunas_necessarias
            if coluna not in df.columns
        ]

        if faltantes:
            st.error(
                "A base não possui todas as colunas necessárias: "
                + ", ".join(faltantes)
            )
            return

        df = df.copy()

        df["Ano"] = pd.to_numeric(
            df["Ano"],
            errors="coerce",
        )

        df["Cenario"] = pd.to_numeric(
            df["Cenario"],
            errors="coerce",
        )

        anos = sorted(
            df["Ano"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        cenarios = sorted(
            df["Cenario"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        if not anos or not cenarios:
            st.warning(
                "Não há anos ou cenários disponíveis na base."
            )
            return

        ano, cenario = _cabecalho(anos, cenarios)
        modo_sensibilidade = st.radio(
            "Tipo de análise",
            options=[
                "Regressão atual",
                "Simulação de indicadores",
            ],
            horizontal=True,
            key="sens_modo_analise",
        )

        if modo_sensibilidade == "Simulação de indicadores":
            _renderizar_simulacao(
                df,
                ano,
                cenario,
            )
            return

        resultado, erro = _calcular_sensibilidade(df, ano)

        if erro:
            st.warning(erro)
            return

        fatores = resultado["fatores"]
        modelo = resultado["modelo"]
        dados = resultado["dados"]

        _indicadores_ajuste(
            modelo,
            len(dados),
        )

        st.write("")

        col_grafico, col_tabela = st.columns(
            [1.55, 1],
            gap="medium",
        )

        with col_grafico:
            _card_grafico(fatores)

        with col_tabela:
            _card_tabela(fatores)

        como_interpretar(
            "sens_regressao",
            [
                "**Barras:** mostram quanto a geração de caixa muda, em R$ "
                "milhões, se cada fator variar 10% e os demais ficarem iguais.",
                "**Verde e vermelho:** verde indica aumento estimado do caixa; "
                "vermelho indica redução estimada.",
                "**Variação (%):** o mesmo impacto em relação à geração de caixa "
                "média dos cenários do ano.",
                "**Poder explicativo:** quanto das diferenças de caixa entre os "
                "cenários os fatores conseguem explicar juntos.",
                "**Custos e Investimentos:** são saídas de dinheiro; crescer "
                "significa gastar mais.",
            ],
            "os dados são de cenários simulados. A regressão mostra "
            "associações e não comprova causa e efeito. Os resultados dependem "
            "da variação entre os cenários disponíveis.",
        )

        st.caption(
            f"Cenário de referência selecionado: {cenario}. "
            "A regressão considera todos os cenários disponíveis "
            "no ano selecionado."
        )

        if resultado["removidos"]:
            st.caption(
                "Fatores retirados do modelo por colinearidade "
                "ou ausência de variação: "
                + ", ".join(resultado["removidos"])
            )