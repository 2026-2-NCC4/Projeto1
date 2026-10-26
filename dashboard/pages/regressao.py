import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from data.load_data import carregar_demonstrativo

# Nome exibido -> coluna da base. Valores monetários são convertidos para R$ mi.
VARIAVEIS = {
    "EBITDA": "DRE - EBITDA",
    "Receita": "DRE - Receita",
    "Custos": "DRE - Custos",
    "Tributos": "DRE - Tributos",
    "Depreciação e Amortização": "DRE - Depreciação e Amortização",
    "Resultado Operacional": "DRE - Resultado Operacional",
    "Resultado Financeiro": "DRE - Resultado Financeiro",
    "Imposto de Renda": "DRE - Imposto de Renda e Contribuição Social",
    "Resultado Líquido": "DRE - Resultado Líquido",
    "Geração de Caixa": "FLU - Geração de Caixa",
    "Investimentos": "FLU - Investimentos",
}

# Mesmo modelo da Entrega 2 (análise de regressão). EBITDA a partir de
# Receita/Custos/Tributos é praticamente uma identidade contábil (R² ≈ 1).
DEPENDENTE_PADRAO = "Geração de Caixa"
PREDITORES_PADRAO = ["Resultado Líquido", "Custos", "Investimentos"]

# Acima disso um preditor é tratado como combinação exata dos outros
# (ex.: Tributos é sempre a mesma fração da Receita).
LIMITE_COLINEARIDADE = 0.9999

TODOS_OS_ANOS = "Todos os anos"

PAGE_STYLE = """
<style>
    .st-key-reg_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .reg-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .reg-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .reg-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .st-key-reg_topo [data-testid="stHorizontalBlock"] {
        align-items: flex-end;
    }

    .st-key-reg_topo label p,
    .st-key-reg_filtros label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-reg_nova_simulacao button {
        background: var(--cti-blue) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 40px;
        font-weight: 600;
        white-space: nowrap;
    }

    .st-key-reg_nova_simulacao button:hover {
        background: var(--cti-dark) !important;
    }

    /* cartões brancos */
    .st-key-reg_filtros,
    .st-key-reg_kpi_r2,
    .st-key-reg_kpi_erro,
    .st-key-reg_kpi_obs,
    .st-key-reg_coeficientes,
    .st-key-reg_grafico {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
    }

    .st-key-reg_filtros {
        padding: 12px 22px;
    }

    .st-key-reg_filtros [data-testid="stHorizontalBlock"] {
        align-items: center;
    }

    /* os chips quebram linha em vez de rolar para os lados */
    .st-key-reg_filtros [data-testid="stButtonGroup"] > div {
        flex-wrap: wrap;
        overflow: visible;
        row-gap: 6px;
    }

    .st-key-reg_filtros [data-testid="stButtonGroup"] button {
        border-radius: 999px;
        font-size: 12.5px;
    }

    .reg-kpi-label {
        font-size: 12px;
        color: var(--cti-muted);
    }

    .reg-kpi-value {
        font-size: clamp(20px, 1.9vw, 26px);
        white-space: nowrap;
        font-weight: 700;
        color: var(--cti-blue);
        line-height: 1.3;
    }

    .reg-kpi-note {
        font-size: 11px;
        color: #8AA4BF;
    }

    .reg-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
        margin-bottom: 12px;
    }

    .reg-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12.5px;
        color: var(--cti-text);
    }

    .reg-table th {
        text-align: left;
        font-weight: 500;
        color: var(--cti-muted);
        background: #F5F9FD;
        padding: 10px 12px;
    }

    .reg-table-wrap {
        overflow-x: auto;
    }

    .reg-table td {
        white-space: nowrap;
        padding: 12px;
        border-bottom: 1px solid #EEF3F9;
        font-variant-numeric: tabular-nums;
    }

    .reg-table td:first-child {
        font-weight: 700;
    }

    .reg-chart-note {
        font-size: 11px;
        color: #8AA4BF;
        margin-top: 4px;
    }

    .reg-insight {
        display: flex;
        align-items: center;
        gap: 16px;
        background: #EEF5FC;
        border: 1px solid #DCEBFC;
        border-radius: 14px;
        padding: 16px 20px;
        font-size: 13px;
        color: var(--cti-text);
    }

    .reg-insight-icon {
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

    .reg-insight p {
        margin: 0;
    }

    .reg-insight .reg-alerta {
        display: block;
        margin-top: 4px;
        color: #9A6700;
        font-size: 12px;
    }
</style>
"""


# ---------- Formatação ----------

