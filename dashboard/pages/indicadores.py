import streamlit as st
import pandas as pd
from components.como_interpretar import como_interpretar, dicionario_indicadores
from data.load_data import carregar_indicadores

PAGE_STYLE = """
<style>
.st-key-ind_page {
    padding: 28px 32px 40px;
    gap: 18px !important;
}
.ind-eyebrow {
    color: var(--cti-blue);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.ind-title {
    color: var(--cti-text);
    font-size: 30px;
    font-weight: 750;
    line-height: 1.15;
    margin: 0 0 7px 0;
}
.ind-subtitle {
    color: var(--cti-muted);
    font-size: 13px;
    margin-bottom: 8px;
}
.ind-section-title {
    color: #173B63;
    font-size: 18px;
    font-weight: 750;
    margin: 12px 0 3px 0;
}
.ind-section-subtitle {
    color: #8293A7;
    font-size: 12px;
    margin-bottom: 14px;
}
.ind-card {
    background: #FFFFFF;
    border: 1px solid #E1ECF7;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(0,75,133,.05);
    min-height: 112px;
}
.ind-kpi-label {
    color: #718096;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .6px;
    margin-bottom: 10px;
}
.ind-kpi-value {
    color: #173B63;
    font-size: 24px;
    font-weight: 750;
}
.ind-kpi-note {
    color: #8293A7;
    font-size: 11px;
    margin-top: 7px;
}
.ind-insight-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr));
    gap: 16px;
    align-items: stretch;
    margin-bottom: 8px;
}
.ind-insight {
    background: #FFFFFF;
    border: 1px solid #E3ECF5;
    border-left: 4px solid #2585C5;
    border-radius: 14px;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    box-shadow: 0 3px 12px rgba(23, 59, 99, 0.05);
    transition: all 0.2s ease;
}
.ind-insight:hover {
    border-color: #B9D2E8;
    border-left-color: #004B85;
    box-shadow: 0 6px 18px rgba(23, 59, 99, 0.10);
    transform: translateY(-2px);
}
.ind-insight--wide {
    grid-column: 1 / -1;
    background: linear-gradient(135deg, #FFFFFF 0%, #F4F8FC 100%);
}
.ind-insight-title {
    color: #173B63;
    font-size: 15px;
    font-weight: 750;
    line-height: 1.3;
}
.ind-insight-text {
    color: #4A5E75;
    font-size: 14px;
    line-height: 1.65;
}
.ind-info {
    background: #F4F8FC;
    border: 1px solid #E1ECF7;
    border-radius: 10px;
    padding: 13px 16px;
    color: #52677D;
    font-size: 12px;
    margin: 8px 0 14px 0;
}
</style>
"""


