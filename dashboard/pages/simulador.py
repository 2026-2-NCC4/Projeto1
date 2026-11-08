import altair as alt
import pandas as pd
import streamlit as st

from components.como_interpretar import como_interpretar
from data.load_data import carregar_demonstrativo
from pages.regressao import _moeda_mi, _num

MEDIA_CENARIOS = "Média dos cenários"


PREMISSAS = {
    "receita": "Receita",
    "custos": "Custos",
    "tributos": "Tributos",
    "investimentos": "Investimentos",
}
LIMITE_PREMISSA = 30


DRE = {
    "receita": "DRE - Receita",
    "tributos": "DRE - Tributos",
    "custos": "DRE - Custos",
    "depreciacao": "DRE - Depreciação e Amortização",
    "resultado_financeiro": "DRE - Resultado Financeiro",
    "outros": "DRE - Outros Resultados Operacionais",
    "antes_ir": "DRE - Resultado Antes do Imposto de Renda",
    "ir": "DRE - Imposto de Renda e Contribuição Social",
    "resultado": "DRE - Resultado Líquido",
    "ebitda": "DRE - EBITDA",
}
FLUXO = {
    "receita": "FLU - Receita",
    "tributos": "FLU - Tributos",
    "custos": "FLU - Custos",
    "investimentos": "FLU - Investimentos",
    "ir": "FLU - Imposto de Renda e Contribuição Social",
    "caixa": "FLU - Geração de Caixa",
}


ALIQUOTA_PADRAO = -0.342

INDICADORES_GRAFICO = {
    "EBITDA": "ebitda",
    "Resultado Líquido": "resultado",
    "Geração de Caixa": "caixa",
}

PAGE_STYLE = """
<style>
    .st-key-sim_page {
        padding: 28px 32px 40px;
        gap: 16px !important;
    }

    .sim-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .sim-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .sim-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .st-key-sim_topo [data-testid="stHorizontalBlock"] {
        align-items: flex-end;
    }

    .st-key-sim_page label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-sim_page [data-testid="stSelectbox"] [role="group"] {
        background: #fff !important;
        border: 1px solid #D5E3EE !important;
        border-radius: 10px !important;
    }

        .st-key-sim_premissas,
    [class*="st-key-sim_kpi_"],
    .st-key-sim_grafico,
    .st-key-sim_cascata {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
    }

    .st-key-sim_premissas [data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    .st-key-sim_restaurar button {
        background: #EEF5FC !important;
        color: var(--cti-blue) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600;
    }

    .st-key-sim_restaurar button:hover {
        background: #DCEBFC !important;
    }

    .sim-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
    }

    .sim-card-note {
        font-size: 12px;
        color: #8AA4BF;
        margin: 2px 0 10px;
        line-height: 1.5;
    }

        .st-key-sim_page [data-testid="stHorizontalBlock"]:has([class*="st-key-sim_kpi_"]),
    .st-key-sim_page [data-testid="stHorizontalBlock"]:has(.st-key-sim_grafico) {
        align-items: stretch;
    }

    .st-key-sim_page [data-testid="stColumn"]:has([class*="st-key-sim_kpi_"]) > div,
    .st-key-sim_page [data-testid="stColumn"]:has(.st-key-sim_grafico) > div,
    .st-key-sim_page [data-testid="stColumn"]:has(.st-key-sim_cascata) > div,
    .st-key-sim_page [data-testid="stLayoutWrapper"]:has(> [class*="st-key-sim_kpi_"]),
    .st-key-sim_page [data-testid="stLayoutWrapper"]:has(> .st-key-sim_grafico),
    .st-key-sim_page [data-testid="stLayoutWrapper"]:has(> .st-key-sim_cascata),
    [class*="st-key-sim_kpi_"],
    .st-key-sim_grafico,
    .st-key-sim_cascata {
        height: 100%;
    }

    [class*="st-key-sim_kpi_"] {
        padding: 14px 16px;
    }

    .sim-kpi-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--cti-text);
        margin-bottom: 8px;
    }

    .sim-kpi-rotulo {
        font-size: 10.5px;
        color: #8AA4BF;
    }

    .sim-kpi-simulado {
        font-size: clamp(16px, 1.5vw, 22px);
        font-weight: 700;
        color: var(--cti-blue);
        white-space: nowrap;
        line-height: 1.3;
    }

    .sim-kpi-original {
        font-size: 11.5px;
        color: var(--cti-muted);
        white-space: nowrap;
        margin-top: 2px;
    }

    .sim-kpi-delta {
        font-size: 12px;
        font-weight: 700;
        margin-top: 8px;
    }

    .sim-sobe { color: #2E8B6A; }
    .sim-desce { color: #C2410C; }
    .sim-igual { color: #8AA4BF; }

    .sim-insight {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        background: #EEF5FC;
        border: 1px solid #DCEBFC;
        border-radius: 14px;
        padding: 16px 20px;
        font-size: 13px;
        color: var(--cti-text);
    }

    .sim-insight-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        width: 34px;
        height: 34px;
        border-radius: 9px;
        background: #fff;
        color: var(--cti-blue);
        font-size: 17px;
        font-weight: 700;
    }

    .sim-insight p {
        margin: 0;
        line-height: 1.6;
    }

    .sim-insight .sim-ressalva {
        display: block;
        margin-top: 6px;
        font-size: 11.5px;
        color: var(--cti-muted);
    }
</style>
"""