def _num(valor, casas=2):
    texto = f"{abs(valor):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"−{texto}" if valor < 0 else texto


def _moeda_mi(valor):
    """Valor já em R$ mi -> 'R$ 0,42 mi' ou 'R$ 1,23 bi'."""
    if abs(valor) >= 1000:
        return f"R$ {_num(valor / 1000)} bi"
    return f"R$ {_num(valor)} mi"


def _p_valor(p):
    # Vai dentro de HTML, então o "<" precisa ser escapado
    return "&lt; 0,001" if p < 0.001 else _num(p, 3)


def _qualidade_ajuste(r2):
    if r2 >= 0.7:
        return "Bom ajuste"
    if r2 >= 0.4:
        return "Ajuste moderado"
    return "Ajuste fraco"


# ---------- Modelo ----------

def ajustar_ols(y, X):
    """Regressão linear por mínimos quadrados, com intercepto.

    Devolve um dict com coeficientes, erros padrão, p-valores, IC 95%,
    R² ajustado, RMSE e os valores previstos.
    """
    n, k = X.shape
    matriz = np.column_stack([np.ones(n), X])

    beta, *_ = np.linalg.lstsq(matriz, y, rcond=None)
    previsto = matriz @ beta
    residuos = y - previsto

    gl = n - k - 1
    sigma2 = residuos @ residuos / gl
    erro_padrao = np.sqrt(np.diag(sigma2 * np.linalg.pinv(matriz.T @ matriz)))

    with np.errstate(divide="ignore", invalid="ignore"):
        t = beta / erro_padrao
    p = 2 * stats.t.sf(np.abs(t), gl)
    margem = stats.t.ppf(0.975, gl) * erro_padrao

    sq_total = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (residuos @ residuos) / sq_total
    r2_ajustado = 1 - (1 - r2) * (n - 1) / gl

    return {
        "coef": beta[1:],
        "erro_padrao": erro_padrao[1:],
        "p": p[1:],
        "ic_inf": (beta - margem)[1:],
        "ic_sup": (beta + margem)[1:],
        "r2_ajustado": r2_ajustado,
        "rmse": float(np.sqrt(residuos @ residuos / n)),
        "previsto": previsto,
    }


def remover_colineares(X, nomes):
    """Separa os preditores que são (quase) combinação exata dos anteriores.

    Com eles o modelo não tem solução única e os coeficientes perdem o sentido.
    Devolve (índices mantidos, nomes removidos).
    """
    mantidos, removidos = [], []

    for i, nome in enumerate(nomes):
        if mantidos:
            outros = np.column_stack([np.ones(len(X)), X[:, mantidos]])
            beta, *_ = np.linalg.lstsq(outros, X[:, i], rcond=None)
            residuo = X[:, i] - outros @ beta
            variacao = ((X[:, i] - X[:, i].mean()) ** 2).sum()

            if variacao == 0 or 1 - (residuo @ residuo) / variacao > LIMITE_COLINEARIDADE:
                removidos.append(nome)
                continue

        elif X[:, i].std() == 0:
            removidos.append(nome)
            continue

        mantidos.append(i)

    return mantidos, removidos


# ---------- Blocos da página ----------

def _topo(anos, cenarios):
    with st.container(key="reg_topo"):
        titulo, col_ano, col_cenario, col_botao = st.columns(
            [2.6, 1, 1.2, 1.3], vertical_alignment="bottom"
        )

        with titulo:
            st.markdown("""
                <div class="reg-eyebrow">PAINEL FINANCEIRO</div>
                <div class="reg-title">Regressão</div>
                <div class="reg-subtitle">
                    Explore dados, cenários e recomendações para apoiar decisões.
                </div>
            """, unsafe_allow_html=True)

        with col_ano:
            ano = st.selectbox(
                "Ano",
                options=[TODOS_OS_ANOS] + anos,
                index=len(anos),
                format_func=lambda a: a if a == TODOS_OS_ANOS else f"Ano {a}",
                key="reg_ano",
            )

        with col_cenario:
            cenario = st.selectbox(
                "Cenário",
                options=cenarios,
                format_func=lambda c: f"Cenário {c}",
                key="reg_cenario",
            )

        with col_botao:
            if st.button(
                "Nova simulação",
                icon=":material/add:",
                key="reg_nova_simulacao",
                use_container_width=True,
            ):
                st.session_state.pagina_atual = "Simular novo cenário"
                st.rerun()

    return ano, cenario