INDICADORES = {
    "EBITDA": {
        "grupo": "Rentabilidade e resultado",
        "formato": "moeda",
        "descricao": "Resultado antes de juros, impostos, depreciação e amortização."
    },
    "Margem EBITDA": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Representa a parcela da receita convertida em EBITDA."
    },
    "Margem Líquida": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Representa a parcela da receita que se transforma em lucro líquido."
    },
    "NOPAT": {
        "grupo": "Rentabilidade e resultado",
        "formato": "moeda",
        "descricao": "Lucro operacional líquido após impostos."
    },
    "ROIC": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Mede o retorno obtido sobre o capital investido."
    },
    "WACC": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Representa o custo médio ponderado de capital."
    },
    "LC": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez corrente: capacidade de pagamento das obrigações de curto prazo."
    },
    "LS": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez seca: capacidade de pagamento sem considerar os estoques."
    },
    "LI": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez imediata: capacidade de pagamento com recursos disponíveis imediatamente."
    },
    "LG": {
        "grupo": "Liquidez",
        "formato": "numero",
        "descricao": "Liquidez geral: capacidade de pagamento considerando curto e longo prazo."
    },
    "PCT": {
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Participação do capital de terceiros na estrutura de capital."
    },
    "CE": {
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Indica a composição do endividamento."
    },
    "IPL": {
        "grupo": "Endividamento",
        "formato": "percentual",
        "descricao": "Indica o nível de imobilização do patrimônio líquido."
    },
    "Capital Investido": {
        "grupo": "Valor econômico",
        "formato": "moeda",
        "descricao": "Capital aplicado nas operações da empresa."
    },
    "EVA": {
        "grupo": "Valor econômico",
        "formato": "moeda",
        "descricao": "Valor econômico agregado após considerar o custo do capital."
    },
    "MVA Aproximado": {
        "grupo": "Valor econômico",
        "formato": "moeda",
        "descricao": "Estimativa do valor agregado pelo mercado."
    },

    "ROE": {
        "grupo": "Rentabilidade e resultado",
        "formato": "percentual",
        "descricao": "Mede o retorno gerado sobre o patrimônio líquido médio."
    },
    "DuPont - Margem Líquida": {
        "grupo": "Análise DuPont",
        "formato": "percentual",
        "descricao": "Representa a parcela da receita convertida em lucro líquido."
    },
    "DuPont - Giro do Ativo": {
        "grupo": "Análise DuPont",
        "formato": "numero",
        "descricao": "Mede a capacidade dos ativos de gerar receita."
    },
    "DuPont - Alavancagem": {
        "grupo": "Análise DuPont",
        "formato": "numero",
        "descricao": "Relaciona os ativos médios ao patrimônio líquido médio."
    },
    "ROE DuPont": {
        "grupo": "Análise DuPont",
        "formato": "percentual",
        "descricao": "Resultado do ROE calculado pela decomposição DuPont."
    },

    "CCL": {
        "grupo": "Capital de giro e prazos",
        "formato": "moeda",
        "descricao": "Capital circulante líquido: diferença entre ativo e passivo circulantes."
    },
    "PMR": {
        "grupo": "Capital de giro e prazos",
        "formato": "dias",
        "descricao": "Prazo médio de recebimento das vendas."
    },
    "PMP": {
        "grupo": "Capital de giro e prazos",
        "formato": "dias",
        "descricao": "Prazo médio de pagamento aos fornecedores."
    },
    "Ciclo Financeiro": {
        "grupo": "Capital de giro e prazos",
        "formato": "dias",
        "descricao": "Diferença entre o prazo médio de recebimento e o de pagamento."
    },
    "Necessidade de Capital de Giro": {
        "grupo": "Capital de giro e prazos",
        "formato": "moeda",
        "descricao": "Estimativa dos recursos necessários para financiar o ciclo financeiro."
    },

    "Taxa de Conversão da Receita em Caixa": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Relaciona os recebimentos de caixa à receita operacional."
    },
    "FCO": {
        "grupo": "Fluxo de caixa",
        "formato": "moeda",
        "descricao": "Fluxo de caixa operacional."
    },
    "FCO / EBITDA": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa operacional ao EBITDA."
    },
    "FCO / Lucro Líquido": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa operacional ao lucro líquido."
    },
    "FCL": {
        "grupo": "Fluxo de caixa",
        "formato": "moeda",
        "descricao": "Fluxo de caixa livre após os investimentos."
    },
    "Investimentos / Receita": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Representa os investimentos em relação à receita."
    },
    "Investimentos / Depreciação": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona os investimentos à depreciação e amortização do período."
    },
    "Cobertura de Juros": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa operacional às despesas financeiras utilizadas como referência."
    },
    "FCO / Dívida Bruta": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Relaciona o fluxo de caixa operacional à dívida bruta."
    },
    "Distribuição / Lucro Líquido": {
        "grupo": "Fluxo de caixa",
        "formato": "percentual",
        "descricao": "Relaciona a distribuição de caixa aos acionistas ao lucro líquido."
    },
    "Cobertura de Dividendos": {
        "grupo": "Fluxo de caixa",
        "formato": "multiplo",
        "descricao": "Relaciona o fluxo de caixa livre à distribuição de caixa aos acionistas."
    }
}


