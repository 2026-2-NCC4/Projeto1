import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from data.load_data import carregar_demonstrativo, carregar_indicadores


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
    "ROE": ("indicadores", "ROE", "Rentabilidade", "percentual", "maior"),
    "ROE DuPont": ("indicadores", "ROE DuPont", "Rentabilidade", "percentual", "maior"),
    "DuPont - Margem Líquida": ("indicadores", "DuPont - Margem Líquida", "Rentabilidade", "percentual", "maior"),
    "DuPont - Giro do Ativo": ("indicadores", "DuPont - Giro do Ativo", "Rentabilidade", "multiplo", "maior"),
    "DuPont - Alavancagem": ("indicadores", "DuPont - Alavancagem", "Rentabilidade", "multiplo", "menor"),
    "CCL": ("indicadores", "CCL", "Capital de giro", "moeda", "maior"),
    "PMR": ("indicadores", "PMR", "Capital de giro", "dias", "menor"),
    "PMP": ("indicadores", "PMP", "Capital de giro", "dias", "maior"),
    "Ciclo Financeiro": ("indicadores", "Ciclo Financeiro", "Capital de giro", "dias", "menor"),
    "Necessidade de Capital de Giro": ("indicadores", "Necessidade de Capital de Giro", "Capital de giro", "moeda", "menor"),
    "Taxa de Conversão da Receita em Caixa": ("indicadores", "Taxa de Conversão da Receita em Caixa", "Fluxo de caixa", "percentual", "maior"),
    "FCO": ("indicadores", "FCO", "Fluxo de caixa", "moeda", "maior"),
    "FCO / EBITDA": ("indicadores", "FCO / EBITDA", "Fluxo de caixa", "multiplo", "maior"),
    "FCO / Lucro Líquido": ("indicadores", "FCO / Lucro Líquido", "Fluxo de caixa", "multiplo", "maior"),
    "FCL": ("indicadores", "FCL", "Fluxo de caixa", "moeda", "maior"),
    "Investimentos / Receita": ("indicadores", "Investimentos / Receita", "Investimentos", "percentual", "menor"),
    "Investimentos / Depreciação": ("indicadores", "Investimentos / Depreciação", "Investimentos", "multiplo", "maior"),
    "Cobertura de Juros": ("indicadores", "Cobertura de Juros", "Cobertura", "multiplo", "maior"),
    "FCO / Dívida Bruta": ("indicadores", "FCO / Dívida Bruta", "Cobertura", "percentual", "maior"),
    "Distribuição / Lucro Líquido": ("indicadores", "Distribuição / Lucro Líquido", "Distribuição", "percentual", "menor"),
    "Cobertura de Dividendos": ("indicadores", "Cobertura de Dividendos", "Distribuição", "multiplo", "maior"),
}


PAGE_STYLE = """
<style>

.st-key-tend_page {
    padding: 28px 32px 40px;
    gap: 20px !important;
}

/* ---------- Cabeçalho (mesmo padrão de Indicadores) ---------- */
.tend-eyebrow {
    color: var(--cti-blue);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.tend-title {
    color: var(--cti-text);
    font-size: 30px;
    font-weight: 750;
    line-height: 1.15;
    margin: 0 0 7px 0;
}
.tend-subtitle {
    color: var(--cti-muted);
    font-size: 13px;
    margin-bottom: 8px;
}
.tend-section-title {
    color: #173B63;
    font-size: 18px;
    font-weight: 750;
    margin: 4px 0 3px 0;
}
.tend-section-subtitle {
    color: #8293A7;
    font-size: 12.5px;
    margin-bottom: 14px;
}

/* ---------- Cards das seções ---------- */
.st-key-tend_filtros,
.st-key-tend_evolucao,
.st-key-tend_variacao,
.st-key-tend_distribuicao,
.st-key-tend_comparacao,
.st-key-tend_ajuda {
    background: #FFFFFF;
    border: 1px solid #E1ECF7;
    border-radius: 16px;
    box-shadow: 0 3px 14px rgba(0,55,100,.06);
    padding: 22px 24px;
}

.st-key-tend_filtros {
    padding: 18px 22px;
}

.st-key-tend_filtros label p {
    font-size: 14px !important;
    color: #49647E !important;
}

.st-key-tend_page p,
.st-key-tend_page label,
.st-key-tend_page .stCaption {
    font-size: 14px;
}

.st-key-tend_page h1,
.st-key-tend_page h2,
.st-key-tend_page h3 {
    color: #173B63;
}

/* ---------- Selos e chips de status ---------- */
.tend-badge {
    width: 26px;
    height: 26px;
    min-width: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    line-height: 1;
}
.tend-badge--sm {
    width: 20px;
    height: 20px;
    min-width: 20px;
    font-size: 11px;
}
.tend-badge--positivo { background: #E6F6EE; color: #1F7A4F; }
.tend-badge--atencao  { background: #FFF6DD; color: #9A6B00; }
.tend-badge--negativo { background: #FDECEC; color: #B02A2A; }
.tend-badge--neutro   { background: #E8F2FA; color: #1B6AA0; }

.tend-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0 0 14px 0;
}
.tend-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 1px solid #E3ECF5;
    border-radius: 999px;
    padding: 5px 14px 5px 6px;
    font-size: 13px;
    font-weight: 650;
    background: #FFFFFF;
    color: #4A5E75;
}
.tend-chip--negativo { background: #FDECEC; border-color: #F3C6C6; color: #8F2222; }
.tend-chip--atencao  { background: #FFF6DD; border-color: #F1DDA0; color: #7A5600; }
.tend-chip--positivo { background: #E6F6EE; border-color: #BFE3D0; color: #19623F; }
.tend-chip--neutro   { background: #F4F8FC; border-color: #E1ECF7; color: #4A5E75; }

/* ---------- Cards de resumo (KPIs) ---------- */
.tend-kpi {
    background: #FFFFFF;
    border: 1px solid #E1ECF7;
    border-left: 4px solid #2585C5;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(0,75,133,.05);
    min-height: 158px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: all 0.2s ease;
}
.tend-kpi:hover {
    box-shadow: 0 6px 18px rgba(23, 59, 99, 0.10);
    transform: translateY(-2px);
}
.tend-kpi--positivo { border-left-color: #2E9E6B; }
.tend-kpi--atencao  { border-left-color: #E0A100; background: #FFFDF5; }
.tend-kpi--negativo { border-left-color: #D64545; background: #FFF9F9; }
.tend-kpi--neutro   { border-left-color: #2585C5; }

.tend-kpi-head {
    display: flex;
    align-items: center;
    gap: 10px;
}
.tend-kpi-label {
    color: #718096;
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .6px;
    line-height: 1.3;
}
.tend-kpi-value {
    color: #173B63;
    font-size: 24px;
    font-weight: 750;
    line-height: 1.2;
}
.tend-kpi-note {
    color: #8293A7;
    font-size: 12.5px;
    line-height: 1.45;
}

/* ---------- Insights e alertas ---------- */
.tend-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr));
    gap: 14px;
    align-items: stretch;
}
.tend-insight {
    background: #FFFFFF;
    border: 1px solid #E3ECF5;
    border-left: 4px solid #2585C5;
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 14px;
    box-shadow: 0 3px 12px rgba(23, 59, 99, 0.05);
}
.tend-grid .tend-insight { margin-top: 0; }
.tend-insight--positivo { border-left-color: #2E9E6B; }
.tend-insight--atencao  { border-left-color: #E0A100; background: #FFFDF5; }
.tend-insight--negativo { border-left-color: #D64545; background: #FFF9F9; }
.tend-insight--neutro   { border-left-color: #2585C5; }

.tend-insight-head {
    display: flex;
    align-items: center;
    gap: 10px;
}
.tend-insight-title {
    color: #173B63;
    font-size: 15px;
    font-weight: 750;
    line-height: 1.3;
}
.tend-insight-text {
    color: #4A5E75;
    font-size: 14px;
    line-height: 1.65;
}

/* ---------- Legenda do gráfico de distribuição ---------- */
.tend-key {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 18px;
    margin: 6px 0 4px 0;
    font-size: 13px;
    color: #4A5E75;
}
.tend-key-item {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}
.tend-swatch {
    display: inline-block;
    width: 22px;
    height: 0;
    border-top: 3px solid;
}
.tend-swatch--dash { border-top-style: dashed; }
.tend-swatch--band {
    height: 12px;
    border-top: 0;
    border-radius: 3px;
}

</style>
"""