def _filtros():
    with st.container(key="reg_filtros"):
        col_dep, col_pred = st.columns([1.2, 4], vertical_alignment="center")

        with col_dep:
            dependente = st.selectbox(
                "Variável dependente",
                options=list(VARIAVEIS),
                index=list(VARIAVEIS).index(DEPENDENTE_PADRAO),
                key="reg_dependente",
            )

        opcoes = [nome for nome in VARIAVEIS if nome != dependente]

        with col_pred:
            # A key muda com a dependente para não manter um preditor
            # que deixou de ser opção válida.
            preditores = st.pills(
                "Preditores",
                options=opcoes,
                selection_mode="multi",
                default=[p for p in PREDITORES_PADRAO if p in opcoes],
                key=f"reg_preditores_{dependente}",
            )

    return dependente, list(preditores or [])


def _kpi(key, rotulo, valor, nota):
    with st.container(key=key):
        st.markdown(f"""
            <div class="reg-kpi-label">{rotulo}</div>
            <div class="reg-kpi-value">{valor}</div>
            <div class="reg-kpi-note">{nota}</div>
        """, unsafe_allow_html=True)


def _tabela_coeficientes(preditores, modelo):
    linhas = "".join(
        f"""
        <tr>
            <td>{nome}</td>
            <td>{_num(modelo["coef"][i])}</td>
            <td>{_num(modelo["erro_padrao"][i])}</td>
            <td>{_p_valor(modelo["p"][i])}</td>
            <td>{_num(modelo["ic_inf"][i])} – {_num(modelo["ic_sup"][i])}</td>
        </tr>
        """
        for i, nome in enumerate(preditores)
    )

    st.markdown(f"""
        <div class="reg-card-title">Coeficientes do modelo</div>
        <div class="reg-table-wrap">
        <table class="reg-table">
            <thead>
                <tr>
                    <th>Variável</th>
                    <th>Coeficiente</th>
                    <th>Erro padrão</th>
                    <th>p-valor</th>
                    <th>IC 95%</th>
                </tr>
            </thead>
            <tbody>{linhas}</tbody>
        </table>
        </div>
    """, unsafe_allow_html=True)


def _grafico(observado, previsto, cenarios, cenario_destacado, dependente):
    dados = pd.DataFrame({
        "Observado": observado,
        "Previsto": previsto,
        "Cenario": cenarios,
    })

    destaque = dados[dados["Cenario"] == cenario_destacado]

    # Muitos pontos deixam o gráfico pesado; uma amostra mostra o mesmo padrão
    if len(dados) > 2000:
        dados = dados.sample(2000, random_state=0)

    minimo = float(min(dados["Observado"].min(), dados["Previsto"].min()))
    maximo = float(max(dados["Observado"].max(), dados["Previsto"].max()))
    eixo = alt.Scale(domain=[minimo, maximo], nice=True, zero=False)
    tooltip = [
        alt.Tooltip("Cenario:Q", title="Cenário"),
        alt.Tooltip("Observado:Q", format=",.1f", title="Observado (R$ mi)"),
        alt.Tooltip("Previsto:Q", format=",.1f", title="Previsto (R$ mi)"),
    ]

    # Rótulos no padrão brasileiro: 1.234 em vez de 1,234
    rotulo = "replace(format(datum.value, ',.0f'), ',', '.')"

    pontos = alt.Chart(dados).mark_circle(size=34, opacity=0.55, color="#4A90D9").encode(
        x=alt.X("Previsto:Q", scale=eixo, title="Previsto (R$ mi)",
                axis=alt.Axis(labelExpr=rotulo, tickCount=5)),
        y=alt.Y("Observado:Q", scale=eixo, title="Observado (R$ mi)",
                axis=alt.Axis(labelExpr=rotulo, tickCount=5)),
        tooltip=tooltip,
    )

    linha = alt.Chart(
        pd.DataFrame({"Previsto": [minimo, maximo], "Observado": [minimo, maximo]})
    ).mark_line(color="#3E9C7A", strokeWidth=1.5).encode(x="Previsto:Q", y="Observado:Q")

    camadas = [linha, pontos]

    if not destaque.empty:
        camadas.append(
            alt.Chart(destaque).mark_circle(
                size=150, color="#F59E0B", stroke="#fff", strokeWidth=2, opacity=1
            ).encode(x="Previsto:Q", y="Observado:Q", tooltip=tooltip)
        )

    grafico = alt.layer(*camadas).properties(height=300).configure_axis(
        grid=False,
        labelColor="#55799F",
        titleColor="#55799F",
        titleFontWeight=500,
        domainColor="#C3D9F2",
        tickColor="#C3D9F2",
    ).configure_view(strokeWidth=0)

    st.markdown('<div class="reg-card-title">Previsto × Observado</div>', unsafe_allow_html=True)
    st.altair_chart(grafico, use_container_width=True)

    nota = "Linha verde: previsão perfeita."
    if not destaque.empty:
        nota += f" Ponto laranja: Cenário {cenario_destacado}."
    st.markdown(f'<div class="reg-chart-note">{nota}</div>', unsafe_allow_html=True)