def simular(base, premissas):
    r, c = premissas["receita"], premissas["custos"]
    t, i = premissas["tributos"], premissas["investimentos"]

    receita = base[DRE["receita"]] * (1 + r)
    tributos = base[DRE["tributos"]] * (1 + r) * (1 + t)
    custos = base[DRE["custos"]] * (1 + c)

    variacao_operacional = (
        (receita - base[DRE["receita"]])
        + (tributos - base[DRE["tributos"]])
        + (custos - base[DRE["custos"]])
    )

    antes_ir_base = base[DRE["antes_ir"]]
    antes_ir = antes_ir_base + variacao_operacional

    if antes_ir_base > 0:

        aliquota = base[DRE["ir"]] / antes_ir_base
        ir = aliquota * antes_ir if antes_ir > 0 else 0.0
    else:

        ir = base[DRE["ir"]] + (ALIQUOTA_PADRAO * antes_ir if antes_ir > 0 else 0.0)

    resultado = antes_ir + ir


    fator_ir = ir / base[DRE["ir"]] if base[DRE["ir"]] else 1.0
    variacao_caixa = (
        base[FLUXO["receita"]] * r
        + base[FLUXO["tributos"]] * ((1 + r) * (1 + t) - 1)
        + base[FLUXO["custos"]] * c
        + base[FLUXO["investimentos"]] * i
        + base[FLUXO["ir"]] * (fator_ir - 1)
    )

    return {
        "receita": receita,
        "tributos": tributos,
        "custos": custos,
        "depreciacao": base[DRE["depreciacao"]],
        "financeiro_outros": base[DRE["resultado_financeiro"]] + base[DRE["outros"]],
        "ir": ir,
        "resultado": resultado,
        "ebitda": base[DRE["ebitda"]] + variacao_operacional,
        "caixa": base[FLUXO["caixa"]] + variacao_caixa,
    }


def _base(df, ano, cenario):
    colunas = list(DRE.values()) + list(FLUXO.values())
    dados = df[df["Ano"] == ano]

    if cenario != MEDIA_CENARIOS:
        dados = dados[dados["Cenario"] == cenario]

    if dados.empty:
        return None

    return dados[colunas].astype(float).mean() / 1e6


def _margem(valor, receita):
    return valor / receita if receita else float("nan")


def _pct(valor, casas=1):
    return f"{_num(valor * 100, casas)}%"


def _compacto(valor):
    if abs(valor) >= 1000:
        return f"{_num(valor / 1000, 1)} bi"
    return f"{_num(valor, 0)} mi"


def _delta_moeda(diferenca):
    if abs(diferenca) < 0.005:
        return "sim-igual", "Sem mudança"
    classe = "sim-sobe" if diferenca > 0 else "sim-desce"
    return classe, ("Δ +" if diferenca > 0 else "Δ −") + _moeda_mi(abs(diferenca))


def _delta_pp(diferenca):
    pontos = diferenca * 100
    if abs(pontos) < 0.05:
        return "sim-igual", "Sem mudança"
    classe = "sim-sobe" if pontos > 0 else "sim-desce"
    return classe, f"Δ {'+' if pontos > 0 else '−'}{_num(abs(pontos), 1)} p.p."


def _restaurar():
    for chave in PREMISSAS:
        st.session_state[f"sim_premissa_{chave}"] = 0