# Escala de exibição por unidade: (fator, rótulo do eixo)
ESCALAS = {
    "moeda": (1 / 1_000_000, "R$ mi"),
    "percentual": (100, "%"),
    "multiplo": (1, "x"),
    "dias": (1, "dias"),
}

FORMATO_EIXO = ",.2~f"

# Troca o padrão americano (1,234.5) pelo brasileiro (1.234,5) nos rótulos dos eixos
LABEL_BR = (
    "replace(replace(replace(datum.label, regexp(',', 'g'), '#'), "
    "regexp('\\\\.', 'g'), ','), regexp('#', 'g'), '.')"
)

ICONES_STATUS = {
    "positivo": "✓",
    "atencao": "!",
    "negativo": "✕",
    "neutro": "i",
}

ICONE_ALERTA = "⚠️"

# Variação anual (em módulo) a partir da qual o resumo sinaliza atenção
LIMITE_OSCILACAO = 0.30


# ======================================================================
# Formatação
# ======================================================================

def _numero(valor, casas=2):

    if pd.isna(valor):
        return "—"

    texto = (
        f"{abs(float(valor)):,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"−{texto}" if float(valor) < 0 else texto


def _formatar(valor, unidade):

    if pd.isna(valor):
        return "—"

    if unidade == "moeda":

        mi = float(valor) / 1_000_000

        if abs(mi) >= 1000:
            return f"R$ {_numero(mi / 1000)} bi"

        return f"R$ {_numero(mi)} mi"

    if unidade == "percentual":
        return f"{_numero(valor * 100)}%"

    if unidade == "multiplo":
        return f"{_numero(valor)}x"

    if unidade == "dias":
        return f"{_numero(valor, 1)} dias"

    return _numero(valor)


def _pct_br(valor, casas=1):

    if pd.isna(valor):
        return "—"

    sinal = "+" if valor >= 0 else "−"

    return f"{sinal}{_numero(abs(valor) * 100, casas)}%"


def _escala(unidade):

    return ESCALAS.get(unidade, (1, ""))


def _titulo_eixo(nome, unidade):

    _, rotulo = _escala(unidade)

    return f"{nome} ({rotulo})" if rotulo else nome


def _html_seguro(texto):
    """Evita que o Markdown do Streamlit interprete R$ ... R$ como fórmula."""
    return str(texto).replace("$", "&#36;")


# ======================================================================
# Componentes visuais (HTML)
# ======================================================================

def _titulo_secao(titulo, subtitulo=None):

    st.markdown(
        f'<div>'
        f'<div class="tend-section-title">{titulo}</div>'
        f'<div class="tend-section-subtitle">{subtitulo or ""}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def _html_insight(titulo, texto, status="neutro", icone=None):

    icone = icone or ICONES_STATUS[status]

    return (
        f'<div class="tend-insight tend-insight--{status}">'
        f'<div class="tend-insight-head">'
        f'<span class="tend-badge tend-badge--{status}">{icone}</span>'
        f'<span class="tend-insight-title">{_html_seguro(titulo)}</span>'
        f'</div>'
        f'<div class="tend-insight-text">{_html_seguro(texto)}</div>'
        f'</div>'
    )


def _mostrar_insight(insight):

    if not insight:
        return

    titulo, texto, status = insight

    st.markdown(
        _html_insight(titulo, texto, status),
        unsafe_allow_html=True
    )


def _html_chip(status, texto, icone=None):

    icone = icone or ICONES_STATUS[status]

    return (
        f'<span class="tend-chip tend-chip--{status}">'
        f'<span class="tend-badge tend-badge--sm tend-badge--{status}">'
        f'{icone}</span>{_html_seguro(texto)}</span>'
    )


def _kpi(coluna, titulo, valor, nota, status="neutro", icone=None):

    icone = icone or ICONES_STATUS[status]

    with coluna:

        st.markdown(
            f'<div class="tend-kpi tend-kpi--{status}">'
            f'<div class="tend-kpi-head">'
            f'<span class="tend-badge tend-badge--{status}">{icone}</span>'
            f'<span class="tend-kpi-label">{titulo}</span>'
            f'</div>'
            f'<div class="tend-kpi-value">{_html_seguro(valor)}</div>'
            f'<div class="tend-kpi-note">{_html_seguro(nota)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ======================================================================
# Dados
# ======================================================================

def _carregar_indicador(nome):

    fonte, coluna, _, _, _ = INDICADORES[nome]

    df = (
        carregar_demonstrativo()
        if fonte == "demonstrativo"
        else carregar_indicadores()
    )

    faltantes = {"Ano", "Cenario", coluna}.difference(df.columns)

    if faltantes:
        raise ValueError(
            f"Colunas ausentes na fonte de {nome}: "
            f"{', '.join(sorted(faltantes))}"
        )

    if fonte == "indicadores" and "Ano_Numero" in df.columns:

        dados = df[
            ["Ano", "Ano_Numero", "Cenario", coluna]
        ].copy()

        dados["Ano"] = pd.to_numeric(
            dados["Ano_Numero"],
            errors="coerce"
        )

    else:

        dados = df[
            ["Ano", "Cenario", coluna]
        ].copy()

        dados["Ano"] = pd.to_numeric(
            dados["Ano"].astype(str).str.extract(
                r"(\d+)",
                expand=False
            ),
            errors="coerce"
        )

    dados["Cenario"] = pd.to_numeric(
        dados["Cenario"].astype(str).str.extract(
            r"(\d+)(?:\.0+)?\s*$",
            expand=False
        ),
        errors="coerce"
    )

    dados["Valor"] = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    )

    dados = dados.dropna(
        subset=["Ano", "Cenario", "Valor"]
    )

    dados["Ano"] = dados["Ano"].astype(int)
    dados["Cenario"] = dados["Cenario"].astype(int)


    dados = (
        dados.groupby(
            ["Ano", "Cenario"],
            as_index=False
        )["Valor"]
        .mean()
        .sort_values(["Ano", "Cenario"])
    )

    return dados


def _resumo_anual(dados):

    return (
        dados.groupby("Ano")["Valor"]
        .agg(
            Media="mean",
            Mediana="median",
            P10=lambda s: s.quantile(.10),
            P25=lambda s: s.quantile(.25),
            P75=lambda s: s.quantile(.75),
            P90=lambda s: s.quantile(.90),
            Minimo="min",
            Maximo="max",
            Cenarios="count"
        )
        .reset_index()
        .sort_values("Ano")
    )


def _variacoes(resumo):

    df = resumo[["Ano", "Media"]].copy()

    anterior = df["Media"].shift(1)

    # abs() no denominador: com base negativa, ir de -100 para -50 é melhora (+50%)
    df["Variacao"] = (df["Media"] - anterior) / anterior.abs()

    df.loc[
        anterior.abs() < 1e-12,
        "Variacao"
    ] = np.nan

    return df


def _alertas(resumo, variacoes):

    alertas = []
    analisou = False

    validas = variacoes.dropna()


    if len(validas) >= 4:

        analisou = True

        mediana = validas["Variacao"].median()

        mad = (
            validas["Variacao"] - mediana
        ).abs().median()

        limite = max(3 * 1.4826 * mad, .10)

        for _, linha in validas.iterrows():

            if abs(linha["Variacao"] - mediana) > limite:

                alertas.append((
                    "warning",
                    "Oscilação fora do padrão histórico",
                    (
                        f"No Ano {int(linha['Ano'])}, a variação "
                        f"da média foi {_pct_br(linha['Variacao'])}, "
                        "distante do comportamento habitual."
                    )
                ))


    temp = resumo.copy()

    temp["Dispersao"] = (
        (temp["P90"] - temp["P10"])
        / temp["Media"].abs().replace(0, np.nan)
    )

    serie = (
        temp["Dispersao"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if len(serie) >= 4:

        analisou = True

        q1 = serie.quantile(.25)
        q3 = serie.quantile(.75)

        limite = q3 + 1.5 * (q3 - q1)

        for _, linha in temp.dropna(
            subset=["Dispersao"]
        ).iterrows():

            if linha["Dispersao"] > limite:

                alertas.append((
                    "warning",
                    "Alta dispersão entre cenários",
                    (
                        f"No Ano {int(linha['Ano'])}, a faixa "
                        f"P10–P90 equivale a "
                        f"{_numero(linha['Dispersao'] * 100, 1)}% da média, "
                        "acima do padrão histórico."
                    )
                ))

    if not alertas:

        if not analisou:

            return [(
                "info",
                "Período curto demais para gerar alertas",
                (
                    "Os alertas precisam de pelo menos 4 anos de dados "
                    "(5 para detectar oscilações). Amplie o período "
                    "analisado para habilitá-los."
                )
            )]

        return [(
            "info",
            "Nenhum sinal estatístico relevante identificado",
            (
                "Os critérios aplicados não identificaram "
                "oscilações ou dispersões incomuns no período selecionado."
            )
        )]

    return alertas


# ======================================================================
# Insights (leituras automáticas)
# ======================================================================

def insight_evolucao(dados, resumo, cenario, unidade, direcao):
    """Leitura da evolução histórica: (título, texto, status) ou None."""

    validos = resumo.dropna(subset=["Media"])

    if len(validos) < 2:
        return None

    ini = validos.iloc[0]
    fim = validos.iloc[-1]

    a0, a1 = int(ini["Ano"]), int(fim["Ano"])
    v0, v1 = ini["Media"], fim["Media"]

    texto = (
        f"A média dos cenários passou de {_formatar(v0, unidade)} "
        f"(Ano {a0}) para {_formatar(v1, unidade)} (Ano {a1})"
    )

    status = "neutro"

    if abs(v0) > 1e-12:

        var = (v1 - v0) / abs(v0)

        texto += f", variação de {_pct_br(var)}"

        if abs(var) >= .005:

            favoravel = (var > 0) == (direcao == "maior")

            status = "positivo" if favoravel else "negativo"

    texto += "."

    sc = (
        dados.loc[dados["Cenario"] == cenario]
        .set_index("Ano")["Valor"]
    )

    med = resumo.set_index("Ano")["Media"]

    comum = sc.index.intersection(med.index)

    if len(comum):

        acima = int((sc[comum] > med[comum]).sum())

        texto += (
            f" O Cenário {cenario} ficou acima da média em {acima} "
            f"de {len(comum)} anos e terminou em "
            f"{_formatar(sc[comum.max()], unidade)}."
        )

    texto += (
        f" No Ano {a1}, 80% dos cenários ficaram entre "
        f"{_formatar(fim['P10'], unidade)} e {_formatar(fim['P90'], unidade)}."
    )

    return "Leitura da evolução histórica", texto, status


def insight_variacao(variacoes, direcao):
    """Leitura da variação anual: (título, texto, status) ou None."""

    vv = variacoes.dropna(subset=["Variacao"])

    if vv.empty:
        return None

    n = len(vv)
    altas = int((vv["Variacao"] > 0).sum())
    quedas = int((vv["Variacao"] < 0).sum())

    maior_alta = vv.loc[vv["Variacao"].idxmax()]
    maior_queda = vv.loc[vv["Variacao"].idxmin()]

    texto = f"A média subiu em {altas} de {n} anos e caiu em {quedas}."

    if maior_alta["Variacao"] > 0:
        texto += (
            f" A maior alta foi {_pct_br(maior_alta['Variacao'])} "
            f"no Ano {int(maior_alta['Ano'])}"
        )
        texto += "."

    if maior_queda["Variacao"] < 0:
        texto += (
            f" A maior queda foi {_pct_br(maior_queda['Variacao'])} "
            f"no Ano {int(maior_queda['Ano'])}."
        )

    if direcao == "maior":
        favoravel, adverso = altas > quedas, quedas > altas
    else:
        favoravel, adverso = quedas > altas, altas > quedas

    status = "positivo" if favoravel else "negativo" if adverso else "neutro"

    if vv["Variacao"].abs().max() >= 0.5:

        texto += " Oscilações dessa magnitude merecem atenção."

        if status != "negativo":
            status = "atencao"

    return "Leitura da variação anual", texto, status


def insight_distribuicao(dados, ano, unidade):
    """Leitura da distribuição dos cenários: (título, texto, status) ou None."""

    s = dados.loc[dados["Ano"] == ano, "Valor"].dropna()

    if len(s) < 2:
        return None

    media = s.mean()
    mediana = s.median()

    texto = (
        f"No Ano {ano}, 80% dos {len(s)} cenários ficaram entre "
        f"{_formatar(s.quantile(.10), unidade)} e "
        f"{_formatar(s.quantile(.90), unidade)}."
    )

    dif = (
        (media - mediana) / abs(mediana)
        if abs(mediana) > 1e-12 else 0
    )

    if dif > .05:

        texto += (
            " A média está acima da mediana: poucos cenários com valores "
            "altos puxam a média para cima."
        )

        status = "atencao" if dif > .20 else "neutro"

    elif dif < -.05:

        texto += (
            " A média está abaixo da mediana: poucos cenários com valores "
            "baixos puxam a média para baixo."
        )

        status = "atencao" if dif < -.20 else "neutro"

    else:

        texto += (
            " Média e mediana estão próximas: os cenários se distribuem "
            "de forma equilibrada."
        )

        status = "positivo"

    return "Leitura da distribuição", texto, status


# ======================================================================
# Gráficos
# ======================================================================

def _tema(grafico):

    return (
        grafico
        .configure_view(strokeWidth=0)
        .configure_axis(
            gridColor="#EDF2F7",
            labelColor="#526B83",
            titleColor="#294A68",
            labelFontSize=13,
            titleFontSize=14
        )
        .configure_legend(
            labelFontSize=13,
            titleFontSize=13
        )
    )


def _grafico_evolucao(dados, resumo, cenario, unidade=None):

    fator, _ = _escala(unidade)
    titulo_y = _titulo_eixo("Valor", unidade)

    eixo_y = alt.Axis(
        format=FORMATO_EIXO,
        labelExpr=LABEL_BR
    )

    destaque = dados.loc[
        dados["Cenario"] == cenario,
        ["Ano", "Valor"]
    ].copy()

    destaque["Série"] = "Cenário selecionado"

    media = resumo[
        ["Ano", "Media"]
    ].rename(
        columns={"Media": "Valor"}
    ).copy()

    media["Série"] = "Média dos cenários"

    linhas = pd.concat(
        [destaque, media],
        ignore_index=True
    )

    linhas["Plot"] = linhas["Valor"] * fator
    linhas["Texto"] = linhas["Valor"].map(
        lambda v: _formatar(v, unidade)
    )

    faixa_dados = resumo[["Ano", "P10", "P90"]].copy()

    faixa_dados["P10_plot"] = faixa_dados["P10"] * fator
    faixa_dados["P90_plot"] = faixa_dados["P90"] * fator
    faixa_dados["P10_txt"] = faixa_dados["P10"].map(
        lambda v: _formatar(v, unidade)
    )
    faixa_dados["P90_txt"] = faixa_dados["P90"].map(
        lambda v: _formatar(v, unidade)
    )

    faixa = alt.Chart(faixa_dados).mark_area(
        color="#8CBCE5",
        opacity=.25
    ).encode(
        x=alt.X("Ano:O", title="Ano", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("P10_plot:Q", title=titulo_y, axis=eixo_y),
        y2="P90_plot:Q",
        tooltip=[
            "Ano:O",
            alt.Tooltip("P10_txt:N", title="P10"),
            alt.Tooltip("P90_txt:N", title="P90")
        ]
    )

    linha = alt.Chart(linhas).mark_line(
        point=True,
        strokeWidth=3
    ).encode(
        x=alt.X("Ano:O", title="Ano", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Plot:Q", title=titulo_y, axis=eixo_y),
        color=alt.Color(
            "Série:N",
            title=None,
            scale=alt.Scale(
                domain=[
                    "Cenário selecionado",
                    "Média dos cenários"
                ],
                range=[
                    "#1680DB",
                    "#329879"
                ]
            )
        ),
        tooltip=[
            "Ano:O",
            "Série:N",
            alt.Tooltip("Texto:N", title="Valor")
        ]
    )

    titulo = alt.TitleParams(
        text="Área sombreada: faixa P10–P90 dos cenários",
        anchor="start",
        fontSize=13,
        fontWeight="normal",
        color="#526B83"
    )

    return _tema(
        (faixa + linha).properties(height=320, title=titulo)
    )


def _grafico_variacao(variacoes):

    dados = variacoes.dropna(
        subset=["Variacao"]
    ).copy()

    if dados.empty:
        return None

    dados["Sinal"] = np.where(
        dados["Variacao"] >= 0,
        "Positiva",
        "Negativa"
    )

    dados["Texto"] = dados["Variacao"].map(
        lambda v: _pct_br(v, 1)
    )

    x = alt.X("Ano:O", title="Ano", axis=alt.Axis(labelAngle=0))

    y = alt.Y(
        "Variacao:Q",
        title="Variação anual",
        axis=alt.Axis(format=".0%")
    )

    barras = (
        alt.Chart(dados)
        .mark_bar(
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        )
        .encode(
            x=x,
            y=y,
            color=alt.Color(
                "Sinal:N",
                scale=alt.Scale(
                    domain=["Positiva", "Negativa"],
                    range=["#329879", "#D92D20"]
                ),
                legend=None
            ),
            tooltip=[
                "Ano:O",
                alt.Tooltip("Texto:N", title="Variação")
            ]
        )
    )

    rotulos_pos = (
        alt.Chart(dados)
        .transform_filter(alt.datum.Variacao >= 0)
        .mark_text(dy=-8, fontSize=12, fontWeight="bold", color="#526B83")
        .encode(x=x, y=y, text="Texto:N")
    )

    rotulos_neg = (
        alt.Chart(dados)
        .transform_filter(alt.datum.Variacao < 0)
        .mark_text(dy=12, fontSize=12, fontWeight="bold", color="#526B83")
        .encode(x=x, y=y, text="Texto:N")
    )

    return _tema(
        (barras + rotulos_pos + rotulos_neg).properties(height=290)
    )


def _grafico_distribuicao(dados, ano, unidade=None):

    fator, _ = _escala(unidade)

    recorte = dados.loc[
        dados["Ano"] == ano,
        ["Valor"]
    ].dropna().copy()

    if recorte.empty:
        return None

    recorte["Plot"] = recorte["Valor"] * fator

    media = recorte["Plot"].mean()
    mediana = recorte["Plot"].median()
    p25 = recorte["Plot"].quantile(.25)
    p75 = recorte["Plot"].quantile(.75)

    titulo_x = _titulo_eixo("Faixas de valores", unidade)

    eixo_x = alt.Axis(
        format=FORMATO_EIXO,
        labelExpr=LABEL_BR
    )

    # faixa dos 50% centrais (P25–P75), atrás das barras
    faixa_central = alt.Chart(
        pd.DataFrame({"x1": [p25], "x2": [p75]})
    ).mark_rect(
        color="#16805D",
        opacity=.10
    ).encode(
        x=alt.X("x1:Q", title=titulo_x, axis=eixo_x),
        x2="x2:Q"
    )

    histograma = alt.Chart(recorte).mark_bar(
        color="#4C91C6",
        opacity=.85,
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        x=alt.X(
            "Plot:Q",
            bin=alt.Bin(maxbins=25),
            title=titulo_x,
            axis=eixo_x
        ),
        y=alt.Y(
            "count():Q",
            title="Quantidade de cenários"
        ),
        tooltip=[
            alt.Tooltip(
                "Plot:Q",
                bin=alt.Bin(maxbins=25),
                title="Faixa",
                format=FORMATO_EIXO
            ),
            alt.Tooltip(
                "count():Q",
                title="Quantidade de cenários"
            )
        ]
    )

    linha_media = alt.Chart(
        pd.DataFrame({"referencia": [media]})
    ).mark_rule(
        color="#D97706",
        strokeWidth=3,
        strokeDash=[6, 4]
    ).encode(
        x=alt.X("referencia:Q", title=titulo_x, axis=eixo_x)
    )

    linha_mediana = alt.Chart(
        pd.DataFrame({"referencia": [mediana]})
    ).mark_rule(
        color="#16805D",
        strokeWidth=3
    ).encode(
        x=alt.X("referencia:Q", title=titulo_x, axis=eixo_x)
    )

    return _tema(
        (
            faixa_central
            + histograma
            + linha_media
            + linha_mediana
        ).properties(height=300)
    )


def _legenda_distribuicao(dados, ano, unidade):
    """Legenda em HTML: média, mediana e faixa central, com os valores."""

    s = dados.loc[dados["Ano"] == ano, "Valor"].dropna()

    if s.empty:
        return ""

    media = s.mean()
    mediana = s.median()
    p25 = s.quantile(.25)
    p75 = s.quantile(.75)

    return _html_seguro(
        f'<div class="tend-key">'
        f'<span class="tend-key-item">'
        f'<span class="tend-swatch tend-swatch--dash" style="border-color:#D97706"></span>'
        f'<b>Média</b> {_formatar(media, unidade)}</span>'
        f'<span class="tend-key-item">'
        f'<span class="tend-swatch" style="border-color:#16805D"></span>'
        f'<b>Mediana</b> {_formatar(mediana, unidade)}</span>'
        f'<span class="tend-key-item">'
        f'<span class="tend-swatch tend-swatch--band" '
        f'style="background:rgba(22,128,93,.18)"></span>'
        f'<b>50% centrais</b> {_formatar(p25, unidade)} a {_formatar(p75, unidade)}</span>'
        f'</div>'
    )


def _grafico_comparacao(comparacao, nome_a, unidade_a, nome_b, unidade_b):
    """Duas linhas com eixos independentes (esquerda e direita)."""

    fator_a, _ = _escala(unidade_a)
    fator_b, _ = _escala(unidade_b)

    cor_a = "#1680DB"
    cor_b = "#329879"

    dados = comparacao.copy()

    dados["A_plot"] = dados["A"] * fator_a
    dados["B_plot"] = dados["B"] * fator_b
    dados["A_txt"] = dados["A"].map(lambda v: _formatar(v, unidade_a))
    dados["B_txt"] = dados["B"].map(lambda v: _formatar(v, unidade_b))

    base = alt.Chart(dados).encode(
        x=alt.X(
            "Ano:O",
            title="Ano",
            axis=alt.Axis(labelAngle=0)
        )
    )

    linha_a = base.mark_line(
        point=True,
        strokeWidth=3,
        color=cor_a
    ).encode(
        y=alt.Y(
            "A_plot:Q",
            title=_titulo_eixo(nome_a, unidade_a),
            axis=alt.Axis(
                format=FORMATO_EIXO,
                labelExpr=LABEL_BR,
                titleColor=cor_a,
                labelColor=cor_a
            )
        ),
        tooltip=[
            "Ano:O",
            alt.Tooltip("A_txt:N", title=nome_a)
        ]
    )

    linha_b = base.mark_line(
        point=True,
        strokeWidth=3,
        color=cor_b
    ).encode(
        y=alt.Y(
            "B_plot:Q",
            title=_titulo_eixo(nome_b, unidade_b),
            axis=alt.Axis(
                format=FORMATO_EIXO,
                labelExpr=LABEL_BR,
                orient="right",
                titleColor=cor_b,
                labelColor=cor_b
            )
        ),
        tooltip=[
            "Ano:O",
            alt.Tooltip("B_txt:N", title=nome_b)
        ]
    )

    return _tema(
        alt.layer(linha_a, linha_b)
        .resolve_scale(y="independent")
        .properties(height=280)
    )


# ======================================================================
# Resumo
# ======================================================================

def resumo_evolucao(resumo, variacoes, direcao, com_variacao=False):
    """CAGR, maior variação, melhor e pior ano (usado pela tela e pelo PDF).

    Devolve (cagr, maior_txt, melhor_txt, pior_txt); cagr pode ser NaN.
    Com com_variacao=True, melhor e pior ano trazem também a variação.
    """
    validos = resumo.dropna(
        subset=["Media"]
    )

    cagr = np.nan

    if len(validos) >= 2:

        inicial = validos.iloc[0]["Media"]
        final = validos.iloc[-1]["Media"]

        if inicial > 0 and final > 0:

            cagr = (
                (final / inicial)
                ** (1 / (len(validos) - 1))
            ) - 1

    vv = variacoes.dropna(
        subset=["Variacao"]
    )

    if vv.empty:
        return cagr, "—", "—", "—"

    maior = vv.loc[
        vv["Variacao"].abs().idxmax()
    ]

    melhor = vv.loc[
        vv["Variacao"].idxmax()
    ]

    pior = vv.loc[
        vv["Variacao"].idxmin()
    ]

    if direcao == "menor":
        melhor, pior = pior, melhor

    maior_txt = (
        f"{maior['Variacao']:+.1%} "
        f"· Ano {int(maior['Ano'])}"
    )

    if com_variacao:

        melhor_txt = (
            f"Ano {int(melhor['Ano'])} · {melhor['Variacao']:+.1%}"
        )

        pior_txt = (
            f"Ano {int(pior['Ano'])} · {pior['Variacao']:+.1%}"
        )

        return cagr, maior_txt, melhor_txt, pior_txt

    return cagr, maior_txt, f"Ano {int(melhor['Ano'])}", f"Ano {int(pior['Ano'])}"


def _kpis_resumo(resumo, variacoes, direcao):
    """Os 4 cartões do resumo: (título, valor, nota, status, ícone)."""

    cagr, maior_txt, melhor_txt, pior_txt = resumo_evolucao(
        resumo, variacoes, direcao, com_variacao=True
    )

    vv = variacoes.dropna(subset=["Variacao"])

    # CAGR: verde se evoluiu na direção boa do indicador, vermelho se não
    if pd.isna(cagr) or abs(cagr) < .0005:
        status_cagr = "neutro"
    else:
        favoravel = (cagr > 0) == (direcao == "maior")
        status_cagr = "positivo" if favoravel else "negativo"

    oscilacao_forte = (
        not vv.empty
        and vv["Variacao"].abs().max() >= LIMITE_OSCILACAO
    )

    if oscilacao_forte:
        status_maior = "atencao"
        icone_maior = ICONE_ALERTA
        nota_maior = (
            f"Oscilação acima de {int(LIMITE_OSCILACAO * 100)}%: "
            "vale investigar o que aconteceu nesse ano."
        )
    else:
        status_maior = "neutro"
        icone_maior = None
        nota_maior = "Maior oscilação percentual observada no período."

    tem_variacao = not vv.empty

    return [
        (
            "Crescimento médio anual (CAGR)",
            f"{cagr:+.1%}" if pd.notna(cagr) else "N/A",
            "Taxa composta de crescimento entre o primeiro e o último ano.",
            status_cagr,
            None
        ),
        (
            "Maior variação anual",
            maior_txt,
            nota_maior,
            status_maior,
            icone_maior
        ),
        (
            "Melhor ano",
            melhor_txt,
            "Considera a direção financeira do indicador.",
            "positivo" if tem_variacao else "neutro",
            None
        ),
        (
            "Pior ano",
            pior_txt,
            "Considera a direção financeira do indicador.",
            "negativo" if tem_variacao else "neutro",
            None
        ),
    ]


def _chip_alertas(alertas):
    """Chip de status dos alertas, mostrado no topo do resumo."""

    n = sum(1 for tipo, _, _ in alertas if tipo == "warning")

    if n > 0:

        texto = (
            f"{n} alerta detectado no período"
            if n == 1
            else f"{n} alertas detectados no período"
        )

        return _html_chip("negativo", texto, ICONE_ALERTA)

    if alertas and alertas[0][1].startswith("Período curto"):

        return _html_chip(
            "neutro",
            "Alertas indisponíveis: período curto demais",
            "i"
        )

    return _html_chip("positivo", "Nenhum alerta no período", "✓")


def _html_alertas(alertas):

    cards = []

    for tipo, titulo, texto in alertas[:6]:

        if tipo == "warning":
            cards.append(
                _html_insight(titulo, texto, "negativo", ICONE_ALERTA)
            )
        elif titulo.startswith("Nenhum"):
            cards.append(_html_insight(titulo, texto, "positivo"))
        else:
            cards.append(_html_insight(titulo, texto, "neutro"))

    return f'<div class="tend-grid">{"".join(cards)}</div>'


# ======================================================================
# Página
# ======================================================================

def render_tendencias():

    st.markdown(
        PAGE_STYLE,
        unsafe_allow_html=True
    )

    with st.container(key="tend_page"):


        st.markdown(
            """
            <div>
                <div class="tend-eyebrow">PAINEL FINANCEIRO</div>
                <div class="tend-title">Tendências</div>
                <div class="tend-subtitle">
                    Acompanhe a evolução histórica, a distribuição
                    dos cenários e os principais sinais de atenção.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


        nomes = list(INDICADORES)

        with st.container(key="tend_filtros"):

            f1, f2, f3, f4 = st.columns(
                [1, 1.2, 1.35, 1.35],
                gap="medium"
            )

            with f1:

                indicador = st.selectbox(
                    "Indicador principal",
                    nomes,
                    index=nomes.index("EBITDA"),
                    key="tend_indicador"
                )

            with f2:

                secundarias = (
                    ["Nenhum"]
                    + [n for n in nomes if n != indicador]
                )

                if (
                    st.session_state.get("tend_secundario")
                    not in secundarias
                ):
                    st.session_state["tend_secundario"] = "Nenhum"

                secundario = st.selectbox(
                    "Indicador secundário",
                    secundarias,
                    key="tend_secundario"
                )

            try:

                dados = _carregar_indicador(indicador)

            except Exception as erro:

                st.error(
                    f"Não foi possível carregar {indicador}: {erro}"
                )
                return

            if dados.empty:

                st.warning(
                    f"Não existem valores válidos para {indicador}."
                )
                return

            anos = sorted(
                dados["Ano"].unique().tolist()
            )

            cenarios = sorted(
                dados["Cenario"].unique().tolist()
            )

            with f3:

                periodo_atual = st.session_state.get("tend_periodo")

                if (
                    not isinstance(periodo_atual, (tuple, list))
                    or len(periodo_atual) != 2
                    or periodo_atual[0] not in anos
                    or periodo_atual[1] not in anos
                ):
                    st.session_state["tend_periodo"] = (anos[0], anos[-1])

                periodo = st.select_slider(
                    "Período analisado",
                    options=anos,
                    format_func=lambda ano: f"Ano {ano}",
                    key="tend_periodo"
                )

            with f4:

                if (
                    st.session_state.get("tend_cenario")
                    not in cenarios
                ):
                    st.session_state["tend_cenario"] = cenarios[0]

                cenario = st.selectbox(
                    "Destacar cenário",
                    cenarios,
                    format_func=lambda c: f"Cenário {c}",
                    key="tend_cenario"
                )


        dados = dados[
            dados["Ano"].between(
                periodo[0],
                periodo[1]
            )
        ].copy()

        if dados.empty:

            st.info(
                "Não há dados no período selecionado."
            )
            return

        resumo = _resumo_anual(dados)
        variacoes = _variacoes(resumo)
        alertas = _alertas(resumo, variacoes)

        _, _, _, unidade, direcao = INDICADORES[indicador]


        # ---------------- Resumo da evolução ----------------

        _titulo_secao(
            "Resumo da evolução",
            "Indicadores calculados com base na média anual "
            "dos cenários válidos."
        )

        st.markdown(
            f'<div class="tend-chips">{_chip_alertas(alertas)}</div>',
            unsafe_allow_html=True
        )

        k1, k2, k3, k4 = st.columns(
            4,
            gap="medium"
        )

        for coluna, (titulo, valor, nota, status, icone) in zip(
            (k1, k2, k3, k4),
            _kpis_resumo(resumo, variacoes, direcao)
        ):
            _kpi(coluna, titulo, valor, nota, status, icone)


        # ---------------- Evolução histórica ----------------

        with st.container(key="tend_evolucao"):

            _titulo_secao(
                "Evolução histórica e faixa dos cenários",
                "A linha destaca o cenário escolhido; a média resume "
                "os cenários disponíveis e a faixa mostra os percentis "
                "10 a 90."
            )

            st.altair_chart(
                _grafico_evolucao(
                    dados,
                    resumo,
                    cenario,
                    unidade
                ),
                use_container_width=True
            )

            _mostrar_insight(
                insight_evolucao(
                    dados, resumo, cenario, unidade, direcao
                )
            )

            with st.expander(
                "Entenda a faixa P10–P90",
                expanded=False
            ):

                st.markdown("**P10 — 10º percentil**")

                st.write(
                    "10% dos cenários apresentam valores iguais "
                    "ou inferiores a esse ponto."
                )

                st.markdown("**P90 — 90º percentil**")

                st.write(
                    "90% dos cenários apresentam valores iguais "
                    "ou inferiores a esse ponto."
                )

                st.markdown(
                    "**O que significa a faixa P10–P90?**"
                )

                st.write(
                    "Ela representa os 80% centrais dos cenários. "
                    "É útil para visualizar a variação dos resultados "
                    "sem deixar que valores extremos dominem a análise."
                )


        # ---------------- Variação anual e distribuição ----------------

        col_var, col_dist = st.columns(
            2,
            gap="medium"
        )

        with col_var:

            with st.container(key="tend_variacao"):

                _titulo_secao(
                    "Variação anual",
                    "Variação percentual da média dos cenários "
                    "em relação ao ano anterior."
                )

                graf = _grafico_variacao(variacoes)

                if graf is None:

                    st.info(
                        "Não há anos consecutivos suficientes "
                        "para calcular a variação."
                    )

                else:

                    st.altair_chart(
                        graf,
                        use_container_width=True
                    )

                    _mostrar_insight(
                        insight_variacao(variacoes, direcao)
                    )

        with col_dist:

            with st.container(key="tend_distribuicao"):

                _titulo_secao(
                    "Distribuição dos cenários",
                    "Veja como os resultados dos cenários estão "
                    "concentrados em diferentes faixas de valores."
                )

                anos_disponiveis = sorted(
                    dados["Ano"].unique()
                )

                if (
                    st.session_state.get("tend_ano_dist")
                    not in anos_disponiveis
                ):
                    st.session_state["tend_ano_dist"] = anos_disponiveis[-1]

                ano_dist = st.selectbox(
                    "Ano da distribuição",
                    anos_disponiveis,
                    format_func=lambda a: f"Ano {a}",
                    key="tend_ano_dist"
                )

                distribuicao = _grafico_distribuicao(
                    dados,
                    ano_dist,
                    unidade
                )

                if distribuicao is None:

                    st.info(
                        "Não há dados disponíveis para este ano."
                    )

                else:

                    st.altair_chart(
                        distribuicao,
                        use_container_width=True
                    )

                    st.markdown(
                        _legenda_distribuicao(dados, ano_dist, unidade),
                        unsafe_allow_html=True
                    )

                    quantidade = dados.loc[
                        dados["Ano"] == ano_dist,
                        "Valor"
                    ].count()

                    st.caption(
                        f"{quantidade:,} cenários com dados válidos."
                        .replace(",", ".")
                    )

                    _mostrar_insight(
                        insight_distribuicao(dados, ano_dist, unidade)
                    )


        # ---------------- Alertas ----------------

        _titulo_secao(
            "Alertas automáticos",
            "Sinais estatísticos do período selecionado. "
            "Não são previsões."
        )

        st.markdown(
            _html_alertas(alertas),
            unsafe_allow_html=True
        )

        if len(alertas) > 6:

            st.caption(
                f"Mostrando os 6 primeiros de {len(alertas)} alertas."
            )


        # ---------------- Comparação ----------------

        if secundario != "Nenhum":

            try:

                sec = _carregar_indicador(secundario)

                sec = sec[
                    sec["Ano"].between(
                        periodo[0],
                        periodo[1]
                    )
                ]

                sec_resumo = _resumo_anual(sec)

                _, _, _, unidade_sec, _ = INDICADORES[secundario]

                comparacao = (
                    resumo[["Ano", "Media"]]
                    .rename(columns={"Media": "A"})
                    .merge(
                        sec_resumo[["Ano", "Media"]].rename(
                            columns={"Media": "B"}
                        ),
                        on="Ano",
                        how="inner"
                    )
                )

                with st.container(key="tend_comparacao"):

                    if comparacao.empty:

                        _titulo_secao(
                            f"Comparação de médias anuais: "
                            f"{indicador} e {secundario}"
                        )

                        st.info(
                            "Os dois indicadores não têm anos em comum "
                            "no período selecionado."
                        )

                    else:

                        _titulo_secao(
                            f"Comparação de médias anuais: "
                            f"{indicador} e {secundario}",
                            "Cada indicador tem seu próprio eixo e sua "
                            "unidade original: o da esquerda é do "
                            "primeiro e o da direita, do segundo. "
                            "Compare principalmente a direção das tendências."
                        )

                        st.altair_chart(
                            _grafico_comparacao(
                                comparacao,
                                indicador,
                                unidade,
                                secundario,
                                unidade_sec
                            ),
                            use_container_width=True
                        )

            except Exception as erro:

                st.warning(
                    f"Não foi possível carregar o indicador secundário: {erro}"
                )


        # ---------------- Ajuda ----------------

        with st.container(key="tend_ajuda"):

            with st.expander(
                "Como interpretar esta tela"
            ):

                st.markdown(
                    """
                    - **Média dos cenários:** média dos valores válidos de cada ano.
                    - **P10:** valor abaixo ou igual ao de 10% dos cenários.
                    - **P90:** valor abaixo ou igual ao de 90% dos cenários.
                    - **Faixa P10–P90:** representa os 80% centrais dos resultados.
                    - **Histograma:** mostra a quantidade de cenários em cada faixa de valores.
                    - **Média e mediana:** ajudam a comparar o centro da distribuição e identificar possíveis assimetrias.
                    - **Variação anual:** mudança percentual da média em relação ao ano anterior.
                    - **Alertas:** identificam oscilações e dispersões incomuns em relação ao histórico. São sinais para investigação, não previsões.
                    - **Cores dos cards:** verde é favorável, amarelo pede atenção, vermelho é crítico e azul é informativo. Nos indicadores em que menor é melhor (como WACC e prazos), a cor considera essa direção.
                    """
                )