def _insight(dependente, preditores, modelo):
    # Destaca o preditor mais significativo (menor p-valor)
    i = int(np.argmin(modelo["p"]))
    nome, coef, p = preditores[i], modelo["coef"][i], modelo["p"][i]

    if p < 0.05:
        sinal = "+" if coef >= 0 else "−"
        texto = (
            f"A cada +R$ 1 mi em {nome}, {dependente} varia "
            f"{sinal}{_moeda_mi(abs(coef))}, mantendo o resto constante "
            f"(p {_p_valor(p) if p < 0.001 else '= ' + _p_valor(p)})."
        )
    else:
        texto = (
            "Nenhum preditor selecionado tem efeito estatisticamente "
            f"significativo sobre {dependente} (p ≥ 0,05)."
        )

    alerta = ""
    if modelo["r2_ajustado"] > 0.99:
        alerta = (
            '<span class="reg-alerta">R² muito próximo de 1: as variáveis podem estar '
            "ligadas por uma identidade contábil (uma é calculada a partir das outras), "
            "e não por uma relação a ser descoberta.</span>"
        )

    st.markdown(f"""
        <div class="reg-insight">
            <span class="reg-insight-icon">β</span>
            <p>{texto}{alerta}</p>
        </div>
    """, unsafe_allow_html=True)


# ---------- Página principal ----------

def render_regressao():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="reg_page"):
        try:
            df = carregar_demonstrativo()
        except Exception as erro:
            st.error(f"Não foi possível carregar a base do demonstrativo: {erro}")
            return

        anos = sorted(df["Ano"].dropna().astype(int).unique().tolist())
        cenarios = sorted(df["Cenario"].dropna().astype(int).unique().tolist())

        ano, cenario = _topo(anos, cenarios)
        dependente, preditores = _filtros()

        if not preditores:
            st.info("Selecione pelo menos um preditor para ajustar o modelo.")
            return

        colunas = [VARIAVEIS[dependente]] + [VARIAVEIS[p] for p in preditores]
        recorte = df if ano == TODOS_OS_ANOS else df[df["Ano"] == ano]
        recorte = recorte[["Cenario"] + colunas].dropna()

        if len(recorte) <= len(preditores) + 1:
            st.warning("Não há observações suficientes para ajustar o modelo neste recorte.")
            return

        # Valores em R$ mi: deixa os números legíveis e o cálculo mais estável
        y = recorte[colunas[0]].to_numpy(dtype=float) / 1e6
        X = recorte[colunas[1:]].to_numpy(dtype=float) / 1e6

        mantidos, removidos = remover_colineares(X, preditores)

        if removidos:
            st.warning(
                f"Removido do modelo: {', '.join(removidos)}. "
                "É uma combinação exata dos outros preditores neste recorte "
                "(por exemplo, Tributos é sempre a mesma fração da Receita), "
                "então não acrescenta informação."
            )

        if not mantidos:
            st.info("Nenhum preditor selecionado varia neste recorte.")
            return

        preditores = [preditores[i] for i in mantidos]
        modelo = ajustar_ols(y, X[:, mantidos])

        with st.container(key="reg_kpis"):
            k1, k2, k3, _ = st.columns([1, 1, 1, 0.6])
            with k1:
                _kpi(
                    "reg_kpi_r2",
                    "R² ajustado",
                    _num(modelo["r2_ajustado"]),
                    _qualidade_ajuste(modelo["r2_ajustado"]),
                )
            with k2:
                _kpi("reg_kpi_erro", "Erro médio", _moeda_mi(modelo["rmse"]), "RMSE")
            with k3:
                _kpi(
                    "reg_kpi_obs",
                    "Observações",
                    _num(len(recorte), 0),
                    "Cenários válidos" if ano != TODOS_OS_ANOS else "Cenários x anos válidos",
                )

        col_tabela, col_grafico = st.columns([1.55, 1], gap="medium")

        with col_tabela:
            with st.container(key="reg_coeficientes"):
                _tabela_coeficientes(preditores, modelo)

        with col_grafico:
            with st.container(key="reg_grafico"):
                _grafico(
                    y,
                    modelo["previsto"],
                    recorte["Cenario"].to_numpy(),
                    cenario,
                    dependente,
                )

        _insight(dependente, preditores, modelo)