def _topo(anos, cenarios):
    with st.container(key="sim_topo"):
        titulo, col_ano, col_cenario = st.columns([2.8, 1, 1.4])

        with titulo:
            st.markdown("""
                <div class="sim-eyebrow">PAINEL FINANCEIRO</div>
                <div class="sim-title">Simular novo cenário</div>
                <div class="sim-subtitle">
                    Ajuste as premissas e veja como os resultados mudam.
                </div>
            """, unsafe_allow_html=True)

        with col_ano:
            ano = st.selectbox(
                "Ano",
                options=anos,
                index=len(anos) - 1,
                format_func=lambda a: f"Ano {a}",
                key="sim_ano",
            )

        with col_cenario:
            cenario = st.selectbox(
                "Cenário base",
                options=[MEDIA_CENARIOS] + cenarios,
                format_func=lambda c: c if c == MEDIA_CENARIOS else f"Cenário {c}",
                key="sim_cenario",
            )

    return ano, cenario


def _premissas():
    for chave in PREMISSAS:
        st.session_state.setdefault(f"sim_premissa_{chave}", 0)

    with st.container(key="sim_premissas"):
        titulo, botao = st.columns([5, 1])

        with titulo:
            st.markdown(
                '<div class="sim-card-title">Premissas da simulação</div>'
                '<div class="sim-card-note">Quanto cada item muda em relação ao cenário '
                "base. Custos, Tributos e Investimentos são saídas de dinheiro: "
                "+10% significa gastar 10% a mais.</div>",
                unsafe_allow_html=True,
            )

        with botao:
            st.button(
                "Restaurar",
                icon=":material/restart_alt:",
                key="sim_restaurar",
                on_click=_restaurar,
                use_container_width=True,
            )

        colunas = st.columns(len(PREMISSAS), gap="large")
        for coluna, (chave, nome) in zip(colunas, PREMISSAS.items()):
            with coluna:
                st.slider(
                    nome,
                    min_value=-LIMITE_PREMISSA,
                    max_value=LIMITE_PREMISSA,
                    step=1,
                    format="%+d%%",
                    key=f"sim_premissa_{chave}",
                )

    return {chave: st.session_state[f"sim_premissa_{chave}"] / 100 for chave in PREMISSAS}


def _kpi(key, rotulo, original, simulado, delta):


    classe, texto_delta = delta
    with st.container(key=key):
        st.markdown(
            f'<div class="sim-kpi-label">{rotulo}</div>'
            f'<div class="sim-kpi-rotulo">Simulado</div>'
            f'<div class="sim-kpi-simulado">{simulado}</div>'
            f'<div class="sim-kpi-original">Original: {original}</div>'
            f'<div class="sim-kpi-delta {classe}">{texto_delta}</div>',
            unsafe_allow_html=True,
        )


def _kpis(original, simulado):
    margem_ebitda = (_margem(original["ebitda"], original["receita"]),
                     _margem(simulado["ebitda"], simulado["receita"]))
    margem_liquida = (_margem(original["resultado"], original["receita"]),
                      _margem(simulado["resultado"], simulado["receita"]))

    colunas = st.columns(5, gap="small")
    cartoes = [
        ("sim_kpi_ebitda", "EBITDA", original["ebitda"], simulado["ebitda"], "moeda"),
        ("sim_kpi_margem_ebitda", "Margem EBITDA", *margem_ebitda, "pct"),
        ("sim_kpi_resultado", "Resultado Líquido", original["resultado"], simulado["resultado"], "moeda"),
        ("sim_kpi_margem_liquida", "Margem Líquida", *margem_liquida, "pct"),
        ("sim_kpi_caixa", "Geração de Caixa", original["caixa"], simulado["caixa"], "moeda"),
    ]

    for coluna, (key, rotulo, antes, depois, tipo) in zip(colunas, cartoes):
        with coluna:
            if tipo == "moeda":
                _kpi(key, rotulo, _moeda_mi(antes), _moeda_mi(depois), _delta_moeda(depois - antes))
            else:
                _kpi(key, rotulo, _pct(antes), _pct(depois), _delta_pp(depois - antes))


