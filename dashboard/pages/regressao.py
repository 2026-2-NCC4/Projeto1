import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from data.load_data import carregar_demonstrativo

# Nome exibido -> coluna da base. Valores monetários são convertidos para R$ mi.
# (Também usado pelas páginas de Ranking e Insights.)
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

# A página responde a uma pergunta só, com os fatores do modelo da Entrega 2.
# Outras combinações da DRE viram contas contábeis (o modelo "explica" 100%)
# e confundiam mais do que ajudavam.
RESULTADO = "Geração de Caixa"
FATORES = {
    "Resultado Líquido": "lucro que sobra depois de todas as despesas e impostos",
    "Custos": "gastos para operar (saída de dinheiro)",
    "Investimentos": "dinheiro aplicado em obras e equipamentos (saída de dinheiro)",
}

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
        gap: 16px !important;
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

    /* cartões brancos */
    .st-key-reg_filtros,
    .st-key-reg_kpi_r2,
    .st-key-reg_kpi_erro,
    .st-key-reg_kpi_obs,
    .st-key-reg_impactos,
    .st-key-reg_grafico,
    .st-key-reg_ajuda {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 22px;
    }

    /* barra de filtros */
    .st-key-reg_filtros {
        padding: 14px 22px;
    }

    .st-key-reg_filtros [data-testid="stHorizontalBlock"] {
        align-items: flex-end;
    }

    .st-key-reg_filtros label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-reg_filtros [data-testid="stSelectbox"] [role="group"] {
        background: #F5F9FD !important;
        border: 1px solid #D5E3EE !important;
        border-radius: 10px !important;
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

    /* resposta em destaque */
    .reg-resposta {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        background: linear-gradient(135deg, #0B5FA5 0%, var(--cti-blue) 55%, #003563 100%);
        border-radius: 14px;
        box-shadow: 0 10px 26px rgba(0, 63, 117, .18);
        padding: 20px 24px;
        color: #fff;
    }

    .reg-resposta-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: rgba(255, 255, 255, .16);
        font-size: 18px;
        font-weight: 700;
    }

    .reg-resposta-eyebrow {
        font-size: 11px;
        letter-spacing: .12em;
        color: rgba(255, 255, 255, .7);
    }

    .reg-resposta-titulo {
        font-size: 18px;
        font-weight: 700;
        margin: 4px 0 6px;
    }

    .reg-resposta p {
        margin: 0;
        font-size: 13.5px;
        line-height: 1.6;
        color: rgba(255, 255, 255, .92);
    }

    .reg-resposta .reg-ressalva {
        display: block;
        margin-top: 8px;
        font-size: 11.5px;
        color: rgba(255, 255, 255, .7);
    }

    /* KPIs */
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
        font-size: 11.5px;
        color: #8AA4BF;
        line-height: 1.4;
    }

    /* cartões da mesma linha com a mesma altura */
    .st-key-reg_page [data-testid="stHorizontalBlock"]:has(.st-key-reg_impactos),
    .st-key-reg_page [data-testid="stHorizontalBlock"]:has(.st-key-reg_kpi_r2) {
        align-items: stretch;
    }

    .st-key-reg_page [data-testid="stColumn"]:has(.st-key-reg_impactos) > div,
    .st-key-reg_page [data-testid="stColumn"]:has(.st-key-reg_grafico) > div,
    .st-key-reg_page [data-testid="stColumn"]:has([class*="st-key-reg_kpi_"]) > div,
    .st-key-reg_page [data-testid="stLayoutWrapper"]:has(> .st-key-reg_impactos),
    .st-key-reg_page [data-testid="stLayoutWrapper"]:has(> .st-key-reg_grafico),
    .st-key-reg_page [data-testid="stLayoutWrapper"]:has(> [class*="st-key-reg_kpi_"]),
    .st-key-reg_impactos,
    .st-key-reg_grafico,
    [class*="st-key-reg_kpi_"] {
        height: 100%;
    }

    .reg-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
    }

    .reg-card-note {
        font-size: 12px;
        color: #8AA4BF;
        margin: 2px 0 14px;
        line-height: 1.5;
    }

    /* barras de impacto */
    .reg-barra-item {
        padding: 12px 0;
        border-bottom: 1px solid #EEF3F9;
    }

    .reg-barra-item:last-child {
        border-bottom: none;
    }

    .reg-barra-topo {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 6px;
    }

    .reg-barra-nome {
        font-size: 13px;
        font-weight: 700;
        color: var(--cti-text);
    }

    .reg-barra-desc {
        display: block;
        font-size: 11px;
        font-weight: 400;
        color: #8AA4BF;
    }

    .reg-barra-valor {
        font-size: 13px;
        font-weight: 700;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }

    .reg-sobe { color: #2E8B6A; }
    .reg-desce { color: #C2410C; }

    .reg-barra-trilho {
        height: 8px;
        border-radius: 999px;
        background: #EEF3F9;
        overflow: hidden;
    }

    .reg-barra-preenchida {
        height: 100%;
        border-radius: 999px;
    }

    .reg-barra-preenchida.reg-sobe { background: #3E9C7A; }
    .reg-barra-preenchida.reg-desce { background: #E07B4A; }

    .reg-conf {
        display: inline-block;
        margin-top: 6px;
        padding: 1px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
    }

    .reg-conf-alta { background: #E6F4EE; color: #1F7A57; }
    .reg-conf-media { background: #FFF4DB; color: #8A5A00; }
    .reg-conf-baixa { background: #F1F3F6; color: #5B6B7F; }

    .reg-destaque {
        font-size: 12px;
        color: var(--cti-text);
        background: #FFF7E8;
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 6px;
    }

    /* explicações no fim da página */
    .st-key-reg_ajuda {
        padding: 6px 14px;
    }

    .st-key-reg_ajuda [data-testid="stExpander"] details {
        border: none;
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
        padding: 10px 12px;
        border-bottom: 1px solid #EEF3F9;
        font-variant-numeric: tabular-nums;
    }

    .reg-table td:first-child {
        font-weight: 700;
    }

    .reg-glossario {
        font-size: 12px;
        color: var(--cti-muted);
        line-height: 1.6;
        margin-top: 10px;
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
        return "Confiança alta", "alta"
    if p < 0.05:
        return "Confiança média", "media"
    return "Confiança baixa", "baixa"


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

def _cabecalho():
    st.markdown(f"""
        <div class="reg-eyebrow">PAINEL FINANCEIRO</div>
        <div class="reg-title">Regressão</div>
        <div class="reg-subtitle">
            O que mais influencia a {RESULTADO}? A análise compara os 1.200
            cenários simulados de um ano para responder.
        </div>
    """, unsafe_allow_html=True)


def _filtros(anos, cenarios):
    with st.container(key="reg_filtros"):
        col_ano, col_cenario, _, col_botao = st.columns(
            [1.1, 1.3, 1.4, 1.1], gap="medium"
        )

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


def _resposta(ano, fatores, modelo):
    principal = fatores[0]
    explica = _num(max(modelo["r2_ajustado"], 0) * 100, 0)

    if principal["p"] < 0.05:
        direcao = "aumenta" if principal["impacto"] >= 0 else "diminui"
        titulo = f"{principal['nome']} é o fator que mais pesa no Ano {ano}."
        texto = (
            f"Quando {principal['nome']} cresce {VARIACAO_IMPACTO:.0%}, a {RESULTADO} "
            f"{direcao}, em média, {_moeda_mi(abs(principal['impacto']))}. "
            f"Os {len(fatores)} fatores juntos explicam {explica}% das diferenças "
            f"de {RESULTADO} entre os cenários."
        )
        if modelo["r2_ajustado"] > 0.99:
            texto += (
                f" Neste ano a {RESULTADO} é praticamente a soma desses fatores "
                "(uma conta contábil), por isso o modelo acerta quase tudo."
            )
    else:
        titulo = f"Nenhum fator teve efeito consistente no Ano {ano}."
        texto = (
            f"Neste ano, os fatores analisados não mostram relação confiável "
            f"com a {RESULTADO}."
        )

    # Linha única: no markdown, HTML recuado depois de linha em branco vira bloco de código
    st.markdown(
        '<div class="reg-resposta"><span class="reg-resposta-icon">β</span><div>'
        '<div class="reg-resposta-eyebrow">RESPOSTA</div>'
        f'<div class="reg-resposta-titulo">{titulo}</div>'
        f"<p>{texto}<span class=\"reg-ressalva\">Mostra como os valores andam juntos "
        "nos cenários simulados; não prova causa e efeito.</span></p>"
        "</div></div>",
        unsafe_allow_html=True,
    )


def _kpi(key, rotulo, valor, nota):
    with st.container(key=key):
        st.markdown(
            f'<div class="reg-kpi-label">{rotulo}</div>'
            f'<div class="reg-kpi-value">{valor}</div>'
            f'<div class="reg-kpi-note">{nota}</div>',
            unsafe_allow_html=True,
        )


def _impactos(fatores):
    maior = max(abs(f["impacto"]) for f in fatores) or 1
    itens = ""

    for f in fatores:
        classe = "reg-sobe" if f["impacto"] >= 0 else "reg-desce"
        seta = "▲" if f["impacto"] >= 0 else "▼"
        largura = max(abs(f["impacto"]) / maior * 100, 2)
        rotulo, classe_conf = _confianca(f["p"])
        itens += (
            '<div class="reg-barra-item"><div class="reg-barra-topo">'
            f'<span class="reg-barra-nome">{f["nome"]}'
            f'<span class="reg-barra-desc">{FATORES[f["nome"]]}</span></span>'
            f'<span class="reg-barra-valor {classe}">{seta} {_moeda_sinal(f["impacto"])}</span>'
            "</div>"
            f'<div class="reg-barra-trilho"><div class="reg-barra-preenchida {classe}" '
            f'style="width:{largura:.0f}%"></div></div>'
            f'<span class="reg-conf reg-conf-{classe_conf}">{rotulo}</span></div>'
        )

    with st.container(key="reg_impactos"):
        st.markdown(
            '<div class="reg-card-title">Impacto de cada fator</div>'
            f'<div class="reg-card-note">Quanto a {RESULTADO} muda se o fator crescer '
            f"{VARIACAO_IMPACTO:.0%} e os outros ficarem iguais. Verde aumenta o caixa, "
            "laranja diminui.</div>"
            f"{itens}",
            unsafe_allow_html=True,
        )


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

    pontos = alt.Chart(dados).mark_circle(size=30, opacity=0.5, color="#4A90D9").encode(
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

    grafico = alt.layer(*camadas).properties(height=280).configure_axis(
        grid=False,
        labelColor="#55799F",
        titleColor="#55799F",
        titleFontWeight=500,
        domainColor="#C3D9F2",
        tickColor="#C3D9F2",
    ).configure_view(strokeWidth=0)

    with st.container(key="reg_grafico"):
        st.markdown(
            '<div class="reg-card-title">O modelo acerta?</div>'
            '<div class="reg-card-note">Cada ponto é um cenário. Pontos perto da linha '
            "verde foram bem previstos.</div>",
            unsafe_allow_html=True,
        )
        st.altair_chart(grafico, use_container_width=True)

        if destaque.empty:
            texto = f"O Cenário {cenario_destacado} não tem dados completos neste ano."
        else:
            real = float(destaque["Real"].iloc[0])
            previsto_cenario = float(destaque["Previsto"].iloc[0])
            texto = (
                f"● <b>Cenário {cenario_destacado}</b>: real {_moeda_mi(real)}, "
                f"previsto {_moeda_mi(previsto_cenario)}."
            )
        st.markdown(f'<div class="reg-destaque">{texto}</div>', unsafe_allow_html=True)


def _ajuda(fatores):
    with st.container(key="reg_ajuda"):
        with st.expander("Como ler esta análise", icon=":material/menu_book:"):
            st.markdown(
                f"- **Cada cenário simulado é uma observação.** A análise compara os "
                f"1.200 cenários do ano escolhido para ver o que anda junto com a {RESULTADO}.\n"
                f"- **Impacto:** quanto a {RESULTADO} muda, em média, quando o fator cresce "
                f"{VARIACAO_IMPACTO:.0%} e os outros ficam iguais. Custos e Investimentos são "
                "saídas de dinheiro, então crescer significa gastar mais.\n"
                "- **Confiança:** alta quando o efeito aparece de forma consistente nos "
                "cenários; baixa quando pode ser só acaso.\n"
                "- **Quanto o modelo explica:** quanto das diferenças de caixa entre os "
                "cenários os três fatores conseguem explicar juntos.\n"
                "- A análise mostra **associação**, não prova que um fator **causa** o outro."
            )

        with st.expander("Detalhes estatísticos", icon=":material/functions:"):
            linhas = "".join(
                f'<tr><td>{f["nome"]}</td>'
                f'<td>{_num(f["coef"])}</td>'
                f'<td>{_num(f["erro_padrao"])}</td>'
                f'<td>{_p_valor(f["p"])}</td>'
                f'<td>{_num(f["ic_inf"])} – {_num(f["ic_sup"])}</td></tr>'
                for f in fatores
            )

            st.markdown(
                '<div class="reg-table-wrap"><table class="reg-table"><thead><tr>'
                "<th>Fator</th><th>Coeficiente</th><th>Erro padrão</th>"
                "<th>p-valor</th><th>IC 95%</th>"
                f"</tr></thead><tbody>{linhas}</tbody></table></div>"
                '<div class="reg-glossario">'
                "<b>Coeficiente:</b> variação da Geração de Caixa, em R$ mi, a cada +R$ 1 mi no fator.<br>"
                "<b>p-valor:</b> abaixo de 0,01 a confiança é alta; entre 0,01 e 0,05, média; "
                "acima de 0,05, baixa.<br>"
                "<b>IC 95%:</b> faixa em que o coeficiente verdadeiro provavelmente está.<br>"
                "Modelo: regressão linear múltipla (mínimos quadrados) entre os cenários do ano, "
                "valores em R$ mi."
                "</div>",
                unsafe_allow_html=True,
            )


# ---------- Página principal ----------

def render_regressao():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="reg_page"):
        _cabecalho()

        try:
            df = carregar_demonstrativo()
        except Exception as erro:
            st.error(f"Não foi possível carregar a base do demonstrativo: {erro}")
            return

        anos = sorted(df["Ano"].dropna().astype(int).unique().tolist())
        cenarios = sorted(df["Cenario"].dropna().astype(int).unique().tolist())

        ano, cenario = _filtros(anos, cenarios)

        nomes = list(FATORES)
        colunas = [VARIAVEIS[RESULTADO]] + [VARIAVEIS[n] for n in nomes]
        recorte = df[df["Ano"] == ano][["Cenario"] + colunas].dropna()

        if len(recorte) <= len(nomes) + 1:
            st.warning("Não há cenários suficientes com dados neste ano para fazer a análise.")
            return

        # Valores em R$ mi: deixa os números legíveis e o cálculo mais estável
        y = recorte[colunas[0]].to_numpy(dtype=float) / 1e6
        X = recorte[colunas[1:]].to_numpy(dtype=float) / 1e6

        # Proteção: um fator que não varia no ano não entra no modelo
        mantidos, _ = remover_colineares(X, nomes)
        if not mantidos:
            st.warning("Os fatores não variam neste ano, então não há o que analisar.")
            return

        modelo = ajustar_ols(y, X[:, mantidos])

        fatores = sorted(
            (
                {
                    "nome": nomes[i],
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

        _resposta(ano, fatores, modelo)

        k1, k2, k3 = st.columns(3, gap="medium")
        with k1:
            _kpi(
                "reg_kpi_r2",
                "Quanto o modelo explica",
                f"{_num(max(modelo['r2_ajustado'], 0) * 100, 0)}%",
                f"{_qualidade_ajuste(modelo['r2_ajustado'])} as diferenças de caixa "
                "entre os cenários",
            )
        with k2:
            _kpi(
                "reg_kpi_erro",
                "Erro típico da previsão",
                f"± {_moeda_mi(modelo['rmse'])}",
                "Diferença comum entre o caixa previsto e o real",
            )
        with k3:
            _kpi(
                "reg_kpi_obs",
                "Cenários analisados",
                _num(len(recorte), 0),
                f"Com dados completos no Ano {ano}",
            )

        col_impactos, col_grafico = st.columns([1, 1], gap="medium")

        with col_impactos:
            _impactos(fatores)

        with col_grafico:
            _grafico(y, modelo["previsto"], recorte["Cenario"].to_numpy(), cenario)

        _ajuda(fatores)
