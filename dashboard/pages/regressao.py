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

# Acima disso o modelo é tratado como uma conta contábil (soma dos fatores)
LIMITE_CONTA_CONTABIL = 0.99

# Tolerância para considerar um cenário "bem previsto"
TOLERANCIA_ACERTO = 0.10

ICONES_STATUS = {
    "positivo": "✓",
    "atencao": "!",
    "negativo": "✕",
    "neutro": "i",
}

ICONE_ALERTA = "⚠️"

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

    /* selos de status */
    .reg-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        min-width: 24px;
        border-radius: 50%;
        font-size: 13px;
        font-weight: 800;
        line-height: 1;
    }

    .reg-badge--sm {
        width: 18px;
        height: 18px;
        min-width: 18px;
        font-size: 11px;
    }

    .reg-badge--positivo { background: #E6F6EE; color: #1F7A4F; }
    .reg-badge--atencao  { background: #FFF6DD; color: #9A6B00; }
    .reg-badge--negativo { background: #FDECEC; color: #B02A2A; }
    .reg-badge--neutro   { background: #E8F2FA; color: #1B6AA0; }

    /* KPIs */
    .reg-kpi-head {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 4px;
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
        font-size: 11.5px;
        color: #7C97B3;
        line-height: 1.45;
        margin-top: 2px;
    }

    /* faixa lateral e fundo conforme o status do KPI */
    [class*="st-key-reg_kpi_"]:has(.reg-st--positivo) { border-left: 4px solid #2E9E6B; }
    [class*="st-key-reg_kpi_"]:has(.reg-st--atencao)  { border-left: 4px solid #E0A100; background: #FFFDF5; }
    [class*="st-key-reg_kpi_"]:has(.reg-st--negativo) { border-left: 4px solid #D64545; background: #FFF9F9; }
    [class*="st-key-reg_kpi_"]:has(.reg-st--neutro)   { border-left: 4px solid #2585C5; }

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
        color: #7C97B3;
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
        align-items: center;
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
        color: #7C97B3;
    }

    .reg-barra-valor {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 700;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }

    .reg-sobe { color: #1F7A4F; }
    .reg-desce { color: #B02A2A; }

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
    .reg-barra-preenchida.reg-desce { background: #D64545; }

    .reg-peso,
    .reg-conf {
        display: inline-block;
        margin-top: 6px;
        margin-right: 6px;
        padding: 1px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
    }

    .reg-peso { background: #E8F2FA; color: #1B6AA0; }

    .reg-conf-alta { background: #E6F4EE; color: #1F7A57; }
    .reg-conf-media { background: #FFF4DB; color: #8A5A00; }
    .reg-conf-baixa { background: #F1F3F6; color: #5B6B7F; }

    .reg-aviso {
        font-size: 12px;
        line-height: 1.5;
        color: #7A5600;
        background: #FFF6DD;
        border: 1px solid #F1DDA0;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
    }

    .reg-destaque {
        font-size: 12px;
        color: var(--cti-text);
        background: #FFF7E8;
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 6px;
    }

    /* leitura automática do gráfico */
    .reg-insight {
        background: #fff;
        border: 1px solid #E3ECF5;
        border-left: 4px solid #2585C5;
        border-radius: 12px;
        padding: 14px 18px;
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        box-shadow: 0 2px 10px rgba(23, 59, 99, .04);
    }

    .reg-insight--positivo { border-left-color: #2E9E6B; }
    .reg-insight--atencao  { border-left-color: #E0A100; background: #FFFDF5; }
    .reg-insight--negativo { border-left-color: #D64545; background: #FFF9F9; }

    .reg-insight-head {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .reg-insight-title {
        font-size: 14px;
        font-weight: 700;
        color: #173B63;
    }

    .reg-insight-text {
        font-size: 13px;
        line-height: 1.6;
        color: #4A5E75;
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


def _html_seguro(texto):
    """Evita que o Markdown do Streamlit interprete R$ ... R$ como fórmula."""
    return str(texto).replace("$", "&#36;")


def _md(html):
    st.markdown(_html_seguro(html), unsafe_allow_html=True)


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


def _periodo_txt(ano):
    return "no conjunto de todos os anos" if ano == "Todos" else f"no Ano {ano}"


# ---------- Dados ----------

def _normalizar(df):
    """Garante Ano e Cenario como inteiros, mesmo que venham como 'Ano 3' ou '3.0'."""
    if (
        pd.api.types.is_integer_dtype(df["Ano"])
        and pd.api.types.is_integer_dtype(df["Cenario"])
    ):
        return df

    base = df.copy()

    base["Ano"] = pd.to_numeric(
        base["Ano"].astype(str).str.extract(r"(\d+)", expand=False),
        errors="coerce",
    )
    base["Cenario"] = pd.to_numeric(
        base["Cenario"].astype(str).str.extract(r"(\d+)(?:\.0+)?\s*$", expand=False),
        errors="coerce",
    )

    base = base.dropna(subset=["Ano", "Cenario"])
    base["Ano"] = base["Ano"].astype(int)
    base["Cenario"] = base["Cenario"].astype(int)

    return base


# ---------- Modelo ----------

def ajustar_ols(y, X):
    """Regressão linear por mínimos quadrados, com intercepto.

    Devolve um dict com coeficientes, erros padrão, p-valores, IC 95%,
    R² ajustado, RMSE (dentro da amostra), RMSE por validação leave-one-out
    (erro de previsão de verdade) e os valores previstos.
    """
    n, k = X.shape
    matriz = np.column_stack([np.ones(n), X])

    beta, *_ = np.linalg.lstsq(matriz, y, rcond=None)
    previsto = matriz @ beta
    residuos = y - previsto

    gl = n - k - 1
    sigma2 = residuos @ residuos / gl
    inversa = np.linalg.pinv(matriz.T @ matriz)
    erro_padrao = np.sqrt(np.diag(sigma2 * inversa))

    with np.errstate(divide="ignore", invalid="ignore"):
        t = beta / erro_padrao
    p = 2 * stats.t.sf(np.abs(t), gl)
    margem = stats.t.ppf(0.975, gl) * erro_padrao

    sq_total = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (residuos @ residuos) / sq_total
    r2_ajustado = 1 - (1 - r2) * (n - 1) / gl

    rmse = float(np.sqrt(residuos @ residuos / n))

    # Erro leave-one-out: cada cenário é previsto sem entrar no ajuste
    alavancagem = np.einsum("ij,jk,ik->i", matriz, inversa, matriz)
    denominador = 1 - alavancagem
    denominador = np.where(np.abs(denominador) < 1e-8, np.nan, denominador)

    with np.errstate(divide="ignore", invalid="ignore"):
        residuos_loo = residuos / denominador

    if np.isfinite(residuos_loo).any():
        rmse_cv = float(np.sqrt(np.nanmean(residuos_loo ** 2)))
    else:
        rmse_cv = rmse

    return {
        "coef": beta[1:],
        "erro_padrao": erro_padrao[1:],
        "p": p[1:],
        "ic_inf": (beta - margem)[1:],
        "ic_sup": (beta + margem)[1:],
        "r2_ajustado": r2_ajustado,
        "rmse": rmse,
        "rmse_cv": rmse_cv,
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


def calcular_regressao(df, ano):
    """Ajusta o modelo do ano, ou de todos os anos juntos (ano="Todos").

    Usado pela tela e pelo relatório em PDF.
    Devolve {"recorte", "y", "modelo", "fatores", "removidos"} ou {"erro": mensagem}.
    """
    base = _normalizar(df)

    nomes = list(FATORES)
    colunas = [VARIAVEIS[RESULTADO]] + [VARIAVEIS[n] for n in nomes]

    recorte = base if ano == "Todos" else base[base["Ano"] == ano]
    recorte = recorte[["Ano", "Cenario"] + colunas].dropna()

    if len(recorte) <= len(nomes) + 1:
        return {"erro": "Não há cenários suficientes com dados neste período para fazer a análise."}

    # Valores em R$ mi: deixa os números legíveis e o cálculo mais estável
    y = recorte[colunas[0]].to_numpy(dtype=float) / 1e6
    X = recorte[colunas[1:]].to_numpy(dtype=float) / 1e6

    # Proteção: um fator que não varia no período não entra no modelo
    mantidos, removidos = remover_colineares(X, nomes)
    if not mantidos:
        return {"erro": "Os fatores não variam neste período, então não há o que analisar."}

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

    return {
        "recorte": recorte,
        "y": y,
        "modelo": modelo,
        "fatores": fatores,
        "removidos": removidos,
    }


def texto_resposta(ano, fatores, modelo):
    """Título e texto da resposta principal da página."""
    explica = _num(max(modelo["r2_ajustado"], 0) * 100, 0)
    periodo = _periodo_txt(ano)
    total = sum(abs(f["impacto"]) for f in fatores) or 1

    # Procura entre TODOS os fatores, não só no de maior impacto
    significativos = [f for f in fatores if f["p"] < 0.05]

    if significativos:
        principal = significativos[0]
        direcao = "aumenta" if principal["impacto"] >= 0 else "diminui"
        peso = abs(principal["impacto"]) / total * 100

        if principal is fatores[0]:
            titulo = f"{principal['nome']} é o fator que mais pesa {periodo}."
        else:
            titulo = f"{principal['nome']} é o fator de efeito mais consistente {periodo}."

        texto = (
            f"Quando {principal['nome']} cresce {VARIACAO_IMPACTO:.0%}, a {RESULTADO} "
            f"{direcao}, em média, {_moeda_mi(abs(principal['impacto']))}. "
            f"Ele responde por {_num(peso, 0)}% do impacto somado dos fatores. "
            f"Os {len(fatores)} fatores juntos explicam {explica}% das diferenças "
            f"de {RESULTADO} entre os cenários."
        )

        if principal is not fatores[0]:
            texto += (
                f" {fatores[0]['nome']} tem o maior impacto bruto, mas sem "
                "confiança suficiente para afirmar o efeito."
            )
    else:
        titulo = f"Nenhum fator teve efeito consistente {periodo}."
        texto = (
            f"Neste recorte, os fatores analisados não mostram relação confiável "
            f"com a {RESULTADO}."
        )

    if modelo["r2_ajustado"] > LIMITE_CONTA_CONTABIL:
        texto += (
            f" Atenção: a {RESULTADO} é praticamente a soma desses fatores "
            "(uma conta contábil), por isso o modelo acerta quase tudo e o "
            "resultado não revela um efeito real."
        )

    return titulo, texto


def insight_ajuste(observado, previsto, cenarios, cenario, anos=None):
    """Leitura do gráfico "O modelo acerta?": (título, texto, status)."""
    observado = np.asarray(observado, dtype=float)
    previsto = np.asarray(previsto, dtype=float)
    cenarios = np.asarray(cenarios)

    n = len(observado)

    if n == 0:
        return None

    acertos = np.abs(observado - previsto) <= TOLERANCIA_ACERTO * np.abs(previsto) + 1e-9
    pct = acertos.mean() * 100

    unidade = "observações" if (anos is not None and len(set(anos)) > 1) else "cenários"

    texto = (
        f"{_num(pct, 0)}% dos {_num(n, 0)} {unidade} ficaram a até "
        f"{TOLERANCIA_ACERTO:.0%} do valor previsto."
    )

    if pct >= 80:
        status = "positivo"
    elif pct >= 50:
        status = "atencao"
    else:
        status = "negativo"

    if cenario != "Todos":
        sel = cenarios == cenario

        if sel.sum() == 1:
            real = float(observado[sel][0])
            prev = float(previsto[sel][0])
            dif = real - prev

            if abs(dif) < 1e-9:
                texto += f" O Cenário {cenario} ficou exatamente no previsto."
            else:
                posicao = "acima" if dif > 0 else "abaixo"
                rel = f" ({_num(abs(dif) / abs(prev) * 100, 1)}%)" if abs(prev) > 1e-9 else ""
                texto += (
                    f" O Cenário {cenario} ficou {posicao} do previsto: "
                    f"{_moeda_mi(abs(dif))}{rel}."
                )

        elif sel.sum() > 1:
            acima = int((observado[sel] > previsto[sel]).sum())
            texto += (
                f" O Cenário {cenario} ficou acima do previsto em {acima} "
                f"de {int(sel.sum())} anos."
            )

    return "Leitura do ajuste do modelo", texto, status


# ---------- Blocos da página ----------

def _cabecalho():
    st.markdown(f"""
        <div class="reg-eyebrow">PAINEL FINANCEIRO</div>
        <div class="reg-title">Regressão</div>
        <div class="reg-subtitle">
            O que mais influencia a {RESULTADO}? A análise compara os
            cenários simulados para responder.
        </div>
    """, unsafe_allow_html=True)


def _filtros(anos, cenarios):
    opcoes_ano = ["Todos"] + anos
    opcoes_cenario = ["Todos"] + cenarios

    with st.container(key="reg_filtros"):
        col_ano, col_cenario, _, col_botao = st.columns(
            [1.1, 1.3, 1.4, 1.1], gap="medium"
        )

        with col_ano:
            ano = st.selectbox(
                "Ano analisado",
                options=opcoes_ano,
                index=len(opcoes_ano) - 1,
                format_func=lambda a: "Todos os anos" if a == "Todos" else f"Ano {a}",
                key="reg_ano",
            )

        with col_cenario:
            cenario = st.selectbox(
                "Destacar cenário",
                options=opcoes_cenario,
                index=1 if cenarios else 0,
                format_func=lambda c: "Todos os cenários" if c == "Todos" else f"Cenário {c}",
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
    titulo, texto = texto_resposta(ano, fatores, modelo)

    ressalva = (
        "Mostra como os valores andam juntos nos cenários simulados; "
        "não prova causa e efeito."
    )

    if ano == "Todos":
        ressalva += (
            " Como cada cenário aparece uma vez por ano, as observações não "
            "são independentes e a confiança tende a ser maior do que a real."
        )

    # Linha única: no markdown, HTML recuado depois de linha em branco vira bloco de código
    _md(
        '<div class="reg-resposta"><span class="reg-resposta-icon">β</span><div>'
        '<div class="reg-resposta-eyebrow">RESPOSTA</div>'
        f'<div class="reg-resposta-titulo">{titulo}</div>'
        f'<p>{texto}<span class="reg-ressalva">{ressalva}</span></p>'
        "</div></div>"
    )


def _kpi(key, rotulo, valor, nota, status="neutro", icone=None):
    icone = icone or ICONES_STATUS[status]

    with st.container(key=key):
        _md(
            '<div class="reg-kpi-head">'
            f'<span class="reg-badge reg-badge--{status} reg-st reg-st--{status}">{icone}</span>'
            f'<span class="reg-kpi-label">{rotulo}</span>'
            "</div>"
            f'<div class="reg-kpi-value">{valor}</div>'
            f'<div class="reg-kpi-note">{nota}</div>'
        )


def _kpis(ano, recorte, y, modelo):
    """Os 3 cartões de resumo, com status e aviso de conta contábil."""
    r2 = modelo["r2_ajustado"]
    conta_contabil = r2 > LIMITE_CONTA_CONTABIL

    # --- Quanto o modelo explica ---
    if conta_contabil:
        status_r2 = "atencao"
        icone_r2 = ICONE_ALERTA
        nota_r2 = (
            f"Quase uma conta contábil: a {RESULTADO} é praticamente a soma dos fatores."
        )
    else:
        status_r2 = "positivo" if r2 >= 0.7 else "atencao" if r2 >= 0.4 else "negativo"
        icone_r2 = None
        nota_r2 = f"{_qualidade_ajuste(r2)} as diferenças de caixa entre os cenários"

    # --- Erro típico (validação leave-one-out) ---
    erro = modelo["rmse_cv"]
    media_y = float(np.mean(np.abs(y)))
    rel = erro / media_y if media_y > 1e-9 else np.nan

    if conta_contabil:
        status_erro = "atencao"
        icone_erro = ICONE_ALERTA
        nota_erro = "Erro baixo porque o modelo é quase uma identidade contábil."
    else:
        icone_erro = None

        if pd.isna(rel):
            status_erro = "neutro"
        elif rel < 0.10:
            status_erro = "positivo"
        elif rel < 0.25:
            status_erro = "atencao"
        else:
            status_erro = "negativo"

        if pd.isna(rel):
            nota_erro = "Diferença comum entre o caixa previsto e o real"
        else:
            nota_erro = (
                f"≈ {_num(rel * 100, 0)}% da {RESULTADO} média. Calculado sem usar "
                "o próprio cenário no ajuste."
            )

    # --- Observações ---
    n = len(recorte)

    if ano == "Todos":
        rotulo_obs = "Observações analisadas"
        nota_obs = (
            f"{_num(recorte['Cenario'].nunique(), 0)} cenários em "
            f"{_num(recorte['Ano'].nunique(), 0)} anos, com dados completos"
        )
    else:
        rotulo_obs = "Cenários analisados"
        nota_obs = f"Com dados completos no Ano {ano}"

    if n < 30:
        status_obs = "atencao"
        icone_obs = ICONE_ALERTA
        nota_obs += ". Poucos casos: resultados menos estáveis."
    else:
        status_obs = "neutro"
        icone_obs = None

    k1, k2, k3 = st.columns(3, gap="medium")

    with k1:
        _kpi(
            "reg_kpi_r2",
            "Quanto o modelo explica",
            f"{_num(max(r2, 0) * 100, 0)}%",
            nota_r2,
            status_r2,
            icone_r2,
        )
    with k2:
        _kpi(
            "reg_kpi_erro",
            "Erro típico da previsão",
            f"± {_moeda_mi(erro)}",
            nota_erro,
            status_erro,
            icone_erro,
        )
    with k3:
        _kpi(
            "reg_kpi_obs",
            rotulo_obs,
            _num(n, 0),
            nota_obs,
            status_obs,
            icone_obs,
        )


def _impactos(fatores, removidos=None):
    total = sum(abs(f["impacto"]) for f in fatores) or 1
    maior = max(abs(f["impacto"]) for f in fatores) or 1
    itens = ""

    for f in fatores:
        sobe = f["impacto"] >= 0
        classe = "reg-sobe" if sobe else "reg-desce"
        estado = "positivo" if sobe else "negativo"
        icone = "✓" if sobe else "✕"
        largura = max(abs(f["impacto"]) / maior * 100, 2)
        participacao = abs(f["impacto"]) / total * 100
        rotulo, classe_conf = _confianca(f["p"])

        itens += (
            '<div class="reg-barra-item"><div class="reg-barra-topo">'
            f'<span class="reg-barra-nome">{f["nome"]}'
            f'<span class="reg-barra-desc">{FATORES[f["nome"]]}</span></span>'
            f'<span class="reg-barra-valor {classe}">'
            f'<span class="reg-badge reg-badge--sm reg-badge--{estado}">{icone}</span>'
            f'{_moeda_sinal(f["impacto"])}</span>'
            "</div>"
            f'<div class="reg-barra-trilho"><div class="reg-barra-preenchida {classe}" '
            f'style="width:{largura:.0f}%"></div></div>'
            f'<span class="reg-peso">{_num(participacao, 0)}% do impacto somado</span>'
            f'<span class="reg-conf reg-conf-{classe_conf}">{rotulo}</span></div>'
        )

    aviso = ""

    if removidos:
        lista = ", ".join(removidos)
        verbo = "não entrou" if len(removidos) == 1 else "não entraram"
        aviso = (
            f'<div class="reg-aviso">{ICONE_ALERTA} {lista} {verbo} na análise: '
            "é combinação exata dos outros fatores e não tem efeito próprio.</div>"
        )

    with st.container(key="reg_impactos"):
        _md(
            '<div class="reg-card-title">Impacto de cada fator</div>'
            f'<div class="reg-card-note">Quanto a {RESULTADO} muda se o fator crescer '
            f"{VARIACAO_IMPACTO:.0%} e os outros ficarem iguais. Verde aumenta o caixa, "
            "vermelho diminui.</div>"
            f"{aviso}{itens}"
        )


def _casas_eixo(minimo, maximo):
    amplitude = maximo - minimo

    if amplitude >= 20:
        return 0
    if amplitude >= 2:
        return 1
    return 2


def _rotulo_br(casas):
    """Rótulo de eixo no padrão brasileiro: 1.234,5 em vez de 1,234.5."""
    return (
        f"replace(replace(replace(format(datum.value, ',.{casas}f'), "
        "regexp(',', 'g'), '#'), regexp('\\\\.', 'g'), ','), regexp('#', 'g'), '.')"
    )


def _html_insight(titulo, texto, status):
    return (
        f'<div class="reg-insight reg-insight--{status}">'
        '<div class="reg-insight-head">'
        f'<span class="reg-badge reg-badge--{status}">{ICONES_STATUS[status]}</span>'
        f'<span class="reg-insight-title">{titulo}</span>'
        "</div>"
        f'<div class="reg-insight-text">{texto}</div>'
        "</div>"
    )


def _grafico(observado, previsto, cenarios, cenario_destacado, anos=None):
    dados = pd.DataFrame({
        "Real": observado,
        "Previsto": previsto,
        "Cenario": cenarios,
    })

    varios_anos = anos is not None and len(set(anos)) > 1

    if anos is not None:
        dados["Ano"] = np.asarray(anos)

    dados["Real_txt"] = [_moeda_mi(v) for v in dados["Real"]]
    dados["Previsto_txt"] = [_moeda_mi(v) for v in dados["Previsto"]]

    if cenario_destacado == "Todos":
        destaque = dados.iloc[0:0]
    else:
        destaque = dados[dados["Cenario"] == cenario_destacado]

    minimo = float(min(dados["Real"].min(), dados["Previsto"].min()))
    maximo = float(max(dados["Real"].max(), dados["Previsto"].max()))
    eixo = alt.Scale(domain=[minimo, maximo], nice=True, zero=False)

    tooltip = [alt.Tooltip("Cenario:Q", title="Cenário", format="d")]

    if varios_anos:
        tooltip.append(alt.Tooltip("Ano:Q", title="Ano", format="d"))

    tooltip += [
        alt.Tooltip("Real_txt:N", title="Real"),
        alt.Tooltip("Previsto_txt:N", title="Previsto"),
    ]

    rotulo = _rotulo_br(_casas_eixo(minimo, maximo))

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
        _md(
            '<div class="reg-card-title">O modelo acerta?</div>'
            '<div class="reg-card-note">Cada ponto é um cenário. Pontos perto da linha '
            "verde foram bem previstos.</div>"
        )
        st.altair_chart(grafico, use_container_width=True)

        if cenario_destacado == "Todos":
            texto = (
                "Todos os cenários, sem destaque individual. Escolha um cenário "
                "no filtro para marcá-lo no gráfico."
            )
        elif destaque.empty:
            texto = f"O Cenário {cenario_destacado} não tem dados completos neste período."
        elif len(destaque) == 1:
            real = float(destaque["Real"].iloc[0])
            previsto_cenario = float(destaque["Previsto"].iloc[0])
            texto = (
                f"● <b>Cenário {cenario_destacado}</b>: real {_moeda_mi(real)}, "
                f"previsto {_moeda_mi(previsto_cenario)}."
            )
        else:
            texto = (
                f"● <b>Cenário {cenario_destacado}</b>: {len(destaque)} anos "
                "destacados no gráfico. Passe o mouse para ver o ano de cada ponto."
            )

        _md(f'<div class="reg-destaque">{texto}</div>')

        leitura = insight_ajuste(
            dados["Real"].to_numpy(),
            dados["Previsto"].to_numpy(),
            dados["Cenario"].to_numpy(),
            cenario_destacado,
            anos,
        )

        if leitura:
            _md(_html_insight(*leitura))


def _ajuda(fatores, removidos=None):
    with st.container(key="reg_ajuda"):
        with st.expander("Como ler esta análise", icon=":material/menu_book:"):
            bullets = (
                f"- **Cada cenário simulado é uma observação.** A análise compara os "
                f"cenários do período escolhido para ver o que anda junto com a {RESULTADO}.\n"
                f"- **Impacto:** quanto a {RESULTADO} muda, em média, quando o fator cresce "
                f"{VARIACAO_IMPACTO:.0%} e os outros ficam iguais. Custos e Investimentos são "
                "saídas de dinheiro, então crescer significa gastar mais.\n"
                "- **Participação no impacto:** quanto cada fator pesa no impacto somado "
                "dos fatores. Com muitos cenários, quase todo efeito aparece como "
                "confiável, então a participação ajuda a ver o que realmente pesa.\n"
                "- **Confiança:** alta quando o efeito aparece de forma consistente nos "
                "cenários; baixa quando pode ser só acaso.\n"
                "- **Quanto o modelo explica:** quanto das diferenças de caixa entre os "
                f"{len(fatores)} fatores analisados conseguem explicar juntos.\n"
                "- **Erro típico da previsão:** diferença comum entre o caixa previsto e o real, "
                "calculada prevendo cada cenário sem que ele participe do ajuste.\n"
                "- **Conta contábil:** quando o modelo explica quase 100%, a Geração de Caixa "
                "é praticamente a soma dos fatores. Nesse caso o acerto é aritmético, não "
                "um efeito descoberto.\n"
                "- **Todos os anos:** junta os cenários de todos os anos. Cada cenário aparece "
                "uma vez por ano, então as observações não são independentes e a confiança "
                "tende a ser maior do que a real.\n"
                "- **Todos os cenários:** não destaca nenhum cenário em particular no gráfico.\n"
                "- A análise mostra **associação**, não prova que um fator **causa** o outro."
            )

            if removidos:
                bullets += (
                    f"\n- **Fator fora da análise:** {', '.join(removidos)} é combinação "
                    "exata dos outros fatores, por isso não entra no modelo."
                )

            st.markdown(bullets)

        with st.expander("Detalhes estatísticos", icon=":material/functions:"):
            linhas = "".join(
                f'<tr><td>{f["nome"]}</td>'
                f'<td>{_num(f["coef"])}</td>'
                f'<td>{_num(f["erro_padrao"])}</td>'
                f'<td>{_p_valor(f["p"])}</td>'
                f'<td>{_num(f["ic_inf"])} – {_num(f["ic_sup"])}</td></tr>'
                for f in fatores
            )

            _md(
                '<div class="reg-table-wrap"><table class="reg-table"><thead><tr>'
                "<th>Fator</th><th>Coeficiente</th><th>Erro padrão</th>"
                "<th>p-valor</th><th>IC 95%</th>"
                f"</tr></thead><tbody>{linhas}</tbody></table></div>"
                '<div class="reg-glossario">'
                "<b>Coeficiente:</b> variação da Geração de Caixa, em R$ mi, a cada +R$ 1 mi no fator.<br>"
                "<b>p-valor:</b> abaixo de 0,01 a confiança é alta; entre 0,01 e 0,05, média; "
                "acima de 0,05, baixa.<br>"
                "<b>IC 95%:</b> faixa em que o coeficiente verdadeiro provavelmente está.<br>"
                "Modelo: regressão linear múltipla (mínimos quadrados) entre os cenários do período, "
                "valores em R$ mi."
                "</div>"
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

        base = _normalizar(df)

        anos = sorted(base["Ano"].unique().tolist())
        cenarios = sorted(base["Cenario"].unique().tolist())

        if not anos or not cenarios:
            st.warning("A base do demonstrativo não tem anos ou cenários válidos.")
            return

        ano, cenario = _filtros(anos, cenarios)

        calculo = calcular_regressao(base, ano)
        if "erro" in calculo:
            st.warning(calculo["erro"])
            return

        recorte, y = calculo["recorte"], calculo["y"]
        modelo, fatores = calculo["modelo"], calculo["fatores"]
        removidos = calculo["removidos"]

        _resposta(ano, fatores, modelo)

        _kpis(ano, recorte, y, modelo)

        col_impactos, col_grafico = st.columns([1, 1], gap="medium")

        with col_impactos:
            _impactos(fatores, removidos)

        with col_grafico:
            _grafico(
                y,
                modelo["previsto"],
                recorte["Cenario"].to_numpy(),
                cenario,
                recorte["Ano"].to_numpy(),
            )

        _ajuda(fatores, removidos)