def _grafico_anos(df, cenario, premissas, ano_escolhido):
    with st.container(key="sim_grafico"):
        st.markdown(
            '<div class="sim-card-title">Original × Simulado</div>'
            '<div class="sim-card-note">As mesmas premissas aplicadas a todos os anos.</div>',
            unsafe_allow_html=True,
        )

        indicador = st.segmented_control(
            "Indicador",
            options=list(INDICADORES_GRAFICO),
            default="EBITDA",
            key="sim_indicador",
            label_visibility="collapsed",
        ) or "EBITDA"

        chave = INDICADORES_GRAFICO[indicador]
        linhas = []
        for ano in sorted(df["Ano"].dropna().astype(int).unique()):
            base = _base(df, ano, cenario)
            if base is None:
                continue
            original = simular(base, {k: 0 for k in PREMISSAS})[chave]
            simulado = simular(base, premissas)[chave]
            linhas += [
                {"Ano": f"Ano {ano}", "Ordem": ano, "Versão": "Original", "Valor": original},
                {"Ano": f"Ano {ano}", "Ordem": ano, "Versão": "Simulado", "Valor": simulado},
            ]

        dados = pd.DataFrame(linhas)
        rotulo = "replace(format(datum.value, ',.0f'), ',', '.')"

        grafico = alt.Chart(dados).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("Ano:N", sort=alt.SortField("Ordem"), title=None,
                    axis=alt.Axis(labelAngle=0)),
            xOffset=alt.XOffset("Versão:N", sort=["Original", "Simulado"]),
            y=alt.Y("Valor:Q", title=f"{indicador} (R$ mi)", axis=alt.Axis(labelExpr=rotulo)),
            color=alt.Color(
                "Versão:N",
                scale=alt.Scale(domain=["Original", "Simulado"], range=["#B7D3EE", "#1F6FD1"]),
                legend=alt.Legend(orient="top", title=None),
            ),
            opacity=alt.condition(
                alt.datum.Ordem == ano_escolhido, alt.value(1), alt.value(0.75)
            ),
            tooltip=[
                alt.Tooltip("Ano:N"),
                alt.Tooltip("Versão:N"),
                alt.Tooltip("Valor:Q", format=",.1f", title="R$ mi"),
            ],
        ).properties(height=280).configure_axis(
            grid=False,
            labelColor="#55799F",
            titleColor="#55799F",
            titleFontWeight=500,
            domainColor="#C3D9F2",
            tickColor="#C3D9F2",
        ).configure_view(strokeWidth=0)

        st.altair_chart(grafico, use_container_width=True)


def _cascata(simulado, ano):
    etapas = [
        ("Receita", simulado["receita"], "total"),
        ("Tributos", simulado["tributos"], "passo"),
        ("Custos", simulado["custos"], "passo"),
        ("Depreciação", simulado["depreciacao"], "passo"),
        ("Financeiro", simulado["financeiro_outros"], "passo"),
        ("IR", simulado["ir"], "passo"),
        ("Resultado", simulado["resultado"], "total"),
    ]

    linhas, acumulado = [], 0.0
    for ordem, (nome, valor, tipo) in enumerate(etapas):
        if tipo == "total":
            inicio, fim = 0.0, valor
            acumulado = valor
            cor = "Total"
        else:
            inicio, fim = acumulado, acumulado + valor
            acumulado = fim
            cor = "Aumenta" if valor >= 0 else "Diminui"
        linhas.append({
            "Etapa": nome, "Ordem": ordem, "Inicio": inicio, "Fim": fim,
            "Valor": valor, "Cor": cor, "Rotulo": _compacto(valor),
        })


    dados = pd.DataFrame(linhas)
    dados["Direita"] = dados[["Inicio", "Fim"]].max(axis=1)
    eixo_y = alt.Y("Etapa:N", sort=alt.SortField("Ordem"), title=None,
                   axis=alt.Axis(labelLimit=110, labelFontSize=11))
    rotulo_eixo = "replace(format(datum.value, ',.0f'), ',', '.')"


    menor = min(0.0, float(dados[["Inicio", "Fim"]].min().min()))
    maior = float(dados["Direita"].max())
    escala = alt.Scale(domain=[menor, maior + (maior - menor) * 0.35], nice=False)

    barras = alt.Chart(dados).mark_bar(cornerRadius=3, height=22).encode(
        y=eixo_y,
        x=alt.X("Inicio:Q", title="R$ mi", scale=escala,
                axis=alt.Axis(labelExpr=rotulo_eixo, tickCount=4)),
        x2="Fim:Q",
        color=alt.Color(
            "Cor:N",
            scale=alt.Scale(domain=["Total", "Aumenta", "Diminui"],
                            range=["#1F6FD1", "#6DB59A", "#E29A8F"]),
            legend=None,
        ),
        tooltip=[alt.Tooltip("Etapa:N"), alt.Tooltip("Valor:Q", format=",.1f", title="R$ mi")],
    )

    textos = alt.Chart(dados).mark_text(
        align="left", dx=5, fontSize=10.5, color="#55799F"
    ).encode(y=eixo_y, x="Direita:Q", text="Rotulo:N")

    grafico = alt.layer(barras, textos).properties(height=280).configure_axis(
        grid=False,
        labelColor="#55799F",
        titleColor="#55799F",
        titleFontWeight=500,
        domainColor="#C3D9F2",
        tickColor="#C3D9F2",
    ).configure_view(strokeWidth=0)

    with st.container(key="sim_cascata"):
        st.markdown(
            '<div class="sim-card-title">Cascata simulada</div>'
            f'<div class="sim-card-note">Da receita ao resultado líquido no Ano {ano}, '
            "já com as premissas. Financeiro inclui outros resultados operacionais.</div>",
            unsafe_allow_html=True,
        )
        st.altair_chart(grafico, use_container_width=True)