def _numero(valor, casas=2):
    if pd.isna(valor):
        return "—"

    return (
        f"{valor:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def _moeda(valor):
    if pd.isna(valor):
        return "—"

    absoluto = abs(valor)

    if absoluto >= 1_000_000_000:
        return f"R$ {_numero(valor / 1_000_000_000)} bi"

    if absoluto >= 1_000_000:
        return f"R$ {_numero(valor / 1_000_000)} mi"

    if absoluto >= 1_000:
        return f"R$ {_numero(valor / 1_000)} mil"

    return f"R$ {_numero(valor)}"


def _percentual(valor, serie=None):
    if pd.isna(valor):
        return "—"

    return f"{_numero(valor * 100)}%"


def _formatar_indicador(coluna, valor, serie=None):
    if pd.isna(valor):
        return "—"

    formato = INDICADORES.get(coluna, {}).get("formato")

    if formato == "moeda":
        return _moeda(valor)

    if formato == "percentual":
        return _percentual(valor, serie)

    if formato == "dias":
        return f"{_numero(valor, 1)} dias"

    if formato == "multiplo":
        return f"{_numero(valor)}x"

    return _numero(valor)


def _titulo_secao(titulo, subtitulo=None):
    st.markdown(
        f"""
        <div>
            <div class="ind-section-title">{titulo}</div>
            <div class="ind-section-subtitle">{subtitulo or ""}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _card(coluna, titulo, valor, observacao):
    with coluna:
        st.markdown(
            f"""
            <div class="ind-card">
                <div class="ind-kpi-label">{titulo}</div>
                <div class="ind-kpi-value">{valor}</div>
                <div class="ind-kpi-note">{observacao}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def _html_insight(titulo, texto, largo=False):
    classe = "ind-insight ind-insight--wide" if largo else "ind-insight"
    return (
        f'<div class="{classe}">'
        f'<div class="ind-insight-title">{titulo}</div>'
        f'<div class="ind-insight-text">{texto}</div>'
        f'</div>'
    )


def _grade_insights(esquerda=(), direita=(), abaixo=()):
    from itertools import zip_longest

    cards = []

    # intercala esquerda/direita para manter a ordem de leitura
    for e, d in zip_longest(esquerda, direita):
        for item in (e, d):
            if item:
                cards.append(_html_insight(*item))

    # os cards de comparação ocupam a linha inteira
    for titulo, texto in abaixo:
        cards.append(_html_insight(titulo, texto, largo=True))

    st.markdown(
        f'<div class="ind-insight-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True
    )


def _numero_ano(valor):
    resultado = pd.Series([str(valor)]).str.extract(
        r"(\d+)",
        expand=False
    ).iloc[0]

    return int(resultado) if pd.notna(resultado) else 0


def _mapear_cenarios(df):
    cenarios_originais = sorted(
        df["Cenario"].dropna().unique(),
        key=lambda x: (
            _numero_ano(x),
            str(x)
        )
    )

    mapa = {
        cenario: f"Cenário {i + 1}"
        for i, cenario in enumerate(cenarios_originais)
    }

    return mapa

def _gerar_insights(df_ano, df_anterior=None, cenario_selecionado=None):
    if df_ano.empty:
        st.info("Não há dados disponíveis para gerar insights.")
        return

    l = leituras_desempenho(df_ano, df_anterior, cenario_selecionado)
    _grade_insights(l["esquerda"], l["direita"], l["abaixo"])

def leituras_desempenho(df_ano, df_anterior=None, cenario_selecionado=None):
    """Leituras automáticas de desempenho (usadas pela tela e pelo relatório em PDF).

    Devolve {"esquerda", "direita", "abaixo"}: listas de (título, texto).
    """
    esquerda, direita, abaixo = [], [], []

    if cenario_selecionado == "Todos":
        contexto = "considerando todos os cenários"
    else:
        contexto = f"para {cenario_selecionado}"

    ebitda = (
        pd.to_numeric(df_ano["EBITDA"], errors="coerce").mean()
        if "EBITDA" in df_ano.columns else None
    )

    margem = (
        pd.to_numeric(df_ano["Margem EBITDA"], errors="coerce").mean()
        if "Margem EBITDA" in df_ano.columns else None
    )

    margem_liquida = (
        pd.to_numeric(df_ano["Margem Líquida"], errors="coerce").mean()
        if "Margem Líquida" in df_ano.columns else None
    )

    roic = (
        pd.to_numeric(df_ano["ROIC"], errors="coerce").mean()
        if "ROIC" in df_ano.columns else None
    )

    wacc = (
        pd.to_numeric(df_ano["WACC"], errors="coerce").mean()
        if "WACC" in df_ano.columns else None
    )

    lc = (
        pd.to_numeric(df_ano["LC"], errors="coerce").mean()
        if "LC" in df_ano.columns else None
    )


    if ebitda is not None and pd.notna(ebitda):
        esquerda.append((
            "Resultado operacional",
            f"A média do EBITDA foi de {_moeda(ebitda)} {contexto}."
        ))

    if margem is not None and pd.notna(margem):
        esquerda.append((
            "Margem EBITDA",
            f"A margem EBITDA média foi de "
            f"{_percentual(margem, df_ano['Margem EBITDA'])}, "
            "indicando a participação do resultado operacional "
            "em relação à receita."
        ))

    if margem_liquida is not None and pd.notna(margem_liquida):
        direita.append((
            "Margem líquida",
            f"A margem líquida média foi de "
            f"{_percentual(margem_liquida, df_ano['Margem Líquida'])}."
        ))

    if lc is not None and pd.notna(lc):
        if lc > 1:
            interpretacao = (
                "a média está acima de 1, indicando maior cobertura "
                "das obrigações de curto prazo pelos ativos circulantes."
            )
        elif lc < 1:
            interpretacao = (
                "a média está abaixo de 1, indicando que os ativos "
                "circulantes são inferiores às obrigações de curto prazo."
            )
        else:
            interpretacao = (
                "a média está em 1, indicando equilíbrio entre "
                "ativos e obrigações de curto prazo."
            )

        direita.append((
            "Liquidez corrente",
            f"A liquidez corrente média foi de {_numero(lc)}; {interpretacao}"
        ))


    if "ROIC" in df_ano.columns and "WACC" in df_ano.columns:
        comparacao = df_ano[["ROIC", "WACC"]].apply(
            pd.to_numeric,
            errors="coerce"
        ).dropna()

        if not comparacao.empty:
            acima = (comparacao["ROIC"] > comparacao["WACC"]).sum()
            total = len(comparacao)
            proporcao = (acima / total) * 100

            if roic > wacc:
                leitura = (
                    "Na média, o retorno sobre o capital investido "
                    "superou o custo de capital."
                )
            elif roic < wacc:
                leitura = (
                    "Na média, o retorno sobre o capital investido "
                    "ficou abaixo do custo de capital."
                )
            else:
                leitura = (
                    "Na média, o retorno sobre o capital investido "
                    "ficou igual ao custo de capital."
                )

            abaixo.append((
                "Retorno sobre o capital x custo de capital",
                f"{leitura} Em {proporcao:.1f}% dos registros com dados "
                "disponíveis, o ROIC ficou acima do WACC."
            ))


    if df_anterior is not None and not df_anterior.empty:

        if "EBITDA" in df_ano.columns and "EBITDA" in df_anterior.columns:
            atual = pd.to_numeric(
                df_ano["EBITDA"], errors="coerce"
            ).mean()

            anterior = pd.to_numeric(
                df_anterior["EBITDA"], errors="coerce"
            ).mean()

            if pd.notna(atual) and pd.notna(anterior) and anterior != 0:
                variacao = ((atual - anterior) / abs(anterior)) * 100

                if variacao > 0:
                    texto = (
                        f"O EBITDA médio aumentou {_numero(variacao)}% "
                        "em relação ao ano anterior."
                    )
                elif variacao < 0:
                    texto = (
                        f"O EBITDA médio diminuiu {_numero(abs(variacao))}% "
                        "em relação ao ano anterior."
                    )
                else:
                    texto = (
                        "O EBITDA médio permaneceu estável em relação "
                        "ao ano anterior."
                    )

                abaixo.append(("Evolução do EBITDA", texto))

        if (
            "Margem EBITDA" in df_ano.columns
            and "Margem EBITDA" in df_anterior.columns
        ):
            atual = pd.to_numeric(
                df_ano["Margem EBITDA"], errors="coerce"
            ).mean()

            anterior = pd.to_numeric(
                df_anterior["Margem EBITDA"], errors="coerce"
            ).mean()

            if pd.notna(atual) and pd.notna(anterior):
                diferenca = atual - anterior

                abaixo.append((
                    "Variação da margem EBITDA",
                    f"A diferença entre a margem EBITDA média do ano selecionado "
                    f"e a do ano anterior foi de {_numero(diferenca)} "
                    "ponto(s) na escala original dos dados."
                ))


    if (
        cenario_selecionado == "Todos"
        and "Cenario" in df_ano.columns
        and "EBITDA" in df_ano.columns
    ):
        ranking = (
            df_ano.groupby("Cenario")["EBITDA"]
            .mean()
            .dropna()
            .sort_values(ascending=False)
        )

        if not ranking.empty:
            melhor = ranking.index[0]
            pior = ranking.index[-1]
            mapa = _mapear_cenarios(df_ano)

            abaixo.append((
                "Destaque entre os cenários",
                f"{mapa.get(melhor, melhor)} apresentou o maior EBITDA médio "
                f"({_moeda(ranking.iloc[0])}). "
                f"{mapa.get(pior, pior)} apresentou o menor "
                f"({_moeda(ranking.iloc[-1])})."
            ))

    return {"esquerda": esquerda, "direita": direita, "abaixo": abaixo}


def _valor_central(df, coluna):
    if coluna not in df.columns:
        return None

    valores = pd.to_numeric(df[coluna], errors="coerce").dropna()

    return float(valores.median()) if not valores.empty else None

def _gerar_insights_novos(df_ano, cenario_selecionado):
    esquerda, direita = leituras_estrutura(df_ano, cenario_selecionado)

    if not esquerda and not direita:
        st.info(
            "Os novos indicadores não têm valores para este recorte. "
            "Os que usam variação ou média de dois anos começam no Ano 2."
        )
        return

    _grade_insights(esquerda, direita)


def leituras_estrutura(df_ano, cenario_selecionado):
    """Leituras de retorno, capital de giro e caixa (tela e relatório em PDF).

    Devolve (esquerda, direita): listas de (título, texto).
    """
    if cenario_selecionado == "Todos":
        referencia = "mediana dos cenários"
    else:
        referencia = "valor do cenário"

    roe = _valor_central(df_ano, "ROE")
    roic = _valor_central(df_ano, "ROIC")
    margem = _valor_central(df_ano, "DuPont - Margem Líquida")
    giro = _valor_central(df_ano, "DuPont - Giro do Ativo")
    alavancagem = _valor_central(df_ano, "DuPont - Alavancagem")
    pmr = _valor_central(df_ano, "PMR")
    pmp = _valor_central(df_ano, "PMP")
    ciclo = _valor_central(df_ano, "Ciclo Financeiro")
    ccl = _valor_central(df_ano, "CCL")
    fco = _valor_central(df_ano, "FCO")
    fco_ebitda = _valor_central(df_ano, "FCO / EBITDA")
    fcl = _valor_central(df_ano, "FCL")
    cobertura_juros = _valor_central(df_ano, "Cobertura de Juros")
    cobertura_dividendos = _valor_central(df_ano, "Cobertura de Dividendos")

    esquerda = []
    direita = []

    if roe is not None:
        texto = f"O ROE ({referencia}) foi de {_percentual(roe)}."

        if roic is not None:
            if roe > roic:
                texto += (
                    f" Ficou acima do ROIC ({_percentual(roic)}): o retorno "
                    "ao acionista superou o retorno do capital investido."
                )
            else:
                texto += (
                    f" Ficou abaixo do ROIC ({_percentual(roic)}): o retorno "
                    "ao acionista não superou o do capital investido."
                )

        esquerda.append(("Retorno sobre o patrimônio líquido", texto))

    if None not in (margem, giro, alavancagem):
        esquerda.append((
            "Decomposição do ROE (DuPont)",
            f"O retorno é formado por margem líquida de {_percentual(margem)}, "
            f"giro do ativo de {_numero(giro)}x e alavancagem de "
            f"{_numero(alavancagem)}x. A margem mostra a eficiência, o giro "
            "mostra o uso dos ativos e a alavancagem mostra o peso do capital "
            "de terceiros."
        ))

    if fco_ebitda is not None:
        texto = (
            f"O fluxo de caixa operacional equivale a "
            f"{_percentual(fco_ebitda)} do EBITDA"
        )

        if fco is not None:
            texto += f" (FCO de {_moeda(fco)})"

        if fco_ebitda >= 1:
            texto += ". Todo o resultado operacional virou caixa no período."
        else:
            texto += ". Parte do resultado operacional não virou caixa no período."

        esquerda.append(("Conversão do EBITDA em caixa", texto))

    if cobertura_juros is not None:
        if cobertura_juros >= 1:
            leitura = "O caixa operacional cobre as despesas financeiras."
        else:
            leitura = "O caixa operacional não cobre as despesas financeiras."

        esquerda.append((
            "Cobertura de juros",
            f"O FCO cobre {_numero(cobertura_juros)}x as despesas "
            f"financeiras. {leitura}"
        ))

    if ciclo is not None:
        texto = f"O ciclo financeiro foi de {_numero(ciclo, 1)} dias"

        if pmr is not None and pmp is not None:
            texto += (
                f" (recebimento em {_numero(pmr, 1)} dias e pagamento em "
                f"{_numero(pmp, 1)} dias)"
            )

        if ciclo > 0:
            texto += (
                ". A empresa espera mais para receber do que leva para pagar "
                "e precisa financiar essa diferença."
            )
        else:
            texto += (
                ". A empresa paga depois de receber: os fornecedores ajudam a "
                "financiar a operação."
            )

        direita.append(("Capital de giro e prazos", texto))

    if ccl is not None:
        if ccl >= 0:
            leitura = "Os ativos circulantes superam os passivos circulantes."
        else:
            leitura = "Os passivos circulantes superam os ativos circulantes."

        direita.append((
            "Capital circulante líquido",
            f"O CCL foi de {_moeda(ccl)}. {leitura}"
        ))

    if fcl is not None:
        if fcl >= 0:
            leitura = "Depois dos investimentos, sobrou caixa."
        else:
            leitura = "Os investimentos superaram o caixa operacional."

        direita.append((
            "Fluxo de caixa livre",
            f"O FCL foi de {_moeda(fcl)}. {leitura}"
        ))

    if cobertura_dividendos is not None:
        if cobertura_dividendos >= 1:
            leitura = "O caixa livre cobre a distribuição aos acionistas."
        else:
            leitura = "O caixa livre não cobre a distribuição aos acionistas."

        direita.append((
            "Cobertura de dividendos",
            f"O FCL cobre {_numero(cobertura_dividendos)}x a distribuição "
            f"de caixa. {leitura}"
        ))

    return esquerda, direita


def _tabela_indicadores(df, mapa_cenarios):
    _titulo_secao(
        "Explore os indicadores",
        "Escolha quais informações deseja consultar. "
        "A tabela será atualizada conforme sua seleção."
    )

    indicadores_disponiveis = [
        indicador
        for indicador in INDICADORES
        if indicador in df.columns
    ]

    grupos = {}

    for indicador in indicadores_disponiveis:
        grupo = INDICADORES[indicador]["grupo"]
        grupos.setdefault(grupo, []).append(indicador)

    opcoes = []

    for grupo, indicadores in grupos.items():
        opcoes.extend(indicadores)

    padrao = [
        "EBITDA",
        "Margem EBITDA",
        "Margem Líquida",
        "ROIC",
        "WACC"
    ]

    padrao = [
        item for item in padrao
        if item in indicadores_disponiveis
    ]

    selecionados = st.multiselect(
        "Indicadores que deseja visualizar",
        options=opcoes,
        default=padrao,
        key="ind_selecao_indicadores",
        help="Você pode selecionar um ou vários indicadores."
    )

    if not selecionados:
        st.info("Selecione pelo menos um indicador para montar a tabela.")
        return

    tabela = df.copy()
    tabela["Cenário"] = tabela["Cenario"].map(mapa_cenarios)
    tabela["Ano"] = tabela["Ano"].astype(str)

    colunas = ["Cenário", "Ano"] + selecionados
    tabela = tabela[colunas].copy()

    tabela = tabela.sort_values(["Cenário", "Ano"])

    rotulos = {
        "PCT": "Participação de Capital de Terceiros",
        "CE": "Composição do Endividamento",
        "IPL": "Imobilização do Patrimônio Líquido",
        "LC": "Liquidez Corrente",
        "LS": "Liquidez Seca",
        "LI": "Liquidez Imediata",
        "LG": "Liquidez Geral",
    }

    nomes = {}

    for indicador in selecionados:
        base = rotulos.get(indicador, indicador)
        formato = INDICADORES[indicador]["formato"]

        if formato == "moeda":
            nomes[indicador] = f"{base} (R$ mi)"
            tabela[indicador] = tabela[indicador] / 1_000_000
        elif formato == "percentual":
            nomes[indicador] = f"{base} (%)"
            tabela[indicador] = tabela[indicador] * 100
        elif formato == "dias":
            nomes[indicador] = f"{base} (dias)"
        else:
            nomes[indicador] = base

    tabela = tabela.rename(columns=nomes)

    configuracao = {
        "Cenário": st.column_config.TextColumn(
            "Cenário",
            width="medium"
        ),
        "Ano": st.column_config.TextColumn(
            "Ano",
            width="small"
        )
    }

    for indicador in selecionados:
        nome = nomes[indicador]
        formato = INDICADORES[indicador]["formato"]

        if formato == "multiplo":
            formato_numero = "%.2fx"
        elif formato == "dias":
            formato_numero = "%.1f"
        else:
            formato_numero = "%.2f"

        configuracao[nome] = st.column_config.NumberColumn(
            nome,
            format=formato_numero,
            help=INDICADORES[indicador]["descricao"]
        )

    col1, col2 = st.columns([1, 4])

    with col1:
        st.metric(
            "Registros",
            f"{len(tabela):,}".replace(",", ".")
        )

    with col2:
        st.caption(
            f"{len(selecionados)} indicador(es) selecionado(s)."
        )

    st.dataframe(
        tabela,
        column_config=configuracao,
        use_container_width=True,
        hide_index=True,
        height=480
    )

    st.caption(
        "Os valores são apresentados conforme os dados disponíveis "
        "na base de indicadores. Campos sem informação permanecem vazios."
    )


def preparar_indicadores(df):
    """Garante o ano numérico e os indicadores como números."""
    df = df.copy()

    if "Ano_Numero" not in df.columns:
        df["Ano_Numero"] = (
            df["Ano"]
            .astype(str)
            .str.extract(r"(\d+)", expand=False)
            .astype(int)
        )

    for coluna in INDICADORES:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce"
            )

    return df


def cartoes_resumo(df_ano):
    """Os 8 cartões do resumo do ano: (título, valor formatado, observação)."""
    def media(coluna):
        if coluna not in df_ano.columns:
            return None

        valores = df_ano[coluna].dropna()

        return valores.mean() if not valores.empty else None

    ebitda = media("EBITDA")
    margem_ebitda = media("Margem EBITDA")
    margem_liquida = media("Margem Líquida")
    roic = media("ROIC")
    roe = media("ROE")
    fcl = media("FCL")
    conversao = media("FCO / EBITDA")
    ciclo = media("Ciclo Financeiro")

    return [
        ("EBITDA médio",
         _moeda(ebitda) if ebitda is not None else "—",
         "Resultado operacional"),
        ("Margem EBITDA",
         _percentual(margem_ebitda, df_ano["Margem EBITDA"])
         if margem_ebitda is not None else "—",
         "Rentabilidade operacional"),
        ("Margem líquida",
         _percentual(margem_liquida, df_ano["Margem Líquida"])
         if margem_liquida is not None else "—",
         "Rentabilidade líquida"),
        ("ROIC médio",
         _percentual(roic, df_ano["ROIC"]) if roic is not None else "—",
         "Retorno sobre o capital investido"),
        ("ROE médio",
         _percentual(roe) if roe is not None else "—",
         "Retorno sobre o patrimônio líquido"),
        ("FCL médio",
         _moeda(fcl) if fcl is not None else "—",
         "Caixa livre após investimentos"),
        ("Conversão de caixa",
         _percentual(conversao) if conversao is not None else "—",
         "FCO em relação ao EBITDA"),
        ("Ciclo financeiro",
         f"{_numero(ciclo, 1)} dias" if ciclo is not None else "—",
         "Prazo de recebimento menos prazo de pagamento"),
    ]


def recorte_indicadores(df, ano, cenario):
    """Linhas do ano (rótulo "Ano N") e do cenário, e as do ano anterior."""
    df_ano = df[df["Ano"] == ano].copy()
    if cenario != "Todos":
        df_ano = df_ano[df_ano["Cenario"] == cenario]

    df_anterior = df[df["Ano_Numero"] == _numero_ano(ano) - 1].copy()
    if cenario != "Todos":
        df_anterior = df_anterior[df_anterior["Cenario"] == cenario]

    return df_ano, df_anterior


def render_indicadores():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="ind_page"):


        try:
            df = carregar_indicadores()

        except Exception as erro:
            st.error(f"Não foi possível carregar os indicadores: {erro}")
            return

        if df is None or df.empty:
            st.warning("A base de indicadores está vazia.")
            return

        df = preparar_indicadores(df)

        mapa_cenarios = _mapear_cenarios(df)

        anos_disponiveis = (
            df[["Ano", "Ano_Numero"]]
            .drop_duplicates()
            .sort_values("Ano_Numero")["Ano"]
            .tolist()
        )

        cenarios_originais = list(mapa_cenarios.keys())


        col_titulo, col_ano, col_cenario = st.columns(
            [2.6, 1, 1.2],
            vertical_alignment="bottom"
        )

        with col_titulo:
            st.markdown(
                """
                <div>
                    <div class="ind-eyebrow">PAINEL FINANCEIRO</div>
                    <div class="ind-title">Indicadores Financeiros</div>
                    <div class="ind-subtitle">
                        Explore os resultados, identifique tendências
                        e analise o desempenho dos cenários.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_ano:
            ano_selecionado = st.selectbox(
                "Ano de análise",
                options=anos_disponiveis,
                index=len(anos_disponiveis) - 1,
                key="ind_filtro_ano"
            )

        with col_cenario:
            cenario_selecionado = st.selectbox(
                "Cenário",
                options=["Todos"] + cenarios_originais,
                format_func=lambda x: (
                    x if x == "Todos"
                    else mapa_cenarios.get(x, x)
                ),
                key="ind_filtro_cenario"
            )

        st.write("")


        df_ano, df_anterior = recorte_indicadores(df, ano_selecionado, cenario_selecionado)

        if df_ano.empty:
            st.warning("Não existem dados para essa seleção.")
            return


        _titulo_secao(
            f"Resumo de {ano_selecionado}",
            "Indicadores médios do recorte selecionado."
        )

        cartoes = cartoes_resumo(df_ano)
        for linha in (cartoes[:4], cartoes[4:]):
            for coluna, (titulo, valor, observacao) in zip(st.columns(4), linha):
                _card(coluna, titulo, valor, observacao)

        st.write("")


        _titulo_secao(
            "Indicadores de Desempenho",
            "Leituras automáticas dos indicadores do ano selecionado."
        )

        _gerar_insights(
            df_ano,
            df_anterior,
            cenario_selecionado
        )

        st.write("")

        _titulo_secao(
            "Indicadores de Estrutura e Retorno",
            "Leituras de retorno, capital de giro e caixa do ano selecionado."
        )

        _gerar_insights_novos(
            df_ano,
            cenario_selecionado
        )

        st.write("")


        _tabela_indicadores(
            df_ano,
            mapa_cenarios
        )

        st.write("")

        dicionario_indicadores("ind")

        como_interpretar(
            "ind",
            [
                "**Resumo do ano:** média dos valores do recorte escolhido. Em "
                "\"Todos\", é a média dos cenários; em um cenário, é o valor dele.",
                "**Insights:** leituras automáticas. As dos novos indicadores usam "
                "a mediana, para que cenários extremos não distorçam o resultado.",
                "**ROE e DuPont:** o ROE é o lucro líquido sobre o patrimônio "
                "líquido médio. A decomposição mostra se o retorno vem da margem, "
                "do giro dos ativos ou da alavancagem.",
                "**Capital de giro:** o ciclo financeiro é o prazo de recebimento "
                "menos o prazo de pagamento. Quanto maior, mais caixa fica preso "
                "na operação.",
                "**Caixa:** o FCO estima o caixa gerado pela operação e o FCL "
                "desconta os investimentos. Coberturas abaixo de 1x indicam que "
                "o caixa não cobre a obrigação.",
                "**N/D ou vazio:** indicadores que usam o ano anterior (ROE, "
                "FCO, FCL e coberturas) não existem no Ano 1.",
            ],
            "os indicadores de caixa são estimados a partir do balanço e da DRE, "
            "não de um fluxo de caixa contábil completo.",
        )