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

# O impacto de cada fator é mostrado como "se ele crescer 10%": assim fatores
# de escalas diferentes ficam comparáveis, sem falar em coeficientes.
VARIACAO_IMPACTO = 0.10

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
    .st-key-reg_impactos,
    .st-key-reg_grafico {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
    }

    .st-key-reg_filtros {
        padding: 14px 22px;
    }

    .st-key-reg_filtros [data-testid="stHorizontalBlock"] {
        align-items: flex-start;
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
        line-height: 1.4;
    }

    .reg-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
    }

    .reg-card-note {
        font-size: 11.5px;
        color: #8AA4BF;
        margin: 2px 0 12px;
    }

    .reg-table-wrap {
        overflow-x: auto;
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

    .reg-table td {
        white-space: nowrap;
        padding: 12px;
        border-bottom: 1px solid #EEF3F9;
        font-variant-numeric: tabular-nums;
    }

    .reg-table td:first-child {
        font-weight: 700;
    }

    .reg-sobe { color: #2E8B6A; font-weight: 600; }
    .reg-desce { color: #C2410C; font-weight: 600; }

    .reg-conf {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 600;
    }

    .reg-conf-alta { background: #E6F4EE; color: #1F7A57; }
    .reg-conf-media { background: #FFF4DB; color: #8A5A00; }
    .reg-conf-baixa { background: #F1F3F6; color: #5B6B7F; }

    .reg-chart-note {
        font-size: 11.5px;
        color: #8AA4BF;
        margin-top: 4px;
    }

    .reg-destaque {
        font-size: 12px;
        color: var(--cti-text);
        background: #FFF7E8;
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 8px;
    }

    .reg-glossario {
        font-size: 12px;
        color: var(--cti-muted);
        line-height: 1.6;
        margin-top: 10px;
    }

    .reg-insight {
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

    .reg-insight strong {
        display: block;
        margin-bottom: 2px;
    }

    .reg-insight p {
        margin: 0;
        line-height: 1.6;
    }

    .reg-insight .reg-alerta {
        display: block;
        margin-top: 6px;
        color: #8A5A00;
        font-size: 12px;
    }

    .reg-insight .reg-ressalva {
        display: block;
        margin-top: 6px;
        color: var(--cti-muted);
        font-size: 11.5px;
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


def _moeda_sinal(valor):
    """'+R$ 12,30 mi' / '−R$ 12,30 mi'."""
    return ("+" if valor >= 0 else "−") + _moeda_mi(abs(valor))


def _p_valor(p):
    # Vai dentro de HTML, então o "<" precisa ser escapado
    return "&lt; 0,001" if p < 0.001 else _num(p, 3)


def _qualidade_ajuste(r2):
    if r2 >= 0.7:
        return "Explica bem"
    if r2 >= 0.4:
        return "Explica em parte"
    return "Explica pouco"


def _confianca(p):
    """Traduz o p-valor para quem não é da estatística."""
    if p < 0.01:
        return "Alta", "alta"
    if p < 0.05:
        return "Média", "media"
    return "Baixa", "baixa"


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
                    Descubra quais fatores mais influenciam um resultado financeiro
                    nos 1.200 cenários simulados.
                </div>
            """, unsafe_allow_html=True)

        with col_ano:
            ano = st.selectbox(
                "Ano analisado",
                options=anos,
                index=len(anos) - 1,
                format_func=lambda a: f"Ano {a}",
                key="reg_ano",
            )

        with col_cenario:
            cenario = st.selectbox(
                "Destacar cenário",
                options=cenarios,
                format_func=lambda c: f"Cenário {c}",
                key="reg_cenario",
                help="Mostra onde esse cenário aparece no gráfico Previsto × Real.",
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
        col_dep, col_pred = st.columns([1.2, 4])

        with col_dep:
            dependente = st.selectbox(
                "1. O que você quer explicar?",
                options=list(VARIAVEIS),
                index=list(VARIAVEIS).index(DEPENDENTE_PADRAO),
                key="reg_dependente",
            )

        opcoes = [nome for nome in VARIAVEIS if nome != dependente]

        with col_pred:
            # A key muda com a escolha anterior para não manter um fator
            # que deixou de ser opção válida.
            preditores = st.pills(
                "2. Quais fatores podem influenciar esse resultado?",
                options=opcoes,
                selection_mode="multi",
                default=[p for p in PREDITORES_PADRAO if p in opcoes],
                key=f"reg_preditores_{dependente}",
            )

    return dependente, list(preditores or [])


def _como_ler():
    with st.expander("Como ler esta análise", icon=":material/menu_book:"):
        st.markdown(
            "- **Cada cenário simulado é uma observação.** A análise compara os "
            "1.200 cenários do ano escolhido para ver o que anda junto com o resultado.\n"
            "- **Impacto de cada fator:** quanto o resultado muda, em média, quando "
            "o fator cresce 10% e os outros fatores ficam iguais. Para Custos, Tributos "
            "e Investimentos, que são saídas de dinheiro, crescer significa gastar mais.\n"
            "- **Confiança:** indica se o efeito é consistente nos dados (Alta) "
            "ou se pode ser só acaso (Baixa).\n"
            "- **Previsto × Real:** quanto mais perto da linha verde estiverem os "
            "pontos, melhor o modelo acerta.\n"
            "- A análise mostra **associação**, não prova que um fator **causa** o outro."
        )


def _kpi(key, rotulo, valor, nota):
    with st.container(key=key):
        st.markdown(f"""
            <div class="reg-kpi-label">{rotulo}</div>
            <div class="reg-kpi-value">{valor}</div>
            <div class="reg-kpi-note">{nota}</div>
        """, unsafe_allow_html=True)


def _tabela_impactos(dependente, fatores):
    linhas = ""

    for fator in fatores:
        classe = "reg-sobe" if fator["impacto"] >= 0 else "reg-desce"
        seta = "▲" if fator["impacto"] >= 0 else "▼"
        rotulo, classe_conf = _confianca(fator["p"])
        # Linha única: no markdown, HTML recuado depois de linha em branco vira bloco de código
        linhas += (
            f'<tr><td>{fator["nome"]}</td>'
            f'<td><span class="{classe}">{seta} {_moeda_sinal(fator["impacto"])}</span></td>'
            f'<td><span class="reg-conf reg-conf-{classe_conf}">{rotulo}</span></td></tr>'
        )

    st.markdown(f"""
        <div class="reg-card-title">Impacto de cada fator</div>
        <div class="reg-card-note">
            Quanto {dependente} muda, em média, se o fator crescer
            {VARIACAO_IMPACTO:.0%} e os demais ficarem iguais.
            Do maior para o menor impacto.
        </div>
        <div class="reg-table-wrap">
        <table class="reg-table">
            <thead>
                <tr>
                    <th>Fator</th>
                    <th>Se o fator crescer {VARIACAO_IMPACTO:.0%}…</th>
                    <th>Confiança</th>
                </tr>
            </thead>
            <tbody>{linhas}</tbody>
        </table>
        </div>
    """, unsafe_allow_html=True)


def _detalhes_tecnicos(fatores):
    with st.expander("Ver detalhes estatísticos"):
        linhas = "".join(
            f'<tr><td>{f["nome"]}</td>'
            f'<td>{_num(f["coef"])}</td>'
            f'<td>{_num(f["erro_padrao"])}</td>'
            f'<td>{_p_valor(f["p"])}</td>'
            f'<td>{_num(f["ic_inf"])} – {_num(f["ic_sup"])}</td></tr>'
            for f in fatores
        )

        st.markdown(f"""
            <div class="reg-table-wrap">
            <table class="reg-table">
                <thead>
                    <tr>
                        <th>Fator</th>
                        <th>Coeficiente</th>
                        <th>Erro padrão</th>
                        <th>p-valor</th>
                        <th>IC 95%</th>
                    </tr>
                </thead>
                <tbody>{linhas}</tbody>
            </table>
            </div>
            <div class="reg-glossario">
                <b>Coeficiente:</b> variação do resultado, em R$ mi, a cada +R$ 1 mi no fator.<br>
                <b>p-valor:</b> chance de o efeito ser só acaso. Abaixo de 0,01 a confiança é
                Alta; entre 0,01 e 0,05, Média; acima de 0,05, Baixa.<br>
                <b>IC 95%:</b> faixa em que o coeficiente verdadeiro provavelmente está.<br>
                Modelo: regressão linear múltipla (mínimos quadrados), valores em R$ mi.
            </div>
        """, unsafe_allow_html=True)


def _grafico(observado, previsto, cenarios, cenario_destacado):
    dados = pd.DataFrame({
        "Real": observado,
        "Previsto": previsto,
        "Cenario": cenarios,
    })

    destaque = dados[dados["Cenario"] == cenario_destacado]

    minimo = float(min(dados["Real"].min(), dados["Previsto"].min()))
    maximo = float(max(dados["Real"].max(), dados["Previsto"].max()))
    eixo = alt.Scale(domain=[minimo, maximo], nice=True, zero=False)
    tooltip = [
        alt.Tooltip("Cenario:Q", title="Cenário"),
        alt.Tooltip("Real:Q", format=",.1f", title="Real (R$ mi)"),
        alt.Tooltip("Previsto:Q", format=",.1f", title="Previsto (R$ mi)"),
    ]

    # Rótulos no padrão brasileiro: 1.234 em vez de 1,234
    rotulo = "replace(format(datum.value, ',.0f'), ',', '.')"

    pontos = alt.Chart(dados).mark_circle(size=34, opacity=0.55, color="#4A90D9").encode(
        x=alt.X("Previsto:Q", scale=eixo, title="Previsto (R$ mi)",
                axis=alt.Axis(labelExpr=rotulo, tickCount=5)),
        y=alt.Y("Real:Q", scale=eixo, title="Real (R$ mi)",
                axis=alt.Axis(labelExpr=rotulo, tickCount=5)),
        tooltip=tooltip,
    )

    linha = alt.Chart(
        pd.DataFrame({"Previsto": [minimo, maximo], "Real": [minimo, maximo]})
    ).mark_line(color="#3E9C7A", strokeWidth=1.5).encode(x="Previsto:Q", y="Real:Q")

    camadas = [linha, pontos]

    if not destaque.empty:
        camadas.append(
            alt.Chart(destaque).mark_circle(
                size=150, color="#F59E0B", stroke="#fff", strokeWidth=2, opacity=1
            ).encode(x="Previsto:Q", y="Real:Q", tooltip=tooltip)
        )

    grafico = alt.layer(*camadas).properties(height=300).configure_axis(
        grid=False,
        labelColor="#55799F",
        titleColor="#55799F",
        titleFontWeight=500,
        domainColor="#C3D9F2",
        tickColor="#C3D9F2",
    ).configure_view(strokeWidth=0)

    st.markdown("""
        <div class="reg-card-title">Previsto × Real</div>
        <div class="reg-card-note">
            Cada ponto é um cenário. Perto da linha verde, o modelo acertou.
        </div>
    """, unsafe_allow_html=True)
    st.altair_chart(grafico, use_container_width=True)

    if destaque.empty:
        st.markdown(
            f'<div class="reg-chart-note">O Cenário {cenario_destacado} não tem dados '
            "completos neste ano.</div>",
            unsafe_allow_html=True,
        )
    else:
        real = float(destaque["Real"].iloc[0])
        previsto_cenario = float(destaque["Previsto"].iloc[0])
        st.markdown(
            f'<div class="reg-destaque">● <b>Cenário {cenario_destacado}</b>: '
            f"real {_moeda_mi(real)}, previsto {_moeda_mi(previsto_cenario)} "
            f"(diferença de {_moeda_mi(abs(real - previsto_cenario))}).</div>",
            unsafe_allow_html=True,
        )


def _resumo(dependente, fatores, modelo):
    principal = fatores[0]
    rotulo, _ = _confianca(principal["p"])

    if principal["p"] < 0.05:
        direcao = "aumenta" if principal["impacto"] >= 0 else "diminui"
        texto = (
            f"<strong>{principal['nome']} é o fator que mais pesa.</strong>"
            f"Se {principal['nome']} crescer {VARIACAO_IMPACTO:.0%}, {dependente} "
            f"{direcao} cerca de {_moeda_mi(abs(principal['impacto']))}, com confiança "
            f"{rotulo.lower()}. Juntos, os fatores escolhidos explicam "
            f"{_num(max(modelo['r2_ajustado'], 0) * 100, 0)}% das diferenças de "
            f"{dependente} entre os cenários."
        )
    else:
        texto = (
            "<strong>Nenhum fator teve efeito consistente.</strong>"
            f"Os fatores escolhidos não mostram relação confiável com {dependente} "
            "neste ano. Experimente outros fatores."
        )

    alerta = ""
    if modelo["r2_ajustado"] > 0.99:
        alerta = (
            '<span class="reg-alerta">⚠ O modelo explica quase 100%. Isso costuma '
            f"acontecer quando {dependente} é calculado diretamente a partir dos fatores "
            "escolhidos (uma conta contábil). Nesse caso o resultado confirma a conta, "
            "mas não revela uma relação nova.</span>"
        )

    ressalva = (
        '<span class="reg-ressalva">A análise mostra associação entre os valores dos '
        "cenários simulados, não prova de causa e efeito.</span>"
    )

    # Tudo numa linha: sem alerta, uma linha vazia faria o markdown virar código
    st.markdown(
        f'<div class="reg-insight"><span class="reg-insight-icon">β</span>'
        f"<p>{texto}{alerta}{ressalva}</p></div>",
        unsafe_allow_html=True,
    )


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
        _como_ler()

        if not preditores:
            st.info("Escolha pelo menos um fator no passo 2 para ver a análise.")
            return

        colunas = [VARIAVEIS[dependente]] + [VARIAVEIS[p] for p in preditores]
        recorte = df[df["Ano"] == ano][["Cenario"] + colunas].dropna()

        if len(recorte) <= len(preditores) + 1:
            st.warning("Não há cenários suficientes com dados neste ano para fazer a análise.")
            return

        # Valores em R$ mi: deixa os números legíveis e o cálculo mais estável
        y = recorte[colunas[0]].to_numpy(dtype=float) / 1e6
        X = recorte[colunas[1:]].to_numpy(dtype=float) / 1e6

        mantidos, removidos = remover_colineares(X, preditores)

        if removidos:
            plural = len(removidos) > 1
            st.info(
                f"{' e '.join(removidos)} {'ficaram' if plural else 'ficou'} fora da análise: "
                f"{'repetem' if plural else 'repete'} a informação de outro fator escolhido "
                "(por exemplo, os Tributos são sempre a mesma porcentagem da Receita).",
                icon=":material/info:",
            )

        if not mantidos:
            st.info("Os fatores escolhidos não variam neste ano. Escolha outros fatores.")
            return

        modelo = ajustar_ols(y, X[:, mantidos])

        fatores = sorted(
            (
                {
                    "nome": preditores[i],
                    "coef": modelo["coef"][j],
                    "erro_padrao": modelo["erro_padrao"][j],
                    "p": modelo["p"][j],
                    "ic_inf": modelo["ic_inf"][j],
                    "ic_sup": modelo["ic_sup"][j],
                    "impacto": modelo["coef"][j] * VARIACAO_IMPACTO * X[:, i].mean(),
                }
                for j, i in enumerate(mantidos)
            ),
            key=lambda f: abs(f["impacto"]),
            reverse=True,
        )

        with st.container(key="reg_kpis"):
            k1, k2, k3 = st.columns(3)
            with k1:
                _kpi(
                    "reg_kpi_r2",
                    "Quanto o modelo explica",
                    f"{_num(max(modelo['r2_ajustado'], 0) * 100, 0)}%",
                    f"{_qualidade_ajuste(modelo['r2_ajustado'])} as diferenças de "
                    f"{dependente} entre os cenários",
                )
            with k2:
                _kpi(
                    "reg_kpi_erro",
                    "Erro típico da previsão",
                    f"± {_moeda_mi(modelo['rmse'])}",
                    "Diferença comum entre o valor previsto e o real",
                )
            with k3:
                _kpi(
                    "reg_kpi_obs",
                    "Cenários analisados",
                    _num(len(recorte), 0),
                    f"Todos com dados completos no Ano {ano}",
                )

        col_tabela, col_grafico = st.columns([1.3, 1], gap="medium")

        with col_tabela:
            with st.container(key="reg_impactos"):
                _tabela_impactos(dependente, fatores)
                _detalhes_tecnicos(fatores)

        with col_grafico:
            with st.container(key="reg_grafico"):
                _grafico(y, modelo["previsto"], recorte["Cenario"].to_numpy(), cenario)

        _resumo(dependente, fatores, modelo)