RESSALVA_SIMULACAO = (
    "Simulação contábil simplificada: os tributos acompanham a receita, a alíquota "
    "efetiva de IR é mantida e os investimentos afetam só o caixa."
)


def texto_simulacao(premissas, original, simulado, ano):
    """Frase de conclusão e ícone (usado pela tela e pelo relatório em PDF)."""
    if not any(premissas.values()):
        texto = (
            "Mova as premissas acima para ver o efeito. Por enquanto, os valores simulados "
            "são iguais aos do cenário base."
        )
        icone = "↗"
    else:
        mudancas = [
            f"{'+' if v > 0 else '−'}{_num(abs(v) * 100, 0)}% em {PREMISSAS[k]}"
            for k, v in premissas.items() if v
        ]
        if len(mudancas) > 1:
            premissa_txt = ", ".join(mudancas[:-1]) + " e " + mudancas[-1]
        else:
            premissa_txt = mudancas[0]

        dif_resultado = simulado["resultado"] - original["resultado"]
        dif_caixa = simulado["caixa"] - original["caixa"]
        dif_margem = (
            _margem(simulado["ebitda"], simulado["receita"])
            - _margem(original["ebitda"], original["receita"])
        ) * 100

        texto = (
            f"Com {premissa_txt}, o Resultado Líquido do Ano {ano} "
            f"{'sobe' if dif_resultado >= 0 else 'cai'} {_moeda_mi(abs(dif_resultado))}, "
            f"a Geração de Caixa {'sobe' if dif_caixa >= 0 else 'cai'} "
            f"{_moeda_mi(abs(dif_caixa))} e a margem EBITDA "
            f"{'ganha' if dif_margem >= 0 else 'perde'} {_num(abs(dif_margem), 1)} p.p."
        )
        icone = "↗" if dif_resultado >= 0 else "↘"

    return texto, icone


def _insight(premissas, original, simulado, ano):
    ressalva = f'<span class="sim-ressalva">{RESSALVA_SIMULACAO}</span>'
    texto, icone = texto_simulacao(premissas, original, simulado, ano)

    st.markdown(
        f'<div class="sim-insight"><span class="sim-insight-icon">{icone}</span>'
        f"<p>{texto}{ressalva}</p></div>",
        unsafe_allow_html=True,
    )


def render_simulador():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="sim_page"):
        try:
            df = carregar_demonstrativo()
        except Exception as erro:
            st.error(f"Não foi possível carregar a base do demonstrativo: {erro}")
            return

        anos = sorted(df["Ano"].dropna().astype(int).unique().tolist())
        cenarios = sorted(df["Cenario"].dropna().astype(int).unique().tolist())

        ano, cenario = _topo(anos, cenarios)
        premissas = _premissas()

        base = _base(df, ano, cenario)
        if base is None:
            st.warning("Não há dados para este cenário no ano escolhido.")
            return

        original = simular(base, {k: 0 for k in PREMISSAS})
        simulado = simular(base, premissas)

        _kpis(original, simulado)

        col_grafico, col_cascata = st.columns([1.5, 1], gap="medium")
        with col_grafico:
            _grafico_anos(df, cenario, premissas, ano)
        with col_cascata:
            _cascata(simulado, ano)

        _insight(premissas, original, simulado, ano)

        como_interpretar(
            "sim",
            [
                "**Premissas:** escolha quanto Receita, Custos, Tributos e "
                "Investimentos mudam, em %. Use Restaurar para voltar a zero.",
                "**Cards:** comparam o valor original com o simulado.",
                "**Gráfico por ano:** mostra o indicador escolhido ao longo dos "
                "anos, antes e depois da simulação.",
                "**Cascata:** mostra como a receita simulada chega ao resultado, "
                "passo a passo.",
            ],
            "a simulação refaz as contas com regras simplificadas e não "
            "representa uma previsão.",
        )